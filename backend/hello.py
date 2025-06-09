from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Dict, List, Optional
import uvicorn
import asyncio # For async operations with Playwright
from playwright.async_api import async_playwright, Page, expect
import base64 # To encode/decode images
from PIL import Image # For image processing (optional, but useful for screenshot quality)
import io # For handling image bytes
import os # For environment variables
from dotenv import load_dotenv # Load environment variables from .env file

# Load environment variables
load_dotenv()

# --- LLM Setup ---
import google.generativeai as genai

# Configure Gemini API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set. Please set it in a .env file or your system environment.")

genai.configure(api_key=GEMINI_API_KEY)
# Initialize the generative model
# Use a model capable of multimodal input (text + image) like 'gemini-1.5-pro'
# Or 'claude-3-sonnet' if you decide to use Anthropic's API later
model = genai.GenerativeModel('gemini-1.5-pro')


# Create FastAPI instance
app = FastAPI(
    title="Orchids Challenge API",
    description="Backend for the Orchids Website Cloning Challenge",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
# (Keeping existing Item models for now, though they are not directly used by the cloning feature)
class Item(BaseModel):
    id: int
    name: str
    description: str = None

class ItemCreate(BaseModel):
    name: str
    description: str = None

class CloneRequest(BaseModel):
    url: HttpUrl # Use HttpUrl for URL validation

class CloneResponse(BaseModel):
    original_url: HttpUrl
    cloned_html: str
    message: str


# In-memory storage for demo purposes
items_db: List[Item] = [
    Item(id=1, name="Sample Item", description="This is a sample item"),
    Item(id=2, name="Another Item", description="This is another sample item")
]

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Hello from FastAPI backend!", "status": "running"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "orchids-challenge-api"}

# Get all items
@app.get("/items", response_model=List[Item])
async def get_items():
    return items_db

# Get item by ID
@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int):
    for item in items_db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

# Create new item
@app.post("/items", response_model=Item)
async def create_item(item: ItemCreate):
    new_id = max([item.id for item in items_db], default=0) + 1
    new_item = Item(id=new_id, **item.dict())
    items_db.append(new_item)
    return new_item

# Update item
@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: ItemCreate):
    for i, existing_item in enumerate(items_db):
        if existing_item.id == item_id:
            updated_item = Item(id=item_id, **item.dict())
            items_db[i] = updated_item
            return updated_item
    raise HTTPException(status_code=404, detail="Item not found")

# Delete item
@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    for i, item in enumerate(items_db):
        if item.id == item_id:
            deleted_item = items_db.pop(i)
            return {"message": f"Item {item_id} deleted successfully", "deleted_item": deleted_item}
    raise HTTPException(status_code=404, detail="Item not found")


# --- NEW WEBSITE CLONING ENDPOINT ---
@app.post("/clone", response_model=CloneResponse)
async def clone_website(request: CloneRequest):
    """
    Clones a given website URL by scraping its design context and using an LLM to replicate it.
    """
    print(f"Received request to clone URL: {request.url}")
    try:
        scraped_data = await scrape_website(str(request.url))
        print("Website scraped successfully.")

        # Prepare content for the LLM
        # Gemini 1.5 Pro can take lists of text and image parts
        llm_parts = [
            {"text": "You are an expert web developer AI. Your task is to accurately clone the aesthetic and layout of the given website into clean, modern, single HTML file with inline CSS (<style> tag in head). Focus on visual fidelity, responsive design, and semantic HTML. Do NOT include JavaScript unless explicitly necessary for core functionality. Ensure all content and styling elements are directly embedded in the HTML file, avoiding external links if possible, to make it a self-contained clone. Make sure the output is JUST the HTML content, without any additional text or markdown formatting outside the HTML itself."},
            {"text": f"Here is the HTML structure of the original website:\n```html\n{scraped_data['dom_html']}\n```"},
        ]

        if scraped_data.get('screenshot_base64'):
            # Convert base64 image to a format consumable by Gemini API
            # Gemini's vision models expect image parts in a specific format
            image_bytes = base64.b64decode(scraped_data['screenshot_base64'])
            image_part = {
                "mime_type": "image/jpeg", # Assuming JPEG for screenshots
                "data": image_bytes
            }
            llm_parts.append(image_part)
            llm_parts.append({"text": "Here is a screenshot of the original website. Use this visual information along with the HTML structure to create a visually identical clone."})

        # Add more context if extracted (e.g., specific styles, asset URLs)
        # For simplicity, we're focusing on screenshot and DOM primarily for this example.
        # if scraped_data.get('key_styles'):
        #     llm_parts.append({"text": f"Key extracted styles:\n```css\n{json.dumps(scraped_data['key_styles'], indent=2)}\n```"})


        print("Sending data to LLM...")
        # Make the LLM call
        response = await model.generate_content_async(llm_parts)
        cloned_html = response.text
        print("LLM response received.")

        # Basic post-processing: remove potential markdown if LLM adds it
        if cloned_html.startswith("```html") and cloned_html.endswith("```"):
            cloned_html = cloned_html[7:-3].strip()


        return CloneResponse(
            original_url=request.url,
            cloned_html=cloned_html,
            message="Website cloned successfully!"
        )

    except Exception as e:
        print(f"Error cloning website: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clone website: {str(e)}")


# --- WEBSITE SCRAPING LOGIC ---
async def scrape_website(url: str) -> Dict:
    """
    Scrapes a given URL using Playwright to extract design context.
    Returns screenshot (base64) and DOM HTML.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch() # You can choose chromium, firefox, or webkit
        page = await browser.new_page()

        try:
            print(f"Navigating to {url}...")
            await page.goto(url, wait_until='networkidle') # Wait for network to be idle
            print(f"Page loaded: {url}")

            # Take a full page screenshot
            screenshot_bytes = await page.screenshot(full_page=True, type='jpeg', quality=80)
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            print("Screenshot taken.")

            # Get the outer HTML of the entire document
            dom_html = await page.content()
            print("DOM HTML extracted.")

            # You can add more sophisticated scraping here:
            # - Extracting specific CSS rules: You could iterate through stylesheets or use page.evaluate() to get computed styles for key elements.
            # - Identifying key assets (images, fonts) and their URLs.
            # - Parsing CSS files (if you download them) to extract variables/global styles.

            return {
                "screenshot_base64": screenshot_base64,
                "dom_html": dom_html,
                # "key_styles": {}, # Placeholder for more advanced style extraction
            }

        except Exception as e:
            print(f"Playwright scraping error for {url}: {e}")
            raise RuntimeError(f"Could not scrape website: {e}")
        finally:
            await browser.close()


def main():
    """Run the application"""
    uvicorn.run(
        "hello:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )


if __name__ == "__main__":
    main()