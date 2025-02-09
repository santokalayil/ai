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

sys.path.append(r"/Users/santothomas/Developer/ai")

from ai.constants import VERTEX_MODEL_NAME, VERTEX_PROJECT_ID, VERTEX_LOCATION


MODEL_NAME = os.getenv("GEMINI_MODEL")

class WebElement(BaseModel):
    """Schema for any HTML element"""
    tag: str
    text: Optional[str]
    attributes: Dict[str, str]
    classes: List[str]
    id: Optional[str]

class LinkData(BaseModel):
    """Schema for link information"""
    href: str
    text: Optional[str]
    title: Optional[str]
    type: str
    attributes: Dict[str, str]

class MediaData(BaseModel):
    """Schema for media information"""
    src: str
    type: str
    alt: Optional[str]
    title: Optional[str]
    description: Optional[str]
    attributes: Dict[str, str]

class GeminiAnalysis(BaseModel):
    """AI analysis of the webpage content"""
    main_topic: str
    summary: str
    key_points: List[str]
    sentiment: str
    detected_entities: List[Dict[str, str]]
    content_type: str
    language: str
    text_structure: Dict[str, Any]

class WebpageContent(BaseModel):
    """Complete webpage content structure"""
    url: str
    timestamp: str
    title: Optional[str]
    meta_tags: List[Dict[str, str]]
    headers: List[Dict[str, str]]
    content_by_tag: Dict[str, List[WebElement]]
    links: Dict[str, List[LinkData]]
    media: Dict[str, List[MediaData]]
    tables: List[List[List[str]]]
    forms: List[Dict[str, Any]]
    scripts: List[Dict[str, str]]
    styles: List[Dict[str, str]]
    raw_text: str
    ai_analysis: Optional[GeminiAnalysis]

