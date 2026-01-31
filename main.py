"""
BBVA 银行流水审计系统 - 主入口
"""
import sys
import os
import logging
import glob
from pathlib import Path
from src.config import Config
from src.audit_engine import AuditEngine
from src.report_generator import ReportGenerator

# 确保控制台能够正确输出 UTF-8（尤其是 Windows 控制台中文）
def configure_console_encoding():
    if os.name != "nt":
        return
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    stdout_reconfig = getattr(sys.stdout, "reconfigure", None)
    stderr_reconfig = getattr(sys.stderr, "reconfigure", None)
    try:
        if callable(stdout_reconfig):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if callable(stderr_reconfig):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        if not callable(stdout_reconfig) or not callable(stderr_reconfig):
            import codecs  # noqa: WPS433
            if not callable(stdout_reconfig) and hasattr(sys.stdout, "buffer"):
                sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, errors="replace")
            if not callable(stderr_reconfig) and hasattr(sys.stderr, "buffer"):
                sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, errors="replace")
    except Exception:
        # 若编码设置失败，不影响主流程
        pass


# 配置日志
def setup_logging():
    """配置日志系统"""
    log_file = Path(Config.LOG_FILE)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def detect_json_files(input_path):
    """
    检测输入路径中的 JSON 文件，支持多文档检测
    
    Args:
        input_path: 输入路径，可能包含通配符
        
    Returns:
        JSON 文件路径列表，按字母顺序排序
    """
    if '*' in str(input_path):
        json_files = glob.glob(str(input_path))
        # 按字母顺序排序，确保 part1, part2, part3 的顺序
        json_files.sort()
        return json_files
    else:
        # 单个文件路径
        return [str(input_path)]


def process_single_document(json_file_path, rules_path, logger):
    """
    处理单个 JSON 文件的审计流程
    
    Args:
        json_file_path: JSON 文件路径
        rules_path: 规则文件路径
        logger: 日志记录器
        
    Returns:
        是否成功处理
    """
    try:
        logger.info(f"开始处理文档: {json_file_path}")
        
        # 初始化审计引擎
        engine = AuditEngine(
            json_path=json_file_path,
            excel_path=rules_path
        )
        
        # 加载数据
        logger.info("正在加载数据...")
        if not engine.load_data():
            logger.error(f"文档 {json_file_path} 数据加载失败")
            return False
        
        # 执行审计（使用并行处理）
        logger.info("开始执行审计...")
        results = engine.execute_audit(
            parallel=Config.PARALLEL_PROCESSING,
            max_workers=Config.MAX_WORKERS
        )
        
        if not results:
            logger.error(f"文档 {json_file_path} 审计执行失败，未生成任何结果")
            return False
        
        # 获取摘要
        summary = engine.get_summary()
        logger.info(f"审计完成: 共处理 {summary['total_rules']} 条规则")
        logger.info(f"命中: {summary['hit_count']}, 未命中: {summary['not_hit_count']}, 无法判断: {summary['unknown_count']}")
        
        # 从输入 JSON 文件路径提取文件名前缀
        input_json_path = Path(json_file_path)
        
        # 获取文件名（不含扩展名）
        input_filename = input_json_path.stem
        # 去掉 _structured 后缀（如果存在）
        if input_filename.endswith('_structured'):
            input_filename = input_filename[:-11]  # 去掉 '_structured'
        
        # 构建输出文件路径
        output_dir = Path(Config.OUTPUT_REPORT_PATH).parent
        output_json_path = output_dir / f"{input_filename}_audit_report.json"
        output_markdown_path = output_dir / f"{input_filename}_audit_report.md"
        output_excel_path = output_dir / f"{input_filename}_audit_report.xlsx"
        
        # 生成报告
        logger.info("正在生成报告...")
        report_generator = ReportGenerator(
            output_json_path=str(output_json_path),
            output_markdown_path=str(output_markdown_path),
            output_excel_path=str(output_excel_path)
        )
        
        # 添加元数据
        metadata = {
            "account_number": engine.bank_statement.get('metadata', {}).get('account_number', 'N/A'),
            "total_pages": engine.bank_statement.get('metadata', {}).get('total_pages', 'N/A'),
            "llm_provider": Config.LLM_PROVIDER,
            "llm_model": Config.get_model_name()
        }
        
        json_path, markdown_path, excel_path = report_generator.generate_all_reports(
            results=results,
            summary=summary,
            metadata=metadata
        )
        
        logger.info("=" * 60)
        logger.info(f"文档 {input_filename} 审计报告生成完成！")
        logger.info(f"JSON 报告: {json_path}")
        logger.info(f"Markdown 报告: {markdown_path}")
        logger.info(f"Excel 报告: {excel_path}")
        logger.info("=" * 60)
        
        return True
        
    except FileNotFoundError as e:
        logger.error(f"文件未找到: {e}")
        return False
    except Exception as e:
        logger.error(f"处理文档 {json_file_path} 时发生错误: {e}", exc_info=True)
        return False


def main():
    """主函数"""
    configure_console_encoding()
    # 设置日志
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("BBVA 银行流水审计系统启动")
    logger.info("=" * 60)
    
    # 验证配置
    if not Config.validate():
        logger.error("配置验证失败，请检查 .env 文件")
        sys.exit(1)
    
    try:
        # 检测 JSON 文件
        json_files = detect_json_files(Config.INPUT_JSON_PATH)
        
        if not json_files:
            logger.error(f"未找到匹配的 JSON 文件: {Config.INPUT_JSON_PATH}")
            sys.exit(1)
        
        logger.info(f"检测到 {len(json_files)} 个 JSON 文件待处理")
        for idx, json_file in enumerate(json_files, 1):
            logger.info(f"  [{idx}] {json_file}")
        
        # 处理每个 JSON 文件
        success_count = 0
        failed_count = 0
        
        for idx, json_file in enumerate(json_files, 1):
            logger.info("")
            logger.info("*" * 60)
            logger.info(f"处理进度: [{idx}/{len(json_files)}]")
            logger.info("*" * 60)
            
            if process_single_document(json_file, Config.RULES_XLSX_PATH, logger):
                success_count += 1
            else:
                failed_count += 1
        
        # 输出最终统计
        logger.info("")
        logger.info("=" * 60)
        logger.info("所有文档处理完成！")
        logger.info(f"成功: {success_count} 个文档")
        logger.info(f"失败: {failed_count} 个文档")
        logger.info("=" * 60)
        
        # 如果有失败的文档，返回非零退出码
        if failed_count > 0:
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"执行过程中发生错误: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

