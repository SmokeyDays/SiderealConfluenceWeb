from langchain_openai import ChatOpenAI # 注意这里改用 ChatOpenAI
from langchain_openai import AzureChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAI
import os
from dotenv import load_dotenv

from server.utils.config import get_config

class LLMInterfaceManager:
  def __init__(self):

    load_dotenv(override=True)

    # 火山 DS API
    langchain_deepseek_v32_api = ChatOpenAI(
        base_url="https://ark.cn-beijing.volces.com/api/v3", 
        api_key=os.getenv("HUOSHAN_API_KEY"),  # 需去 DeepSeek 官网申请 Key
        model="deepseek-v3-2-251201",
        temperature=0,
    )

    langchain_doubao_2_lite_api = ChatOpenAI(
        base_url="https://ark.cn-beijing.volces.com/api/v3", 
        api_key=os.getenv("HUOSHAN_API_KEY"),  # 需去 DeepSeek 官网申请 Key
        model="doubao-seed-2-0-lite-260428",
        temperature=0,
    )

    langchain_doubao_2_pro_api = ChatOpenAI(
        base_url="https://ark.cn-beijing.volces.com/api/v3", 
        api_key=os.getenv("HUOSHAN_API_KEY"),  # 需去 DeepSeek 官网申请 Key
        model="doubao-seed-2-0-pro-260215",
        temperature=0,
    )

    langchain_glm47_api = ChatOpenAI(
        base_url="https://ark.cn-beijing.volces.com/api/v3", 
        api_key=os.getenv("HUOSHAN_API_KEY"),  # 需去商汤官网申请 Key
        model="glm-4-7-251222",
        temperature=0,
    )

    langchain_deepseek_4_pro_api = ChatOpenAI(
        base_url="https://api.deepseek.com",
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        model="deepseek-v4-pro",
        temperature=0,
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

    # Azure OpenAI 配置
    langchain_gpt4omini_api = AzureChatOpenAI(
      azure_endpoint=os.getenv("GPT4OMINI_ENDPOINT"),
      openai_api_version="2024-12-01-preview",
      azure_deployment="gpt-4o-mini",
      openai_api_key=os.getenv("GPT4OMINI_API_KEY"),
    )

    langchain_o3mini_api = AzureChatOpenAI(
      azure_endpoint=os.getenv("O3MINI_ENDPOINT"),
      openai_api_version="2024-12-01-preview",
      azure_deployment="o3-mini",
      openai_api_key=os.getenv("O3MINI_API_KEY"),
    )

    langchain_gpt5_api = AzureChatOpenAI(
      azure_endpoint=os.getenv("O3MINI_ENDPOINT"),
      openai_api_version="2024-12-01-preview",
      azure_deployment="gpt-5",
      openai_api_key=os.getenv("O3MINI_API_KEY"),
    )

    langchain_gemini_3_flash_preview_api = ChatGoogleGenerativeAI(
      model="gemini-3-flash-preview",
    )

    langchain_claude_api = ChatOpenAI(
      api_key=os.getenv("CLAUDE_API_KEY"),
      base_url="https://api.wenwen-ai.com/v1",
      model="claude-opus-4-5-20251101",
      temperature=0.0,
    )

    self.registry = {
        "gpt-4o-mini": langchain_gpt4omini_api,
        "o3-mini": langchain_o3mini_api,
        "qwen-plus": langchain_qwen_api,
        "deepseek-v4-pro": langchain_deepseek_4_pro_api,
        "gemini-3-flash-preview": langchain_gemini_3_flash_preview_api,
        "claude-opus-4": langchain_claude_api,
        "deepseek-v3.2": langchain_deepseek_v32_api,
        "doubao-seed-2.0-lite": langchain_doubao_2_lite_api,
        "doubao-seed-2.0-pro": langchain_doubao_2_pro_api,
        "gpt-5": langchain_gpt5_api,
        "glm-4.7": langchain_glm47_api,
    }
  
  def get_api(self, name):
    if name not in self.registry:
        raise ValueError(f"API '{name}' not found in LLMInterfaceManager.")  
    return self.registry[name]
  
  def has_api(self, name):
    return name in self.registry
  
  @property
  def default_api(self):
    return self.get_api(get_config('default_bot_type'))
  
  @property
  def multi_api_alts(self):
    return self.langchain_llms_api_alts
  
llm_manager = LLMInterfaceManager()

