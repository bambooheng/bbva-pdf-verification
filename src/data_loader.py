"""
数据加载模块：加载 JSON 银行流水和 Excel 审计规则
"""
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)


class DataLoader:
    """数据加载器"""
    
    DETALLE_HEADER_KEY = "detalle de movimientos realizados"
    DATE_PATTERN = re.compile(r"^\d{2}/[A-Z]{3}$", re.IGNORECASE)
    AMOUNT_PATTERN = re.compile(r"^-?\d{1,3}(?:,\d{3})*(?:\.\d{2})?$")
    DETALLE_STRICT_RULE_IDS = {
        "MSTAR_RULE_BBVA_001",
        "MSTAR_RULE_BBVA_002",
        "MSTAR_RULE_BBVA_003",
        "MSTAR_RULE_BBVA_004",
    }
    DETALLE_ROW_START_MAX_X = 40.0
    DETALLE_LIQ_X_RANGE = (55.0, 130.0)
    DETALLE_COLUMN_PADDING = 2.0
    DETALLE_STOP_KEYWORDS = [
        "TOTAL MOVIMIENTOS",
        "TOTAL IMPORTE",
        "CUADRO RESUMEN",
        "RESUMEN"
    ]
    DETALLE_PAGE_HEADER_KEYWORDS = [
        "NO. DE CUENTA",
        "NO. DE CLIENTE",
        "ESTADO DE CUENTA",
        "PAGINA",
        "BBVA MEXICO",
        "TARJETA BASICA",
        "AV. PASEO"
    ]
    
    def __init__(self, json_path: str, excel_path: str):
        """
        初始化数据加载器
        
        Args:
            json_path: JSON 文件路径
            excel_path: Excel 文件路径
        """
        self.json_path = Path(json_path)
        self.excel_path = Path(excel_path)
    
    def load_bank_statement(self) -> Dict[str, Any]:
        """
        加载银行流水 JSON 数据
        
        Returns:
            银行流水数据的字典
            
        Raises:
            FileNotFoundError: 文件不存在
            json.JSONDecodeError: JSON 格式错误
        """
        json_path = self._resolve_json_path()
        if not json_path.exists():
            raise FileNotFoundError(f"银行流水文件不存在: {json_path}")
        
        logger.info(f"正在加载银行流水: {json_path}")
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"成功加载银行流水，账户号: {data.get('metadata', {}).get('account_number', 'N/A')}")
            return data
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析错误: {e}")
            raise
        except Exception as e:
            logger.error(f"加载银行流水时发生错误: {e}")
            raise
    
    def load_audit_rules(self) -> List[Dict[str, Any]]:
        """
        加载审计规则 Excel 文件
        
        Returns:
            规则列表，每个规则是一个字典
            
        Raises:
            FileNotFoundError: 文件不存在
            ValueError: Excel 格式错误或缺少必要列
        """
        if not self.excel_path.exists():
            raise FileNotFoundError(f"审计规则文件不存在: {self.excel_path}")
        
        logger.info(f"正在加载审计规则: {self.excel_path}")
        
        try:
            # 读取 Excel 文件
            df = pd.read_excel(self.excel_path, engine='openpyxl')
            
            # 列名映射：支持中英文列名
            column_mapping = {
                'rule_id': ['Rule ID', '规则ID'],
                'rule_name': ['Rule Name', '规则名称', '审核要点'],
                'condition_logic': ['Condition Logic', '判断逻辑', '涉及银行流水字段指标'],
                'validation_rule': ['校验规则', 'Validation Rule'],
                'decision_result': ['决策结果', 'Decision Result']
            }
            
            # 查找实际列名
            actual_columns = {}
            for key, possible_names in column_mapping.items():
                found = False
                for name in possible_names:
                    if name in df.columns:
                        actual_columns[key] = name
                        found = True
                        break
                if not found:
                    raise ValueError(f"Excel 文件缺少必要列: {key} (期望列名之一: {possible_names})")
            
            # 转换为字典列表
            rules = []
            for idx, row in df.iterrows():
                rule = {
                    'rule_id': str(row[actual_columns['rule_id']]).strip() if pd.notna(row[actual_columns['rule_id']]) else None,
                    'rule_name': str(row[actual_columns['rule_name']]).strip() if pd.notna(row[actual_columns['rule_name']]) else None,
                    'condition_logic': str(row[actual_columns['condition_logic']]).strip() if pd.notna(row[actual_columns['condition_logic']]) else None,
                    'validation_rule': str(row[actual_columns['validation_rule']]).strip() if pd.notna(row[actual_columns['validation_rule']]) else None,
                    'decision_result': str(row[actual_columns['decision_result']]).strip() if pd.notna(row[actual_columns['decision_result']]) else None,
                    'row_index': idx + 2  # Excel 行号（从2开始，因为第1行是表头）
                }
                
                # 跳过无效规则
                if not rule['rule_id'] or not rule['rule_name']:
                    logger.warning(f"第 {rule['row_index']} 行规则无效，已跳过")
                    continue
                
                rules.append(rule)
            
            logger.info(f"成功加载 {len(rules)} 条审计规则")
            return rules
        
        except pd.errors.EmptyDataError:
            logger.error("Excel 文件为空")
            raise ValueError("Excel 文件为空")
        except Exception as e:
            logger.error(f"加载审计规则时发生错误: {e}")
            raise
    
    def validate_bank_statement(self, data: Dict[str, Any]) -> bool:
        """
        验证银行流水数据结构
        
        Args:
            data: 银行流水数据
            
        Returns:
            是否有效
        """
        required_keys = ['metadata', 'pages']
        if not all(key in data for key in required_keys):
            logger.error(f"银行流水数据结构不完整，缺少: {set(required_keys) - set(data.keys())}")
            return False
        
        logger.info("银行流水数据结构验证通过")
        return True
    
    def get_relevant_text_content(self, data: Dict[str, Any], rule: Dict[str, Any] = None) -> str:
        """
        根据规则提取相关的文本内容（优化：只提取与规则相关的数据）
        
        Args:
            data: 银行流水数据
            rule: 审计规则（可选，如果提供则只提取相关数据）
            
        Returns:
            相关的文本内容字符串
        """
        if rule is None:
            # 如果没有提供规则，返回全部内容
            return self.get_all_text_content(data)
        
        text_parts = []
        
        # 提取 metadata
        metadata = data.get('metadata', {})
        text_parts.append(f"账户号: {metadata.get('account_number', 'N/A')}")
        text_parts.append(f"总页数: {metadata.get('total_pages', 'N/A')}")
        text_parts.append("")
        
        # 根据规则类型提取相关数据
        rule_id = (rule.get('rule_id') or '').strip().upper()
        rule_name = rule.get('rule_name', '').lower()
        condition_logic = rule.get('condition_logic', '').lower()
        
        # 判断需要提取哪些部分
        need_comportamiento = 'comportamiento' in condition_logic or 'depósitos' in condition_logic or 'abonos' in condition_logic or 'retiros' in condition_logic or 'cargos' in condition_logic
        need_detalle = 'detalle' in condition_logic or 'movimientos' in condition_logic or 'abonos' in condition_logic or 'cargos' in condition_logic
        enforce_detalle_only = rule_id in self.DETALLE_STRICT_RULE_IDS
        
        # 如果需要 Detalle 数据，先提取结构化的交易明细，确保为后续规则提供原始顺序的明细列表
        if need_detalle:
            detalle_transactions = self.extract_detalle_transactions(data)
            if detalle_transactions:
                formatted_detalle = self.format_detalle_transactions(detalle_transactions)
                if formatted_detalle:
                    text_parts.append("=== Detalle de Movimientos Realizados（结构化明细，已按原始顺序列出） ===")
                    text_parts.append(formatted_detalle)
                    text_parts.append("")
                
                if enforce_detalle_only:
                    subset_sections = self._build_detalle_subsets(rule_id, detalle_transactions)
                    if subset_sections:
                        text_parts.extend(subset_sections)
        
        # 提取 pages 中的文本
        pages = data.get('pages', [])
        for page in pages:
            page_num = page.get('page_number', 'N/A')
            layout_elements = page.get('layout_elements', [])
            
            # ⚠️ 关键：按照 bbox 的 y 坐标排序，确保按照原始文档的行顺序（从上到下）
            # 这样可以保持原始文档中交易的出现顺序
            def get_y_position(element):
                bbox = element.get('bbox', {})
                if isinstance(bbox, dict):
                    return bbox.get('y', 0)
                return 0
            
            # 按照 y 坐标从上到下排序（y 值越小，位置越靠上）
            sorted_elements = sorted(layout_elements, key=get_y_position)
            
            page_texts = []
            for element in sorted_elements:
                raw_text = element.get('raw_text', '')
                if not raw_text or not raw_text.strip():
                    continue
                
                raw_text_lower = raw_text.lower()
                
                # 根据规则需求过滤内容
                include_text = False
                if need_comportamiento and ('comportamiento' in raw_text_lower or 'depósitos' in raw_text_lower or 'abonos' in raw_text_lower or 'retiros' in raw_text_lower or 'cargos' in raw_text_lower):
                    include_text = True
                if need_detalle and ('detalle' in raw_text_lower or 'movimientos' in raw_text_lower or 'fecha' in raw_text_lower or 'saldo' in raw_text_lower or 'oper' in raw_text_lower):
                    include_text = True
                if not need_comportamiento and not need_detalle:
                    # 如果没有特定需求，包含所有内容
                    include_text = True
                
                if include_text:
                    cleaned_text = raw_text.strip()
                    if enforce_detalle_only:
                        upper_text = cleaned_text.upper()
                        if 'TOTAL MOVIMIENTOS' in upper_text or 'TOTAL IMPORTE' in upper_text:
                            continue
                    page_texts.append(cleaned_text)
            
            if page_texts and not enforce_detalle_only:
                text_parts.append(f"=== 页面 {page_num} ===")
                text_parts.append("\n".join(page_texts))
                text_parts.append("")
        
        # 提取验证指标
        validation = data.get('validation_metrics', {})
        if validation:
            text_parts.append("=== 验证指标 ===")
            text_parts.append(f"提取完整性: {validation.get('extraction_completeness', 'N/A')}%")
            text_parts.append(f"内容准确性: {validation.get('content_accuracy', 'N/A')}%")
        
        return "\n".join(text_parts)
    
    def _resolve_json_path(self) -> Path:
        """
        根据配置路径解析实际使用的 JSON 文件。
        支持以下几种配置形式：
        - 指定具体文件（若存在则直接使用）
        - 指定目录（自动选取该目录中最新的 .json 文件）
        - 使用通配符（如 inputs/*.json，自动选取匹配到的最新文件）
        - 指定的具体文件不存在时，会在同目录中自动选取最新的 .json 文件
        """
        path_str = str(self.json_path)
        has_wildcard = any(ch in path_str for ch in ["*", "?", "["])
        
        # 处理通配符
        if has_wildcard:
            pattern_path = Path(path_str)
            base_dir = pattern_path.parent if pattern_path.parent.as_posix() not in ("", ".") else Path(".")
            matches = sorted(
                base_dir.glob(pattern_path.name),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            if matches:
                selected = matches[0]
                logger.info(f"使用通配符匹配到最新的 JSON 文件: {selected}")
                self.json_path = selected
                return selected
            logger.error(f"通配符 {path_str} 未匹配到任何 JSON 文件")
            return self.json_path
        
        # 若路径存在且为文件，直接使用
        if self.json_path.exists() and self.json_path.is_file():
            return self.json_path
        
        # 若路径是目录，则在目录中查找最新文件
        if self.json_path.exists() and self.json_path.is_dir():
            candidate_dir = self.json_path
        else:
            candidate_dir = self.json_path.parent
        
        if not candidate_dir.exists():
            logger.error(f"银行流水目录不存在: {candidate_dir}")
            return self.json_path
        
        json_files = sorted(
            candidate_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        if not json_files:
            logger.error(f"未在目录 {candidate_dir} 中找到任何 JSON 文件")
            return self.json_path
        
        latest = json_files[0]
        if not self.json_path.exists() or not self.json_path.is_file():
            logger.warning(
                "配置的银行流水文件不可用，自动切换到最新的 JSON 文件: %s",
                latest.name
            )
        else:
            logger.info(f"使用目录中最新的 JSON 文件: {latest.name}")
        self.json_path = latest
        return latest

    def extract_detalle_transactions(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        提取“Detalle de Movimientos Realizados”中的交易明细，保持原始顺序
        
        Args:
            data: 银行流水数据
        
        Returns:
            交易明细列表
        """
        transactions: List[Dict[str, Any]] = []
        pages = data.get('pages', [])
        
        detalle_active = False
        column_ranges: Dict[str, tuple] = {}
        
        for page in pages:
            layout_elements = page.get('layout_elements', [])
            has_header, header_y, detected_ranges = self._find_detalle_header(layout_elements)
            
            if has_header:
                detalle_active = True
                column_ranges = detected_ranges or column_ranges
            elif not detalle_active:
                continue
            else:
                header_y = -float("inf")
                if not column_ranges:
                    column_ranges = self._compute_detalle_column_ranges(layout_elements)
            
            if not detalle_active:
                continue
            
            line_entries: List[Dict[str, Any]] = []
            stop_y: Optional[float] = None
            stop_detected = False
            
            for element in layout_elements:
                bbox = element.get('bbox')
                if not isinstance(bbox, dict):
                    continue
                
                y_top = bbox.get('y')
                if y_top is None:
                    continue
                
                if header_y is not None and y_top <= header_y:
                    continue
                
                lines = element.get('lines') or []
                for line in lines:
                    text = (line.get('text') or "").strip()
                    if not text:
                        continue
                    
                    normalized = text.upper()
                    if any(keyword in normalized for keyword in self.DETALLE_PAGE_HEADER_KEYWORDS):
                        continue
                    
                    if any(keyword in normalized for keyword in self.DETALLE_STOP_KEYWORDS):
                        stop_y = line['bbox'][1]
                        stop_detected = True
                        continue
                    
                    ly = line['bbox'][1]
                    if stop_y is not None and ly >= stop_y:
                        continue
                    
                    x0, _, x1, _ = line['bbox']
                    center_x = (x0 + x1) / 2 if x1 is not None else x0
                    line_entries.append({
                        "page": page.get('page_number'),
                        "y": ly,
                        "x": x0,
                        "x_center": center_x,
                        "text": text
                    })
            
            line_entries.sort(key=lambda entry: (entry['y'], entry['x']))
            
            current_txn: Optional[Dict[str, Any]] = None
            orphan_lines: List[str] = []
            
            for entry in line_entries:
                text = entry['text']
                x = entry['x']
                
                x_center = entry.get("x_center")
                
                if self._is_detalle_row_start(text, x):
                    if orphan_lines and transactions:
                        transactions[-1].setdefault("extras", []).extend(orphan_lines)
                        orphan_lines = []
                    if current_txn:
                        transactions.append(current_txn)
                    current_txn = {
                        "page": entry['page'],
                        "oper": text,
                        "liq": None,
                        "description": None,
                        "cargo": None,
                        "abono": None,
                        "operacion": None,
                        "saldo": None,
                        "referencias": [],
                        "extras": [],
                        "y": entry['y']
                    }
                    continue
                
                if current_txn is None:
                    if any(keyword in text.upper() for keyword in self.DETALLE_PAGE_HEADER_KEYWORDS):
                        continue
                    orphan_lines.append(text)
                    continue
                
                if self._is_detalle_liq_date(text, x) and current_txn.get("liq") is None:
                    current_txn["liq"] = text
                elif self._is_amount(text):
                    column = self._categorize_numeric_column(x, column_ranges, x_center)
                    if column == "cargo":
                        current_txn["cargo"] = text
                    elif column == "abono":
                        current_txn["abono"] = text
                    elif column == "operacion":
                        current_txn["operacion"] = text
                    elif column == "liquidacion":
                        current_txn["saldo"] = text
                    else:
                        current_txn.setdefault("extras", []).append(f"[未分类金额] {text}")
                elif text.lower().startswith("referencia"):
                    current_txn["referencias"].append(text)
                elif current_txn.get("description") is None:
                    current_txn["description"] = text
                else:
                    current_txn.setdefault("extras", []).append(text)
            
            if current_txn:
                transactions.append(current_txn)
            elif orphan_lines and transactions:
                transactions[-1].setdefault("extras", []).extend(orphan_lines)
            
            if stop_detected:
                detalle_active = False
                column_ranges = {}
        
        transactions.sort(key=lambda txn: (txn.get("page", 0) or 0, txn.get("y", 0) or 0))
        return transactions
    
    def format_detalle_transactions(self, transactions: List[Dict[str, Any]]) -> str:
        """
        格式化 Detalle 交易明细，生成适合放入提示词的文本
        """
        if not transactions:
            return ""
        
        lines: List[str] = [f"总笔数: {len(transactions)}"]
        
        for idx, txn in enumerate(transactions, 1):
            base = f"{idx}. 页面:{txn.get('page', 'N/A')} | Oper:{txn.get('oper', 'N/A')}"
            if txn.get("liq"):
                base += f" | Liq:{txn['liq']}"
            if txn.get("description"):
                base += f" | 描述:{txn['description']}"
            cargo = txn.get("cargo") or "无"
            abono = txn.get("abono") or "无"
            operacion = txn.get("operacion") or "无"
            saldo = txn.get("saldo") or "无"
            base += f" | Cargo:{cargo} | Abono:{abono} | Operacion:{operacion} | Saldo:{saldo}"
            referencias = [ref.strip() for ref in txn.get("referencias", []) if ref.strip()]
            if referencias:
                base += f" | Referencia:{'; '.join(referencias)}"
            lines.append(base)
            
        return "\n".join(lines)

    @staticmethod
    def _has_effective_amount(value: Optional[str]) -> bool:
        if not value:
            return False
        cleaned = value.replace(",", "").replace(" ", "")
        if cleaned in {"", "0", "0.0", "0.00"}:
            return False
        try:
            numeric = float(cleaned)
        except ValueError:
            return True
        return abs(numeric) > 0

    def _build_detalle_subsets(self, rule_id: str, transactions: List[Dict[str, Any]]) -> List[str]:
        sections: List[str] = []
        upper_rule = rule_id.upper()
        needs_abono = "ABONO" in upper_rule
        needs_cargo = "CARGO" in upper_rule

        if needs_abono:
            abono_entries = [
                txn for txn in transactions
                if self._has_effective_amount(txn.get("abono"))
            ]
            sections.append("=== Detalle 专用视图：ABONOS 列非空交易（已按原始顺序） ===")
            if abono_entries:
                sections.append(self._format_subset_transactions(abono_entries, focus_column="abono"))
            else:
                sections.append("无 ABONOS 列非空的交易记录")
            sections.append("")

        if needs_cargo:
            cargo_entries = [
                txn for txn in transactions
                if self._has_effective_amount(txn.get("cargo"))
            ]
            sections.append("=== Detalle 专用视图：CARGOS 列非空交易（已按原始顺序） ===")
            if cargo_entries:
                sections.append(self._format_subset_transactions(cargo_entries, focus_column="cargo"))
            else:
                sections.append("无 CARGOS 列非空的交易记录")
            sections.append("")

        return sections

    def _format_subset_transactions(self, transactions: List[Dict[str, Any]], focus_column: str) -> str:
        total_label = "总笔数"
        lines = [f"{total_label}: {len(transactions)}"]
        for idx, txn in enumerate(transactions, 1):
            # 保持原始顺序，突出重点列
            oper = txn.get("oper") or "N/A"
            description = txn.get("description") or "无描述"
            amount = txn.get(focus_column) or "无"
            page = txn.get("page", "N/A")
            base = f"{idx}. 页面:{page} | Oper:{oper} | 描述:{description} | {focus_column.upper()}:{amount}"
            saldo = txn.get("saldo")
            if saldo:
                base += f" | Saldo:{saldo}"
            referencias = [ref.strip() for ref in txn.get("referencias", []) if ref.strip()]
            if referencias:
                base += f" | Referencia:{'; '.join(referencias)}"
            lines.append(base)
        return "\n".join(lines)
    
    def _is_detalle_row_start(self, text: str, x: float) -> bool:
        """
        判断是否是交易明细的起始行（操作日期）
        """
        if not text or x is None:
            return False
        return x <= self.DETALLE_ROW_START_MAX_X and bool(self.DATE_PATTERN.match(text))
    
    def _is_detalle_liq_date(self, text: str, x: float) -> bool:
        """
        判断是否是清算日期列
        """
        if not text or x is None:
            return False
        min_x, max_x = self.DETALLE_LIQ_X_RANGE
        return min_x <= x <= max_x and bool(self.DATE_PATTERN.match(text))
    
    def _is_amount(self, text: str) -> bool:
        """
        判断字符串是否为金额格式
        """
        if not text:
            return False
        return bool(self.AMOUNT_PATTERN.match(text.replace(" ", "")))
    
    def _find_detalle_header(self, layout_elements: List[Dict[str, Any]]) -> tuple:
        """
        检测当前页面是否包含 Detalle 表头，返回 (has_header, header_y, column_ranges)
        """
        header_y = None
        column_ranges: Dict[str, tuple] = {}
        has_header = False
        
        for element in layout_elements:
            raw_text = element.get('raw_text') or ""
            if isinstance(raw_text, str) and self.DETALLE_HEADER_KEY in raw_text.lower():
                bbox = element.get('bbox')
                if isinstance(bbox, dict):
                    header_y = bbox.get('y')
                has_header = True
                break
        
        if has_header:
            # 使用表头所在页面的列信息
            column_ranges = self._compute_detalle_column_ranges(layout_elements)
            # 查找 FECHA 等列标题行，精确定位数据起始的 y 坐标
            header_line_y = None
            for element in layout_elements:
                for line in element.get('lines') or []:
                    text = (line.get('text') or "").strip().upper()
                    if text in {"FECHA", "OPER"}:
                        header_line_y = line['bbox'][1]
                        break
                if header_line_y is not None:
                    break
            if header_line_y is not None:
                header_y = header_line_y
        
        return has_header, header_y, column_ranges
    
    def _compute_detalle_column_ranges(self, layout_elements: List[Dict[str, Any]]) -> Dict[str, tuple]:
        """
        基于表头自动推断 CARGO / ABONO / OPERACION / LIQUIDACION 列的横向范围
        """
        header_range = None
        liquidacion_range = None
        
        for element in layout_elements:
            for line in element.get('lines') or []:
                text = (line.get('text') or "").strip().upper()
                bbox = line.get('bbox')
                if not bbox:
                    continue
                x0, _, x1, _ = bbox
                if text == "CARGOS ABONOS OPERACION":
                    header_range = (x0, x1)
                elif text == "LIQUIDACION":
                    liquidacion_range = (x0, x1)
        
        column_ranges: Dict[str, tuple] = {}
        
        if header_range:
            start_x, end_x = header_range
            total_width = max(end_x - start_x, 1.0)
            words = [("cargo", len("CARGOS")), ("abono", len("ABONOS")), ("operacion", len("OPERACION"))]
            total_len = sum(length for _, length in words) or len(words)
            cursor = start_x
            
            for idx, (name, length) in enumerate(words):
                width = total_width * (length / total_len)
                seg_start = cursor
                cursor += width
                seg_end = cursor if idx < len(words) - 1 else end_x
                column_ranges[name] = (
                    seg_start - self.DETALLE_COLUMN_PADDING,
                    seg_end + self.DETALLE_COLUMN_PADDING
                )
        else:
            column_ranges["cargo"] = (-float("inf"), 430.0)
            column_ranges["abono"] = (430.0, 520.0)
            column_ranges["operacion"] = (520.0, 540.0)
        
        if liquidacion_range:
            column_ranges["liquidacion"] = (
                liquidacion_range[0] - self.DETALLE_COLUMN_PADDING,
                liquidacion_range[1] + self.DETALLE_COLUMN_PADDING
            )
        else:
            column_ranges.setdefault("liquidacion", (520.0, float("inf")))
        
        return column_ranges
    
    def _categorize_numeric_column(self, x: float, column_ranges: Dict[str, tuple], x_center: Optional[float] = None) -> Optional[str]:
        """
        根据横坐标判断金额属于哪个列
        """
        if x_center is not None:
            x_value = x_center
        else:
            x_value = x
        if x_value is None:
            return None
        
        matches = []
        for name, (start, end) in column_ranges.items():
            if start <= x_value <= end:
                matches.append(name)
        
        if matches:
            if len(matches) == 1:
                return matches[0]
            nearest_column = None
            min_distance = float("inf")
            for name in matches:
                start, end = column_ranges[name]
                center = (start + end) / 2
                distance = abs(x_value - center)
                if distance < min_distance:
                    min_distance = distance
                    nearest_column = name
            if nearest_column:
                return nearest_column
        
        nearest_column = None
        min_distance = float("inf")
        for name, (start, end) in column_ranges.items():
            center = (start + end) / 2
            distance = abs(x_value - center)
            if distance < min_distance:
                min_distance = distance
                nearest_column = name
        return nearest_column
    
    def get_all_text_content(self, data: Dict[str, Any]) -> str:
        """
        提取银行流水中的所有文本内容（用于 LLM 分析）
        
        Args:
            data: 银行流水数据
            
        Returns:
            所有文本内容的字符串
        """
        text_parts = []
        
        # 提取 metadata
        metadata = data.get('metadata', {})
        text_parts.append(f"账户号: {metadata.get('account_number', 'N/A')}")
        text_parts.append(f"总页数: {metadata.get('total_pages', 'N/A')}")
        text_parts.append("")
        
        # 提取 pages 中的文本，按页面组织
        pages = data.get('pages', [])
        for page in pages:
            page_num = page.get('page_number', 'N/A')
            layout_elements = page.get('layout_elements', [])
            
            # ⚠️ 关键：按照 bbox 的 y 坐标排序，确保按照原始文档的行顺序（从上到下）
            # 这样可以保持原始文档中交易的出现顺序
            def get_y_position(element):
                bbox = element.get('bbox', {})
                if isinstance(bbox, dict):
                    return bbox.get('y', 0)
                return 0
            
            # 按照 y 坐标从上到下排序（y 值越小，位置越靠上）
            sorted_elements = sorted(layout_elements, key=get_y_position)
            
            page_texts = []
            for element in sorted_elements:
                raw_text = element.get('raw_text')
                if raw_text and raw_text.strip():
                    page_texts.append(raw_text.strip())
            
            if page_texts:
                text_parts.append(f"=== 页面 {page_num} ===")
                text_parts.append("\n".join(page_texts))
                text_parts.append("")
        
        # 提取验证指标
        validation = data.get('validation_metrics', {})
        if validation:
            text_parts.append("=== 验证指标 ===")
            text_parts.append(f"提取完整性: {validation.get('extraction_completeness', 'N/A')}%")
            text_parts.append(f"内容准确性: {validation.get('content_accuracy', 'N/A')}%")
        
        return "\n".join(text_parts)

