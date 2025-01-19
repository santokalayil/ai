from pathlib import Path
from vertexai.generative_models import GenerativeModel, Part
import pymupdf4llm

from ai.constants import VERTEX_MODEL_NAME


def _extract_pdf_to_markdown_using_gemini_vision(path: Path) -> str:
    """Extracts pdf docs to string or markdown provided we give proper prompts. Currently prompts are internal to this function.
    Later this functinality will be accessible as param input.
    """
    if input("Do you really want to use Gemini Vision API directory. \nBEWARE that cost is not recorded!")\
        .strip().lower() in ["n", "no"]:
        raise NotImplementedError("Unable to extract pdf")


    prompt = """
    You are a financial analyst who reads the document of companies. 
    identify Details of Voting Power and find what is the total number of securities.
    Also give me in which page number I can find the information
    """

    model = GenerativeModel(VERTEX_MODEL_NAME)
    pdf_file = Part.from_data(path.read_bytes(), mime_type="application/pdf")
    contents = [pdf_file, prompt]

    response = model.generate_content(contents)
    return response.text

def _extract_pdf_to_markdown_using_pymupdf4llm(path: Path) -> str:
    return pymupdf4llm.to_markdown(path)

# https://youtu.be/mdLBr9IMmgI?si=JaeDehlNXS-J5N_9
# Checkout this Marker opensouce library which is lot better. Consider issue with using this on business env.
# ... Crawl4AI may not work in our scenario (which i need to search and dyamic rendering is there in webpage)
# https://youtu.be/BkGVMhZZEDc?si=6v6OkiOGJ15rlvDp   # PDF Extract Kit

def extract_pdf_to_markdown(path: Path, use_llm=False) -> str:
    """
    Extracts PDF documents to markdown. 
    If `use_llm` is `True`, this function will use vertexai and Gemini Vision features to convert to md. 
    Else, it uses `pymupdf3llmm under the hood. 
    """
    if use_llm is True:
        return _extract_pdf_to_markdown_using_gemini_vision(path)
    return _extract_pdf_to_markdown_using_pymupdf4llm(path)
    
