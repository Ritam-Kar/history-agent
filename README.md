# History Agent

An AI-powered conversational agent built with Google ADK and Gemini that tells you the 3 most significant historical events on any given date.

## What it does

- Accepts a date in natural language — "What happened on July 20th?" or "Tell me about March 15th"
- Fetches real historical events from the Wikipedia On This Day API
- Uses Gemini 2.5 Flash to select the 3 most historically significant events
- Returns a concise bullet-point digest
- Responds with a friendly greeting if no date is provided

## Architecture

Three sequential agents run in a pipeline:

1. **DateParser** — extracts the month and day from the user's message
2. **WikiFetcher** — calls the Wikipedia On This Day API and retrieves up to 15 events
3. **Narrator** — selects the top 3 events and formats the response

## Tech stack

- [Google ADK](https://github.com/google/adk-python) — agent orchestration
- Gemini 2.5 Flash — AI inference via Vertex AI
- Wikipedia On This Day API — free, no auth required
- Google Cloud Run — serverless deployment
- Docker — containerisation

## Live demo

- Web UI: `https://history-agent-624320433211.us-central1.run.app/dev-ui/`
- API endpoint: `https://history-agent-624320433211.us-central1.run.app/run`

## Project structure
```
history-agent/
├── history_agent/
│   ├── __init__.py
│   └── agent.py        # Three LlmAgents + SequentialAgent
├── Dockerfile
├── entrypoint.sh
└── requirements.txt
```

## Running locally

### Prerequisites
- Python 3.11+
- Docker
- Google Cloud account with Vertex AI enabled

### Steps
```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/history-agent.git
cd history-agent

# Authenticate with Google Cloud
gcloud auth application-default login

# Build and run
docker build -t history-agent .

docker run --rm \
  -p 8080:8080 \
  -e GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID \
  -e GOOGLE_CLOUD_LOCATION=us-central1 \
  -v ~/.config/gcloud:/root/.config/gcloud \
  history-agent
```

Open `http://localhost:8080/dev-ui/` in your browser.

## Deploying to Cloud Run
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/history-agent .

gcloud run deploy history-agent \
  --image=gcr.io/YOUR_PROJECT_ID/history-agent \
  --region=us-central1 \
  --allow-unauthenticated \
  --port=8080 \
  --memory=512Mi
```

## Example queries

- "What happened on July 20th?"
- "Tell me about March 15th"
- "What major events occurred on November 9th?"
- "Today in history"