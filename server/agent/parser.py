from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from simcity.agents.brain.interface import langchain_llms_api

class BuildingStrategy(BaseModel):
  code: str = Field(description="a line of function call. e.g. func1(para1, para2)")

class BuildingStrategies(BaseModel):
  reasoning: str = Field(description="llms' reasoning")
  actions: list[str] = Field(description="a list of function call. e.g. [func1(para1, para2), func2(para1, para2)]")
buildingStrategies = JsonOutputParser(pydantic_object=BuildingStrategies)

class CitizenActionParser(BaseModel):
  reasoning: str = Field(description="llms' reasoning")
  actions: list[str] = Field(description="a list of function call. e.g. [func1(para1, para2), func2(para1, para2)]")
citizenActionParser = JsonOutputParser(pydantic_object=CitizenActionParser)