# Orchids SWE Intern Challenge Template

This project consists of a backend built with FastAPI and a frontend built with Next.js and TypeScript.

## Backend

The backend uses `uv` for package management.

### Installation

Let's Start with setting up the .env file for the backend - for LLM & Cloud-based browser spinner setup:

```bash
uv sync
```

To install the backend dependencies, run the following command in the backend project directory:

```bash
uv sync
```

### Running the Backend

To run the backend development server, use the following command: (Template also in the .env.local file)

```
# We will first decide which LLM to use
LLM_PROVIDER=

# If using Gemini, set your API key here
GEMINI_API_KEY=

#Browserless API key
BROWSERLESS_API_KEY=

#If using Azure OpenAI, set the following variables
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_API_VERSION=
AZURE_OPENAI_DEPLOYMENT=
AZURE_OPENAI_DEPLOYMENT_NAME=

# If using Antropic (Claude), set the following variables
ANTHROPIC_API_KEY=
ANTHROPIC_MODEL_NAME=

```

## Frontend

The frontend is built with Next.js and TypeScript.

### Installation

To install the frontend dependencies, navigate to the frontend project directory and run:

```bash
npm install
```

### Running the Frontend

To start the frontend development server, run:

```bash
npm run dev
```