class GeminiWebpageExtractor(ExtractionStrategy):
    """Strategy to extract all data and analyze with Gemini"""
    input_format = "html"
    
    def __init__(self, project_id: str, location: str = "us-central1"):
        self.important_tags = [
            'div', 'p', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'article', 'section', 'main', 'header', 'footer', 'nav',
            'aside', 'table', 'form', 'ul', 'ol', 'li', 'blockquote'
        ]
        
        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)
        self.model = GenerativeModel(MODEL_NAME)  # s.getenv("VERTEX_AI_PROJECT_ID")

    async def _analyze_with_gemini(self, content: str, title: str) -> GeminiAnalysis:
        """Analyze content using Gemini"""
        prompt = f"""
        Analyze the following webpage content. The page title is: {title}
        
        Provide a structured analysis with the following information:
        1. Main topic or purpose of the page
        2. Brief summary (2-3 sentences)
        3. Key points (up to 5)
        4. Overall sentiment (positive, negative, or neutral)
        5. Important entities (people, organizations, products, etc.)
        6. Content type (article, product page, documentation, etc.)
        7. Primary language
        8. Text structure analysis (headings, paragraphs, lists organization)
        
        Format the response as valid JSON matching this schema:
        {{
            "main_topic": "string",
            "summary": "string",
            "key_points": ["string"],
            "sentiment": "string",
            "detected_entities": [{{"type": "string", "name": "string"}}],
            "content_type": "string",
            "language": "string",
            "text_structure": {{}}
        }}
        
        Content to analyze:
        {content[:10000]}  # First 10K characters for analysis
        """
        
        try:
            chat = self.model.start_chat()
            response = chat.send_message(prompt)
            return GeminiAnalysis(**json.loads(response.text))
        except Exception as e:
            print(f"Gemini analysis error: {str(e)}")
            return None

    def _extract_element_data(self, element) -> WebElement:
        """Extract data from a BeautifulSoup element"""
        return WebElement(
            tag=element.name,
            text=element.get_text(strip=True) if element.string else None,
            attributes={k: v for k, v in element.attrs.items() if k != 'class'},
            classes=element.get('class', []),
            id=element.get('id')
        )

    def _extract_meta_tags(self, soup) -> List[Dict[str, str]]:
        """Extract all meta tags"""
        return [
            {
                'name': tag.get('name', tag.get('property', '')),
                'content': tag.get('content', ''),
                **{k: v for k, v in tag.attrs.items() if k not in ['name', 'property', 'content']}
            }
            for tag in soup.find_all('meta')
        ]

    def _extract_tables(self, soup) -> List[List[List[str]]]:
        """Extract all tables"""
        tables = []
        for table in soup.find_all('table'):
            table_data = []
            for row in table.find_all('tr'):
                row_data = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
                table_data.append(row_data)
            tables.append(table_data)
        return tables

    def _extract_forms(self, soup) -> List[Dict[str, Any]]:
        """Extract all forms and their inputs"""
        forms = []
        for form in soup.find_all('form'):
            form_data = {
                'action': form.get('action'),
                'method': form.get('method'),
                'id': form.get('id'),
                'class': form.get('class'),
                'inputs': [
                    {
                        'type': input_tag.get('type'),
                        'name': input_tag.get('name'),
                        'id': input_tag.get('id'),
                        'value': input_tag.get('value'),
                        'placeholder': input_tag.get('placeholder'),
                        **{k: v for k, v in input_tag.attrs.items() 
                           if k not in ['type', 'name', 'id', 'value', 'placeholder']}
                    }
                    for input_tag in form.find_all('input')
                ],
                'textareas': [
                    {
                        'name': textarea.get('name'),
                        'id': textarea.get('id'),
                        'text': textarea.get_text(strip=True),
                        **{k: v for k, v in textarea.attrs.items() 
                           if k not in ['name', 'id']}
                    }
                    for textarea in form.find_all('textarea')
                ],
                'selects': [
                    {
                        'name': select.get('name'),
                        'id': select.get('id'),
                        'options': [
                            {
                                'value': option.get('value'),
                                'text': option.get_text(strip=True),
                                'selected': option.get('selected') is not None
                            }
                            for option in select.find_all('option')
                        ]
                    }
                    for select in form.find_all('select')
                ]
            }
            forms.append(form_data)
        return forms

    def _process_links(self, links: Links) -> Dict[str, List[LinkData]]:
        """Process and organize links"""
        return {
            "internal": [
                LinkData(
                    href=link.href,
                    text=link.text,
                    title=link.title,
                    type="internal",
                    attributes=link.__dict__
                ).model_dump()
                for link in links.internal
            ],
            "external": [
                LinkData(
                    href=link.href,
                    text=link.text,
                    title=link.title,
                    type="external",
                    attributes=link.__dict__
                ).model_dump()
                for link in links.external
            ]
        }

    def _process_media(self, media: Media) -> Dict[str, List[MediaData]]:
        """Process and organize media items"""
        return {
            "images": [
                MediaData(
                    src=img.src,
                    type="image",
                    alt=img.alt,
                    title=getattr(img, 'title', None),
                    description=img.desc,
                    attributes=img.__dict__
                ).model_dump()
                for img in media.images
            ],
            "videos": [
                MediaData(
                    src=video.src,
                    type="video",
                    alt=None,
                    title=getattr(video, 'title', None),
                    description=video.desc,
                    attributes=video.__dict__
                ).model_dump()
                for video in media.videos
            ],
            "audios": [
                MediaData(
                    src=audio.src,
                    type="audio",
                    alt=None,
                    title=getattr(audio, 'title', None),
                    description=audio.desc,
                    attributes=audio.__dict__
                ).model_dump()
                for audio in media.audios
            ]
        }

    def extract(self, html: str, *args, **kwargs) -> str:
        """Main extraction method"""
        return asyncio.run(self._extract(html, *args, **kwargs))

    async def _extract(self, html: str, *args, **kwargs) -> str:
        """Async extraction method"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Get links and media from crawler result
        links = kwargs.get('links', Links(internal=[], external=[]))
        media = kwargs.get('media', Media(images=[], videos=[], audios=[]))
        url = kwargs.get('url', '')

        # Extract content by tag type
        content_by_tag = {}
        for tag in self.important_tags:
            elements = soup.find_all(tag)
            if elements:
                content_by_tag[tag] = [
                    self._extract_element_data(elem).dict()
                    for elem in elements
                ]

        # Get raw text for AI analysis
        raw_text = soup.get_text(separator='\n', strip=True)
        title = soup.title.string if soup.title else ""

        # Get AI analysis
        ai_analysis = await self._analyze_with_gemini(raw_text, title)

        # Create complete webpage data
        webpage_data = WebpageContent(
            url=url,
            timestamp=datetime.now().isoformat(),
            title=title,
            meta_tags=self._extract_meta_tags(soup),
            headers=[{'name': k, 'value': v} for k, v in kwargs.get('headers', {}).items()],
            content_by_tag=content_by_tag,
            links=self._process_links(links),
            media=self._process_media(media),
            tables=self._extract_tables(soup),
            forms=self._extract_forms(soup),
            scripts=[{
                'src': script.get('src'),
                'type': script.get('type'),
                'content': script.string if script.string else None
            } for script in soup.find_all('script')],
            styles=[{
                'type': style.get('type'),
                'content': style.string if style.string else None
            } for style in soup.find_all('style')],
            raw_text=raw_text,
            ai_analysis=ai_analysis
        )

        return json.dumps(webpage_data.dict(), ensure_ascii=False)

async def main():
    url = "https://www.treasurydirect.gov/auctions/upcoming/"

    # Initialize with your Google Cloud project details
    project_id = os.getenv("VERTEX_AI_PROJECT_ID")
    
    # Create the extraction strategy
    extractor = GeminiWebpageExtractor(project_id=project_id)
    
    # Configure the crawler
    config = CrawlerRunConfig(
        word_count_threshold=1,  # Keep all text
        excluded_tags=[],  # Don't exclude any tags
        exclude_external_links=False,  # Keep all links
        exclude_social_media_links=False,
        exclude_external_images=False,
        process_iframes=True,
        extraction_strategy=extractor
    )
    
    # Run the crawler
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=url,
            config=config
        )
        
        if result.success:
            # Save the data to a file
            filename = f"webpage_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(result.extracted_content)
            print(f"Data saved to {filename}")
            
            # Print summary
            extracted_content = result.extracted_content
            try:
                # Ensure the content is a valid JSON string
                if isinstance(extracted_content, str):
                    data = json.loads(extracted_content)
                else:
                    data = extracted_content

                # Handle the case where the content is a list of characters
                if isinstance(data, list) and all(isinstance(item, str) for item in data):
                    data = json.loads("".join(data))

                # Assuming the first item is the main content if it's a list
                if isinstance(data, list):
                    data = data[0]

                print("\nExtraction Summary:")
                print(f"- Title: {data['title']}")
                print(f"- Meta tags: {len(data['meta_tags'])}")
                print(f"- Internal links: {len(data['links']['internal'])}")
                print(f"- External links: {len(data['links']['external'])}")
                print(f"- Images: {len(data['media']['images'])}")
                print(f"- Tables: {len(data['tables'])}")
                print(f"- Forms: {len(data['forms'])}")
                
                if data['ai_analysis']:
                    print("\nAI Analysis:")
                    print(f"- Main Topic: {data['ai_analysis']['main_topic']}")
                    print(f"- Content Type: {data['ai_analysis']['content_type']}")
                    print(f"- Sentiment: {data['ai_analysis']['sentiment']}")
                    print("- Key Points:", *data['ai_analysis']['key_points'], sep='\n  - ')
            except json.JSONDecodeError:
                print("Error decoding JSON content")
                return
        else:
            print(f"Error: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(main())