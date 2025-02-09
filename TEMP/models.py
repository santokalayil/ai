from typing import Optional, Literal
from pydantic import BaseModel, HttpUrl, Field

class RawPageData(BaseModel):
    url: HttpUrl
    title: str
    html: str

class USAuctionDataExpected(BaseModel):
    cusip: str
    offered_amount: str

class USAuctionDataFound(BaseModel):
    cusip: Optional[str]
    offered_amount: Optional[str]

class MatchedData(BaseModel):
    expected: USAuctionDataExpected
    found: USAuctionDataFound


class SearchResult(BaseModel):
    found: bool
    reasoning: str
    found_link: Optional[HttpUrl] = Field(
        description=(
            "Found link to substantiate the information. This link, most probably should be a pdf link. "
            "The Link should not be too general like that which ends with `auctions` or `upcoming`"
        ) #Do not keep general link here. you must find the link only inside markdown table if there are tables"
    )
    found_data_is_matching: bool
    matched_data: MatchedData
    upcoming_or_auction_results: Literal["Upcoming", "AuctionResults"]



class ExpectedData(BaseModel):
    base_url: HttpUrl
    data: dict
    markdown_content: str
