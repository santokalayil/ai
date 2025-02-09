import asyncio
import json
import os
import sys
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.extraction_strategy import ExtractionStrategy
from crawl4ai.models import Links, Media
import vertexai
from vertexai.generative_models import GenerativeModel
from datetime import datetime
from bs4 import BeautifulSoup
import nest_asyncio
import asyncio
import json
import os
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import vertexai
from vertexai.generative_models import GenerativeModel
from datetime import datetime
from bs4 import BeautifulSoup
import aiohttp
from playwright.async_api import async_playwright, Error  # Import Playwright
from pathlib import Path
from pydantic import BaseModel, Field, HttpUrl
from pydantic_ai import Agent, RunContext, Tool, ModelRetry
from pydantic_ai.result import RunResult
from pydantic_ai.models.vertexai import VertexAIModel

from typing import Literal

nest_asyncio.apply()

sys.path.append(r"/Users/santothomas/Developer/ai")

from ai.constants import VERTEX_MODEL_NAME, VERTEX_PROJECT_ID, VERTEX_LOCATION

from TEMP.utilities import get_base_url
from TEMP.scraper import fetch_html_with_playwright
from TEMP.models import SearchResult, ExpectedData
from TEMP.llms import model as llm
from TEMP.agents.html_to_markdown import html_content_extractor
from TEMP.agents.finance import financial_analyst


# url = "https://www.deutsche-finanzagentur.de/en/federal-securities/issuances/issuance-results"
url = "https://www.treasurydirect.gov/auctions/upcoming/"  # Example URL
# url = "https://www.aofm.gov.au/program/forthcoming-transactions"
 
raw_page_data = await fetch_html_with_playwright(url)  # Use Playwright
Path("content.html").write_text(raw_page_data.html)

res = html_content_extractor.run_sync("Convert Html to Markdown.", deps=raw_page_data)

# Search For needed Information in the Markdown File.
markdown_content = res.data.markdown_text
Path("content.md").write_text(markdown_content)
base_url = get_base_url(str(res.data.url))
expected_data = ExpectedData(base_url=base_url, data={"CUSIP": "912797LB1", "Offering Amount" :"52 B"}, markdown_content=markdown_content)
search_res = financial_analyst.run_sync("Check the Information ", deps=expected_data)
print(search_res.data.model_dump_json(indent=4))





## FIGURE OUT WHY THIS search_res.data comes None sometime which should not be possible with these pydantic validations
# Path("content.md").write_text(res.data.markdown_text)



  