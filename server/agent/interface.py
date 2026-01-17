from langchain_openai import AzureChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv(override=True)



langchain_llms_api = AzureChatOpenAI(
  azure_endpoint="https://yeqifeng-eastus-new.openai.azure.com/",
  openai_api_version="2024-12-01-preview",
  azure_deployment="gpt-4o-mini",
  openai_api_key=os.getenv("O4MINI_API_KEY"),
)

# langchain_llms_api = AzureChatOpenAI(
#   azure_endpoint="https://yeqifeng-eastus2-2026.openai.azure.com/",
#   openai_api_version="2024-12-01-preview",
#   azure_deployment="o3-mini",
#   openai_api_key=os.getenv("O3MINI_API_KEY"),
# )

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

langchain_vlm_api = AzureChatOpenAI(
  azure_endpoint="https://yeqifeng-eastus-new.openai.azure.com/",
  openai_api_version="2024-12-01-preview",
  azure_deployment="gpt-4",
  openai_api_key=os.getenv("GPT4API_KEY"),
  max_tokens=500,
)

class LLMInterfaceManager:
  def __init__(self):
    self.registry = {
        "gpt-4o-mini": langchain_llms_api,
        "gpt-4": langchain_vlm_api,
    }
  
  def get_api(self, name):
    if name not in self.registry:
        return self.registry.get("gpt-4o-mini")
    return self.registry[name]

llm_manager = LLMInterfaceManager()

