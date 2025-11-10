"""
配置管理模块：从 .env 文件加载配置
"""
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# 加载 .env 文件
env_path = Path(__file__).parent.parent / "config" / "settings.env"
if env_path.exists():
    load_dotenv(env_path)
else:
    # 如果 settings.env 不存在，尝试加载示例文件
    example_path = Path(__file__).parent.parent / "config" / "settings.env.example"
    if example_path.exists():
        print("警告: 未找到 settings.env，请复制 settings.env.example 并配置")
    load_dotenv(example_path)


class Config:
    """应用配置类"""

    # API Keys
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    DEEPSEEK_API_KEY: Optional[str] = os.getenv("DEEPSEEK_API_KEY")
    AUTHORPIC_API_KEY: Optional[str] = os.getenv("AUTHORPIC_API_KEY")

    # LLM Provider
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai").lower()

    # 文件路径
    INPUT_JSON_PATH: str = os.getenv("INPUT_JSON_PATH", "inputs/bank_statement.json")
    RULES_XLSX_PATH: str = os.getenv("RULES_XLSX_PATH", "inputs/audit_rules.xlsx")
    OUTPUT_REPORT_PATH: str = os.getenv("OUTPUT_REPORT_PATH", "outputs/audit_report.json")
    OUTPUT_MARKDOWN_PATH: str = os.getenv("OUTPUT_MARKDOWN_PATH", "outputs/audit_report.md")
    OUTPUT_EXCEL_PATH: str = os.getenv("OUTPUT_EXCEL_PATH", "outputs/audit_report.xlsx")

    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/app.log")

    # LLM 配置
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    AUTHORPIC_MODEL: str = os.getenv("AUTHORPIC_MODEL", "authorpic-model")
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "60"))
    FAST_FAILOVER: bool = os.getenv("FAST_FAILOVER", "true").lower() == "true"
    FAILOVER_COOLDOWN_SECONDS: int = int(os.getenv("FAILOVER_COOLDOWN_SECONDS", "900"))

    # 性能优化配置
    PARALLEL_PROCESSING: bool = os.getenv("PARALLEL_PROCESSING", "true").lower() == "true"
    MAX_WORKERS: int = int(os.getenv("MAX_WORKERS", "4"))

    @classmethod
    def get_api_key(cls) -> Optional[str]:
        """根据当前 LLM_PROVIDER 返回对应的 API Key"""
        return cls.get_api_key_for_provider(cls.LLM_PROVIDER)

    @classmethod
    def get_api_key_for_provider(cls, provider: str) -> Optional[str]:
        """根据指定的 provider 返回对应的 API Key"""
        key_map = {
            "openai": cls.OPENAI_API_KEY,
            "deepseek": cls.DEEPSEEK_API_KEY,
            "authorpic": cls.AUTHORPIC_API_KEY,
        }
        return key_map.get(provider.lower())

    @classmethod
    def get_model_name(cls) -> str:
        """根据当前 LLM_PROVIDER 返回对应的模型名称"""
        return cls.get_model_name_for_provider(cls.LLM_PROVIDER)

    @classmethod
    def get_model_name_for_provider(cls, provider: str) -> str:
        """根据指定的 provider 返回对应的模型名称"""
        model_map = {
            "openai": cls.OPENAI_MODEL,
            "deepseek": cls.DEEPSEEK_MODEL,
            "authorpic": cls.AUTHORPIC_MODEL,
        }
        return model_map.get(provider.lower(), cls.OPENAI_MODEL)

    @classmethod
    def validate(cls) -> bool:
        """验证配置是否完整"""
        api_key = cls.get_api_key()
        if (
            not api_key
            or api_key.startswith("sk-xxxxxx")
            or api_key.startswith("ds-xxxxxx")
            or api_key.startswith("ap-xxxxxx")
        ):
            print(f"错误: 请配置 {cls.LLM_PROVIDER.upper()}_API_KEY")
            return False
        return True

