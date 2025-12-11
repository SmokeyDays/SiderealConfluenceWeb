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

