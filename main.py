"""
BBVA 银行流水审计系统 - 主入口
"""
import sys
import logging
from pathlib import Path
from src.config import Config
from src.audit_engine import AuditEngine
from src.report_generator import ReportGenerator

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


def main():
    """主函数"""
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
        # 初始化审计引擎
        logger.info(f"加载银行流水: {Config.INPUT_JSON_PATH}")
        logger.info(f"加载审计规则: {Config.RULES_XLSX_PATH}")
        
        engine = AuditEngine(
            json_path=Config.INPUT_JSON_PATH,
            excel_path=Config.RULES_XLSX_PATH
        )
        
        # 加载数据
        logger.info("正在加载数据...")
        if not engine.load_data():
            logger.error("数据加载失败")
            sys.exit(1)
        
        # 执行审计（使用并行处理）
        logger.info("开始执行审计...")
        results = engine.execute_audit(
            parallel=Config.PARALLEL_PROCESSING,
            max_workers=Config.MAX_WORKERS
        )
        
        if not results:
            logger.error("审计执行失败，未生成任何结果")
            sys.exit(1)
        
        # 获取摘要
        summary = engine.get_summary()
        logger.info(f"审计完成: 共处理 {summary['total_rules']} 条规则")
        logger.info(f"命中: {summary['hit_count']}, 未命中: {summary['not_hit_count']}, 无法判断: {summary['unknown_count']}")
        
        # 生成报告
        logger.info("正在生成报告...")
        report_generator = ReportGenerator(
            output_json_path=Config.OUTPUT_REPORT_PATH,
            output_markdown_path=Config.OUTPUT_MARKDOWN_PATH,
            output_excel_path=Config.OUTPUT_EXCEL_PATH
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
        logger.info("审计报告生成完成！")
        logger.info(f"JSON 报告: {json_path}")
        logger.info(f"Markdown 报告: {markdown_path}")
        logger.info(f"Excel 报告: {excel_path}")
        logger.info("=" * 60)
        
    except FileNotFoundError as e:
        logger.error(f"文件未找到: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"执行过程中发生错误: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

