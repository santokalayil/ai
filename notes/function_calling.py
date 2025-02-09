import sys
sys.path.append(r"/Users/santothomas/Developer/ai")

import ai

import requests
from vertexai.generative_models import (
    FunctionDeclaration,
    GenerationConfig,
    GenerativeModel,
    Part,
    Tool,
)

get_product_info = FunctionDeclaration(
    name="get_product_info",
    description="Get the stock amount and identifier for a given product",
    parameters={
        "type": "object",
        "properties": {
            "product_name": {"type": "string", "description": "Product name"}
        },
    },
)

get_store_location = FunctionDeclaration(
    name="get_store_location",
    description="Get the location of the closest store",
    parameters={
        "type": "object",
        "properties": {"location": {"type": "string", "description": "Location"}},
    },
)

place_order = FunctionDeclaration(
    name="place_order",
    description="Place an order",
    parameters={
        "type": "object",
        "properties": {
            "product": {"type": "string", "description": "Product name"},
            "address": {"type": "string", "description": "Shipping address"},
        },
    },
)


retail_tool = Tool(
    function_declarations=[
        get_product_info,
        get_store_location,
        place_order,
    ],
)

model = GenerativeModel(
    "gemini-1.5-pro",
    generation_config=GenerationConfig(temperature=0),
    tools=[retail_tool],
)
chat = model.start_chat()


prompt = """
Do you have the Pixel 8 Pro in stock?
"""

response = chat.send_message(prompt)
response.candidates[0].content.parts[0]


# Here you can use your preferred method to make an API request and get a response.
# In this example, we'll use synthetic data to simulate a payload from an external API response.

api_response = {"sku": "GA04834-US", "in_stock": "yes"}
response = chat.send_message(
    Part.from_function_response(
        name="get_product_info",
        response={
            "content": api_response,
        },
    ),
)
response.text

prompt = """
What about the Pixel 8? Is there a store in
Mountain View, CA that I can visit to try one out?
"""

response = chat.send_message(prompt)
response.candidates[0].content.parts[0]


# =======================

get_location = FunctionDeclaration(
    name="get_location",
    description="Get latitude and longitude for a given location",
    parameters={
        "type": "object",
        "properties": {
            "poi": {"type": "string", "description": "Point of interest"},
            "street": {"type": "string", "description": "Street name"},
            "city": {"type": "string", "description": "City name"},
            "county": {"type": "string", "description": "County name"},
            "state": {"type": "string", "description": "State name"},
            "country": {"type": "string", "description": "Country name"},
            "postal_code": {"type": "string", "description": "Postal code"},
        },
    },
)

location_tool = Tool(
    function_declarations=[get_location],
)

prompt = """
I want to get the coordinates for the following address:
1600 Amphitheatre Pkwy, Mountain View, CA 94043, US
"""

response = model.generate_content(
    prompt,
    generation_config=GenerationConfig(temperature=0),
    tools=[location_tool],
)
response.candidates[0].content.parts[0]



from pydantic import BaseModel, Field

class Address(BaseModel):
    name: str = Field(..., description="Name of the Person to whom we are sending.")
    pin_code: str = Field(max_length=6, min_length=6)

a = Address()

Address.model_json_schema()
