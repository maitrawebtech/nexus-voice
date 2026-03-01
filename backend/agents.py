import vertexai
from vertexai.generative_models import GenerativeModel, Part, Content
import os
import json
import schemas
from pydantic import BaseModel

# Initialize Vertex AI. This uses Application Default Credentials.
# Ensure GOOGLE_APPLICATION_CREDENTIALS points to a valid service account JSON.
project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "YOUR_PROJECT_ID")
location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

try:
    vertexai.init(project=project_id, location=location)
    # Using gemini-1.5-pro-preview-0409 as a placeholder for Gemini 3.1 Pro as specified
    MODEL_NAME = "gemini-1.5-pro-preview-0409" # Replace with 'gemini-3.1-pro' when available
    model = GenerativeModel(MODEL_NAME)
except Exception as e:
    print(f"Error initializing Vertex AI: {e}")
    # mock model for dev if no credentials
    model = None

# --- Common Prompts ---
ANALYST_SYSTEM_PROMPT = """
You are "The Analyst," an elite technical editor. Your job is to ingest dense, unstructured technical transcripts or blogs and distil them into raw, high-value components. 
1. Identify and state "The Big Idea" (max 3 sentences).
2. Extract 5 "Atomic Hooks"—compelling, counter-intuitive, or highly valuable points that grab attention. 
Your output MUST strictly follow the provided JSON schema. Do not change the brand voice; remain objective and analytical.
"""

async def run_analyst(text_content: str) -> dict:
    """
    Ingests raw text and returns The Big Idea and Atomic Hooks.
    """
    if not model:
        # Return mock data if model isn't initialized
        return {
            "big_idea": "Mock Big Idea: AI is revolutionizing content generation.",
            "atomic_hooks": [
                {"hook": "Mock Hook 1: 10x ROI on AI agents."},
                {"hook": "Mock Hook 2: Automation is key."},
                {"hook": "Mock Hook 3: Human-in-the-loop is mandatory."},
                {"hook": "Mock Hook 4: Scale quality, not just quantity."},
                {"hook": "Mock Hook 5: The future is autonomous."}
            ]
        }
        
    prompt = f"{ANALYST_SYSTEM_PROMPT}\n\nRaw Text:\n{text_content}"
    
    # Let's enforce the JSON structure using responseSchema
    response = model.generate_content(
        contents=[Content(role="user", parts=[Part.from_text(prompt)])],
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": schemas.AnalystOutput.model_json_schema()
        }
    )
    
    try:
        data = json.loads(response.text)
        # Validate through Pydantic to ensure correctness
        validated = schemas.AnalystOutput(**data)
        return validated.dict()
    except Exception as e:
        print(f"Error parsing Analyst output: {e}\nRaw output: {response.text}")
        raise ValueError("Failed to parse output into schema")

import asyncio
from typing import Type

def call_gemini(system_prompt: str, context: str, brand_voice: str, schema_cls: Type[BaseModel]):
    if not model:
        # Mocking for testing without credentials
        if schema_cls == schemas.XGBThreadOutput:
            return {"posts": [{"content": f"Mock post {i}", "visual_placeholder": None} for i in range(10)]}
        elif schema_cls == schemas.LinkedInOutput:
            return {"post_text": "Mock LinkedIn post with high value."}
        elif schema_cls == schemas.ShortsScriptOutput:
            return {"scenes": [{"timestamp_seconds": "0-10s", "visual": "mock", "audio_speech": "mock"}]}
        elif schema_cls == schemas.SubstackOutput:
            return {"introductory_synthesis": "Mock intro", "takeaways": [{"bullet_point": "mock"} for _ in range(3)]}
        elif schema_cls == dict: # Review review
            return {"feedback": "incorporate new tone"}

    prompt = f"{system_prompt}\n\nBrand Voice: {brand_voice}\n\nContext:\n{context}"
    
    gen_config = {"response_mime_type": "application/json"}
    if schema_cls != dict:
        gen_config["response_schema"] = schema_cls.model_json_schema()

    response = model.generate_content(
        contents=[Content(role="user", parts=[Part.from_text(prompt)])],
        generation_config=gen_config
    )
    
    data = json.loads(response.text)
    if schema_cls != dict:
        validated = schema_cls(**data)
        return validated.dict()
    return data

async def run_agent_x(analyst_context: dict, brand_voice: str) -> dict:
    prompt = "You are 'Agent-X', a master copywriter for X/Twitter. Write a 10-post thread based on this context. Post 1 must be a scroll-stopping hook."
    # Normally run in thread pool or use async client if available in SDK
    return await asyncio.to_thread(call_gemini, prompt, str(analyst_context), brand_voice, schemas.XGBThreadOutput)

async def run_agent_li(analyst_context: dict, brand_voice: str) -> dict:
    prompt = "You are 'Agent-LI', a top 1% B2B ghostwriter for LinkedIn. Write a 1,200 character post."
    return await asyncio.to_thread(call_gemini, prompt, str(analyst_context), brand_voice, schemas.LinkedInOutput)

async def run_agent_shorts(analyst_context: dict, brand_voice: str) -> dict:
    prompt = "You are 'Agent-Shorts', a viral video producer. Write a 60-second video script."
    return await asyncio.to_thread(call_gemini, prompt, str(analyst_context), brand_voice, schemas.ShortsScriptOutput)

async def run_agent_substack(analyst_context: dict, brand_voice: str) -> dict:
    prompt = "You are 'Agent-Substack', a premium newsletter editor. Write a structured TL;DR newsletter with 3 takeaways."
    return await asyncio.to_thread(call_gemini, prompt, str(analyst_context), brand_voice, schemas.SubstackOutput)

async def run_orchestration(text_content: str, brand_voice: str):
    analyst_context = await run_analyst(text_content)
    
    results = await asyncio.gather(
        run_agent_x(analyst_context, brand_voice),
        run_agent_li(analyst_context, brand_voice),
        run_agent_shorts(analyst_context, brand_voice),
        run_agent_substack(analyst_context, brand_voice)
    )
    
    return {
        "analyst": analyst_context,
        "agent_x": results[0],
        "agent_li": results[1],
        "agent_shorts": results[2],
        "agent_substack": results[3]
    }

async def run_reviewer_agent(reviewer_request: schemas.ReviewRequest) -> dict:
    prompt = (
        f"You are the Reviewer Agent. The user edited the output for {reviewer_request.agent_id}.\n"
        f"Original: {reviewer_request.original_output}\n"
        f"Edited: {reviewer_request.edited_output}\n\n"
        f"Extract the tonal or factual shift, and provide instructions on how to adjust the other agents to match."
    )
    feedback_payload = await asyncio.to_thread(call_gemini, prompt, str(reviewer_request.analyst_context), reviewer_request.brand_voice, dict)
    
    # After extracting feedback, we would trigger regenerations for the OTHER agents.
    # For now, return what we would have done, or regenerate if we know which one it is.
    # A full implementation would check agent_id and re-run the missing 3.
    
    return {"feedback_extracted": feedback_payload, "status": "Regenerating other agents (mock)"}


