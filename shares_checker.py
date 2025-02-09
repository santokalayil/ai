import asyncio
import nodriver as uc
from typing import List
from pathlib import Path
import pandas as pd
import httpx

import ai
from spyders.asx import search_asx_docs
from parsers.pdf_extraction import extract_pdf_to_markdown

__all__ = ["ai"]

async def main():
    browser = await uc.start(headless=False)
    search_query = "CBA"
    # df = await search_asx_docs(search_query, browser)
    df: pd.DataFrame = await search_asx_docs(search_query, browser)
    
    print(df.to_markdown())
    # ideally we should give everything to LLM (until last few days (after deciding))
    headline_col = "HEADLINE / DOC SIZE"
    ann, link = df.loc[0, headline_col]
    res = httpx.get(link)
    if res.headers['content-type'] != "application/pdf":
        raise ValueError("not a pdf file")

    pdf_path = ai.paths.DATA_DIR / f"{ann}.pdf"
    pdf_path.write_bytes(res.content)

    markdown_string = extract_pdf_to_markdown(pdf_path, use_llm=False)

    md_path = pdf_path.with_suffix('.md')
    md_path.write_bytes(markdown_string.encode())


    # GET ALL POSSIBLE COMBINATIONS OF CHECK (like Share Change? all of them keep in pydantic models)

    if not browser.stopped:
        browser.stop()


if __name__ == "__main__":
    # uc.loop().run_until_complete(main())
    asyncio.run(main())
