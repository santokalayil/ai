from pydantic import BaseModel, HttpUrl
from pydantic_ai import Agent, RunContext


from ..llms import model as llm
from ..models import RawPageData

system_prompt = """You are an expert html to markdown extractor. From html content, you have to visualize how html rendered in page looks like and create markdown accordingly."""

class ConvertedMarkdown(BaseModel):
    url: HttpUrl
    markdown_text: str

html_content_extractor = Agent(
    llm, result_type=ConvertedMarkdown, retries=1,
    deps_type=RawPageData, 
    system_prompt=system_prompt
)

prompt = """
I have a website content along with its title. Can you figure the real structure (like how human understand) out by understanding the meaning and context from the page title and html content. 

# PAGE HTML

{raw_html}

# PAGE TITLE: 
{page_title}


NEVER EVER FORGET THE FOLLOWING:
- Find all information about upcoming auctions and already done auction results
- make sure that you analyse the css for getting structure to figure out intergently stucture. Once You analysed, get all those contents in markdown format
- create absolute links from relative links and place as a link to related text (the page url is `{url}`)
- Give Markdown alone so that I can write this output directly to .md file. I don't want any explanation
- make sure that you remove something like ```markdown ``` like text. Just give markdown text as as raw
"""


@html_content_extractor.system_prompt
async def add_raw_html_n_title_to_prompt(ctx: RunContext[RawPageData]) -> str:
    return prompt.format(raw_html=ctx.deps.html, page_title=ctx.deps.title, url=ctx.deps.url)
# f'## Expected Data to Search: ```json\n{json.dumps(ctx.deps.data, indent=4)}```\n\n## Markdown Content: ```markdown\n{ctx.deps.markdown_content}```'


