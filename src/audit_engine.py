"""
审计引擎模块：控制整体审计流程
"""
import logging
import sys
import time
import threading
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.data_loader import DataLoader
from src.rule_parser import RuleParser
from src.llm_judge import LLMJudge

logger = logging.getLogger(__name__)


class AuditEngine:
    """审计引擎"""
    
    def __init__(self, json_path: str, excel_path: str):
        """
        初始化审计引擎
        
        Args:
            json_path: JSON 文件路径
            excel_path: Excel 文件路径
        """
        self.data_loader = DataLoader(json_path, excel_path)
        self.rule_parser = RuleParser()
        self.llm_judge = LLMJudge()
        
        self.bank_statement = None
        self.bank_statement_text = None
        self.rules = None
        self.results = []
        self._progress_lock = threading.Lock()
        self._total_rules = 0
        self._completed_rules = 0
    
    def load_data(self) -> bool:
        """
        加载所有数据
        
        Returns:
            是否成功加载
        """
        try:
            # 加载银行流水
            self.bank_statement = self.data_loader.load_bank_statement()
            
            # 验证数据结构
            if not self.data_loader.validate_bank_statement(self.bank_statement):
                return False
            
            # 提取文本内容
            self.bank_statement_text = self.data_loader.get_all_text_content(self.bank_statement)
            
            # 加载审计规则
            raw_rules = self.data_loader.load_audit_rules()
            self.rules = self.rule_parser.parse_all_rules(raw_rules)
            
            logger.info(f"数据加载完成: {len(self.rules)} 条规则")
            return True
        
        except Exception as e:
            logger.error(f"加载数据失败: {e}")
            return False
    
    def _process_single_rule(self, rule: Dict[str, Any], idx: int, total: int) -> Dict[str, Any]:
        """
        处理单条规则（用于并行处理）
        
        Args:
            rule: 规则字典
            idx: 规则索引（从1开始）
            total: 总规则数
            
        Returns:
            审计结果字典
        """
        start_time = time.time()
        logger.info(f"[{idx}/{total}] 开始处理规则: {rule['rule_id']} - {rule['rule_name']}")
        
        try:
            # 根据规则提取相关数据（优化：减少 prompt 大小）
            relevant_text = self.data_loader.get_relevant_text_content(self.bank_statement, rule)
            
            # 构建提示词
            prompt = self.rule_parser.build_llm_prompt(rule, relevant_text)
            
            # 调用 LLM 进行判断
            judgment = self.llm_judge.judge(prompt)
            
            # 构建结果
            result = {
                "rule_id": rule['rule_id'],
                "rule_name": rule['rule_name'],
                "hit": judgment.get('hit'),
                "evidence": judgment.get('evidence', ''),
                "confidence": judgment.get('confidence', 'low'),
                "notes": judgment.get('notes', '')
            }
            
            elapsed_time = time.time() - start_time
            logger.info(f"[{idx}/{total}] [完成] 规则 {rule['rule_id']} 处理完成: hit={result['hit']}, confidence={result['confidence']}, 耗时 {elapsed_time:.1f}秒")
            
            return result
        
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"[{idx}/{total}] [错误] 处理规则 {rule['rule_id']} 时发生错误: {e}, 耗时 {elapsed_time:.1f}秒")
            # 即使出错，也返回结果
            return {
                "rule_id": rule['rule_id'],
                "rule_name": rule['rule_name'],
                "hit": None,
                "evidence": f"处理错误: {str(e)}",
                "confidence": "low",
                "notes": "执行过程中发生异常"
            }
    
    def execute_audit(self, parallel: bool = True, max_workers: int = 4) -> List[Dict[str, Any]]:
        """
        执行审计，处理所有规则
        
        Args:
            parallel: 是否并行处理（默认 True）
            max_workers: 最大并行工作线程数（默认 4）
        
        Returns:
            审计结果列表
        """
        if not self.rules:
            logger.error("未加载规则，无法执行审计")
            return []
        
        if not self.bank_statement:
            logger.error("未加载银行流水，无法执行审计")
            return []
        
        total_rules = len(self.rules)
        logger.info(f"开始执行审计，共 {total_rules} 条规则")
        logger.info(f"处理模式: {'并行处理' if parallel else '串行处理'}")
        if parallel:
            logger.info(f"最大并行数: {max_workers}")
        
        overall_start_time = time.time()
        self.results = []
        self._init_progress(total_rules)
        
        if parallel and total_rules > 1:
            # 并行处理
            with ThreadPoolExecutor(max_workers=min(max_workers, total_rules)) as executor:
                # 提交所有任务
                future_to_rule = {
                    executor.submit(self._process_single_rule, rule, idx + 1, total_rules): rule
                    for idx, rule in enumerate(self.rules)
                }
                
                # 收集结果（按提交顺序）
                results_dict = {}
                completed_count = 0
                
                for future in as_completed(future_to_rule):
                    completed_count += 1
                    rule = future_to_rule[future]
                    try:
                        result = future.result()
                        results_dict[rule['rule_id']] = result
                        logger.info(f"进度: {completed_count}/{total_rules} 条规则已完成")
                        self._advance_progress()
                    except Exception as e:
                        logger.error(f"获取规则 {rule['rule_id']} 的结果时发生错误: {e}")
                        results_dict[rule['rule_id']] = {
                            "rule_id": rule['rule_id'],
                            "rule_name": rule['rule_name'],
                            "hit": None,
                            "evidence": f"获取结果错误: {str(e)}",
                            "confidence": "low",
                            "notes": "并行处理时发生异常"
                        }
                        self._advance_progress()
                
                # 按原始顺序排列结果
                for rule in self.rules:
                    if rule['rule_id'] in results_dict:
                        self.results.append(results_dict[rule['rule_id']])
        else:
            # 串行处理（兼容模式）
            for idx, rule in enumerate(self.rules, 1):
                result = self._process_single_rule(rule, idx, total_rules)
                self.results.append(result)
                self._advance_progress()
        
        overall_elapsed_time = time.time() - overall_start_time
        logger.info(f"审计完成，共处理 {len(self.results)} 条规则，总耗时 {overall_elapsed_time:.1f}秒")
        
        # 验证所有规则都已处理
        if len(self.results) != len(self.rules):
            logger.warning(f"规则处理数量不匹配: 期望 {len(self.rules)}，实际 {len(self.results)}")
        
        return self.results
    
    def _init_progress(self, total: int) -> None:
        """初始化进度条"""
        with self._progress_lock:
            self._total_rules = max(total, 0)
            self._completed_rules = 0
            if self._total_rules > 0:
                self._render_progress()
    
    def _advance_progress(self) -> None:
        """更新进度条"""
        with self._progress_lock:
            if self._total_rules == 0:
                return
            self._completed_rules = min(self._completed_rules + 1, self._total_rules)
            self._render_progress()
            if self._completed_rules == self._total_rules:
                sys.stdout.write("\n")
                sys.stdout.flush()
    
    def _render_progress(self) -> None:
        """渲染进度条"""
        if self._total_rules <= 0:
            return
        ratio = self._completed_rules / self._total_rules if self._total_rules else 0
        bar_width = 24
        filled = int(bar_width * ratio)
        bar = "#" * filled + "-" * (bar_width - filled)
        sys.stdout.write(f"\r进度: [{bar}] {self._completed_rules}/{self._total_rules}")
        sys.stdout.flush()
    
    def get_summary(self) -> Dict[str, Any]:
        """
        获取审计摘要统计
        
        Returns:
            摘要统计字典
        """
        if not self.results:
            return {
                "total_rules": 0,
                "hit_count": 0,
                "not_hit_count": 0,
                "unknown_count": 0,
                "high_confidence_count": 0,
                "medium_confidence_count": 0,
                "low_confidence_count": 0
            }
        
        summary = {
            "total_rules": len(self.results),
            "hit_count": sum(1 for r in self.results if r['hit'] is True),
            "not_hit_count": sum(1 for r in self.results if r['hit'] is False),
            "unknown_count": sum(1 for r in self.results if r['hit'] is None),
            "high_confidence_count": sum(1 for r in self.results if r['confidence'] == 'high'),
            "medium_confidence_count": sum(1 for r in self.results if r['confidence'] == 'medium'),
            "low_confidence_count": sum(1 for r in self.results if r['confidence'] == 'low')
        }
        
        return summary



