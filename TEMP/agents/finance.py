import json

from pydantic_ai import Agent, RunContext, Tool, ModelRetry
from pydantic_ai.result import RunResult



from ..models import SearchResult, ExpectedData
from ..llms import model as llm


system_prompt = """
You are financial analyst, who can understand and extract data from markdown content.
If found the relevant data you have searched for, then you will tell it found. if found data is mismatching you will tell that as well. 

## Make sure that you give:
- your reasoning
- any related link to look further (like pdf, doc, or excel links)
- expected data and found data
"""


financial_analyst = Agent(
    llm, result_type=SearchResult, retries=3,
    deps_type=ExpectedData, 
    system_prompt=system_prompt
)

@financial_analyst.system_prompt
async def add_expected_data_into_prompt(ctx: RunContext[ExpectedData]) -> str:
    return f'## Expected Data to Search: ```json\n{json.dumps(ctx.deps.data, indent=4)}```\n\n## Markdown Content: ```markdown\n{ctx.deps.markdown_content}```'


@financial_analyst.result_validator
async def validate_the_link_url(ctx: RunContext[ExpectedData], result: SearchResult) -> SearchResult:
    if isinstance(result, SearchResult):
        found_link = str(result.found_link)
        base_url = str(ctx.deps.base_url).strip("/")
        if result.found:
            if found_link.strip("/").endswith("auctions"):
                raise ModelRetry("The link ends with the text `auctions`. This link is too general. Look for another url link.")
            if found_link.strip("/").endswith("results"):
                raise ModelRetry("The link ends with the text `auctions`. This link is too general. Look for another url link.")
            elif found_link.strip("/").endswith(base_url):
                raise ModelRetry("The link ends with a base url. This link is too general. Look for another url link.")

            else:
                return result
        else:
            result
    else:
        raise ModelRetry(f"Expected SearchResult type. but got {type(result)} type")

