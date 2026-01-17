from langchain_openai import ChatOpenAI # 注意这里改用 ChatOpenAI
from langchain_openai import AzureChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv(override=True)

# DeepSeek 官方 API 配置
# 模型选项: 'deepseek-chat' (对应 V3) 或 'deepseek-reasoner' (对应 R1)
langchain_deepseek_api = ChatOpenAI(
    base_url="https://api.deepseek.com", 
    api_key=os.getenv("DEEPSEEK_API_KEY"),  # 需去 DeepSeek 官网申请 Key
    model="deepseek-chat",
    temperature=0, # DeepSeek 建议 V3 设为 1.3 左右，通用场景 1.0 也可以
)


# Qwen
langchain_qwen_api = ChatOpenAI(
    # 阿里云百炼兼容 OpenAI 的 Base URL
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    # 你的阿里云 DashScope API Key (通常以 sk- 开头)
    api_key=os.getenv("QWEN_API_KEY"),
    # 模型选择:
    # - qwen-max: 能力最强，对标 GPT-4
    # - qwen-plus: 性价比最高，速度快，能力强 (推荐作为主力)
    # - qwen-turbo: 速度极快，便宜
    model="qwen-plus",
    temperature=0.0,
)


langchain_gpt4omini_api = AzureChatOpenAI(
  azure_endpoint="https://yeqifeng-eastus2-2026.openai.azure.com/",
  openai_api_version="2024-12-01-preview",
  azure_deployment="gpt-4o-mini",
  openai_api_key=os.getenv("GPT4OMINI_API_KEY"),
)

langchain_o3mini_api = AzureChatOpenAI(
  azure_endpoint="https://yeqifeng-eastus2-2026.openai.azure.com/",
  openai_api_version="2024-12-01-preview",
  azure_deployment="o3-mini",
  openai_api_key=os.getenv("O3MINI_API_KEY"),
)

langchain_llms_api_alts = [
  AzureChatOpenAI(
    azure_endpoint="https://yeqifeng-eastus2-new.openai.azure.com/",
    openai_api_version="2024-12-01-preview",
    azure_deployment="gpt-4o-mini",
    openai_api_key=os.getenv("O4MINI_API_KEY2"),
  ),
  AzureChatOpenAI(
    azure_endpoint="https://yeqifeng-italynorth.openai.azure.com/",
    openai_api_version="2024-12-01-preview",
    azure_deployment="gpt-4o-mini",
    openai_api_key=os.getenv("O4MINI_API_KEY3"),
  ),
  AzureChatOpenAI(
    azure_endpoint="https://yeqifeng-japaneast.openai.azure.com/",
    openai_api_version="2024-12-01-preview",
    azure_deployment="gpt-4o-mini",
    openai_api_key=os.getenv("O4MINI_API_KEY4"),
  ),
  AzureChatOpenAI(
    azure_endpoint="https://yeqifeng-germanywestcentral.openai.azure.com/",
    openai_api_version="2024-12-01-preview",
    azure_deployment="gpt-4o-mini",
    openai_api_key=os.getenv("O4MINI_API_KEY5"),
  ),
  
]

class LLMInterfaceManager:
  def __init__(self):
    self.registry = {
        "gpt-4o-mini": langchain_gpt4omini_api,
        "o3-mini": langchain_o3mini_api,
        "deepseek-chat": langchain_deepseek_api,
        "qwen-plus": langchain_qwen_api,
    }
  
  def get_api(self, name):
    if name not in self.registry:
        return self.registry.get("gpt-4o-mini")
    return self.registry[name]

llm_manager = LLMInterfaceManager()

