# hello.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Dict, List, Optional, Any
import uvicorn
import asyncio
import httpx
import base64
import os
from dotenv import load_dotenv

# Import the new LLM service module and the centralized system prompt
from llm_service import get_llm_provider, LLMProvider, LLM_SYSTEM_PROMPT


# Load environment variables
load_dotenv()

# --- LLM Configuration Selection ---
LLM_PROVIDER_NAME = os.getenv("LLM_PROVIDER", "azure_openai")
print(f"Using LLM Provider: {LLM_PROVIDER_NAME}")

try:
    llm_provider: LLMProvider = get_llm_provider(LLM_PROVIDER_NAME)
except ValueError as e:
    print(f"FATAL ERROR: Failed to initialize LLM provider: {e}")
    exit(1)
except Exception as e:
    print(f"FATAL ERROR: An unexpected error occurred during LLM provider initialization: {e}")
    exit(1)


# --- EXTERNAL API KEY FOR BROWSERLESS/SCREENSHOT SERVICE ---
BROWSERLESS_API_KEY = os.getenv("BROWSERLESS_API_KEY")
if not BROWSERLESS_API_KEY:
    raise ValueError("BROWSERLESS_API_KEY environment variable not set. Please set it for the external scraping service.")

# Create FastAPI instance
app = FastAPI(
    title="Orchids Challenge API",
    description="Backend for the Orchids Website Cloning Challenge",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for cloning
class CloneRequest(BaseModel):
    url: HttpUrl

class CloneResponse(BaseModel):
    original_url: HttpUrl
    cloned_html: str
    message: str


# Root endpoint
@app.get("/")
async def root():
    return {"message": "Hello from FastAPI backend!", "status": "running"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "orchids-challenge-api"}


# --- WEBSITE CLONING ENDPOINT (Uses Modular LLM) ---
@app.post("/clone", response_model=CloneResponse)
async def clone_website(request: CloneRequest):
    """
    Clones a given website URL by fetching its design context (screenshot) via an external API
    and using a modular LLM provider to replicate it.
    """
    print(f"Received request to clone URL: {request.url}")
    try:
        scraped_data = await scrape_website_via_api(str(request.url))
        print("Website screenshot retrieved via external API.")

        # Prepare content parts for the LLM provider
        llm_parts: List[Dict[str, Any]] = []

        # This initial text part is added AFTER the system prompt for clarity in multi-modal input.
        llm_parts.append({"text": "Here is the website to clone:"})

        if scraped_data.get('screenshot_base64'):
            image_bytes = base64.b64decode(scraped_data['screenshot_base64'])
            image_part = {
                "mime_type": "image/jpeg",
                "data": image_bytes
            }
            llm_parts.append(image_part)
            llm_parts.append({"text": "Here is a screenshot of the original website. Use this visual information to create a visually identical clone. Focus on the visual layout as the primary input."})
        else:
             llm_parts.append({"text": "No screenshot was provided. Please generate a clone based purely on the instructions."})

        print(f"Sending data to LLM ({LLM_PROVIDER_NAME})...")
        # Pass the centralized system prompt to the LLM provider
        cloned_html = await llm_provider.generate_content(LLM_SYSTEM_PROMPT, llm_parts)
        print("LLM response received.")

        return CloneResponse(
            original_url=request.url,
            cloned_html=cloned_html,
            message="Website cloned successfully using external API (Screenshot only) and modular LLM!"
        )

    except Exception as e:
        print(f"Error cloning website: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clone website: {str(e)}")


# --- EXTERNAL API SCRAPING LOGIC (Unchanged) ---
# --- EXTERNAL API SCRAPING LOGIC (Corrected Browserless.io URL again) ---
async def scrape_website_via_api(url: str) -> Dict:
    """
    Fetches a website screenshot using Browserless.io's /screenshot endpoint.
    This call primarily returns an image.
    """
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    # CORRECTED LINE: Removed Markdown link syntax - this is the problematic line
    browserless_screenshot_url = f"https://production-sfo.browserless.io/screenshot?token={BROWSERLESS_API_KEY}"

    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache"
    }
    payload = {
        "url": url,
        "options": {
            "type": "jpeg",
            "quality": 80,
            "fullPage": True
        }
    }

    # Debugging prints (keep these for now, they are very helpful)
    print(f"DEBUG: Processed URL sent to Browserless.io payload: {url}")
    print(f"DEBUG: Full Browserless API URL (with token): {browserless_screenshot_url}")
    print(f"DEBUG: Payload sent to Browserless.io: {payload}")


    async with httpx.AsyncClient(timeout=45.0) as client:
        try:
            print(f"Calling Browserless.io /screenshot API for {url}...")
            response = await client.post(browserless_screenshot_url, headers=headers, json=payload)
            response.raise_for_status()

            image_bytes = response.content
            screenshot_base64 = base64.b64encode(image_bytes).decode('utf-8')

            print(f"Screenshot received from Browserless.io. Size: {len(image_bytes)} bytes.")

            return {
                "screenshot_base64": screenshot_base64,
                "dom_html": "",
            }

        except httpx.RequestError as e:
            raise RuntimeError(f"External API request failed for {url}: {e}")
        except httpx.HTTPStatusError as e:
            print(f"External API HTTP Error: {e.response.status_code} - {e.response.text}")
            if e.response.status_code in [401, 403]:
                print(f"Browserless.io Error Details: {e.response.text}")
            raise RuntimeError(f"External API returned an error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            print(f"An unexpected error occurred with external API for {url}: {e}")
            raise RuntimeError(f"An unexpected error occurred with external API: {e}")


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