from typing import List
import asyncio
from io import StringIO
import nodriver as uc
import pandas as pd

from ai.constants import VERTEX_MODEL_NAME, VERTEX_PROJECT_ID, VERTEX_LOCATION


async def search_asx(q: str, browser: uc.Browser):
    page = await browser.get('https://www.asx.com.au/')
    cookie_accept_selector = "button[id=onetrust-accept-btn-handler]"
    await page.wait_for(cookie_accept_selector)
    btn = await page.select(cookie_accept_selector)
    await btn.click()
    
    search_btn = await page.select("a[role=button]")
    await search_btn.click()
    
    search_input = await page.select("input[name=search-input]")
    await search_input.send_keys(q+"\n")
    
    autocomplete_div = "div[class=autocomplete-container]"
    ac_bar = await page.wait_for(autocomplete_div)
    # press enter
    
    view_all_results = await page.find("VIEW ALL RESULTS", best_match=True)
    if view_all_results:
        await view_all_results.click()
        
    all_results_loc = "div[id=all]"
    all_results = await page.wait_for(all_results_loc, timeout=20)
    await all_results.get_html()
    list_of_tables = await all_results.query_selector_all("table")
    table_htmls = []
    for table in list_of_tables:
        htm = await table.get_html()
        table_htmls.append(htm)
        
    
    dfs: List[pd.DataFrame] = []
    for i in table_htmls:
        try:
            dfs_extracted = pd.read_html(i, extract_links="body")
            if dfs_extracted:
                dfs.append(dfs_extracted[0])
        except ValueError:
            print("seems no data found")
        except IndexError:
            print("index errors. seems no data found")
    dfs
    
    relevant_dfs = []
    for df in dfs:
        if "ASX Code" in df.columns:
            relevant_dfs.append(df)
    if not relevant_dfs:
        msg = "no relevant data found"
        print(msg)
        raise ValueError(msg)
    if len(relevant_dfs) > 1:
        raise ValueError("more than one relevant data found")
    df = relevant_dfs[0]
    
    base_url = "https://www.asx.com.au"
    df["url"] = df["ASX Code"].str[1].apply(lambda x: base_url + x)
    df["code"] = df["ASX Code"].str[0]
    
    return df
  

async def search_asx_docs(q: str, browser: uc.Browser) -> pd.DataFrame:
    df: pd.DataFrame = asyncio.run(search_asx(q, browser))
    print(df[["url", "code"]])


    # ask LLM which one to use from above based on the input data we had earlier.
    url = df.iloc[0]["url"]

    page = await browser.get(url)
    await page.scroll_down(200)


    el = await page.find("SEE ALL ANNOUNCEMENTS", best_match=True)
    await el.click()

    ann_loc = "section[id=markets_announcements]"
    ann_section = await page.wait_for(ann_loc)
    await page.wait(5)
    ann_section = await page.select(ann_loc)
    htm = await ann_section.get_html()
    dfs = pd.read_html(StringIO(htm), extract_links="body")
    if not dfs:
        raise ValueError("no table found")
    if len(dfs) > 1:
        raise ValueError("more than one table found")
    df = dfs[0]

    
    if not df.shape[0]:
        raise Exception("no records of annoucements found")
    return df