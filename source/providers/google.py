import os
import time
import json
import random
from typing import Any, Type
from google import genai
from google.genai import types
from pydantic import BaseModel

import config

client = genai.Client(api_key=config.API_KEY) if config.API_KEY else None

def record_usage(tokens: int, calls: int = 1):
    usage = {"tokens": 0, "calls": 0}
    if os.path.exists(config.USAGE_FILE):
        try:
            with open(config.USAGE_FILE, 'r', encoding='utf-8') as f:
                usage = json.load(f)
        except Exception:
            pass
    
    usage['tokens'] += tokens
    usage['calls'] += calls
    
    if usage['calls'] >= config.WARNING_QUOTA:
        print(f"WARNING: Daily API call quota is nearing its limit: {usage['calls']}/{config.DAILY_QUOTA}")
        
    with open(config.USAGE_FILE, 'w', encoding='utf-8') as f:
        json.dump(usage, f, indent=2)

def generate_structured(
    prompt: str, 
    image_bytes: bytes, 
    response_schema: Type[BaseModel],
    use_fallback: bool = False,
    task_name: str = "general"
) -> BaseModel:
    if not client:
        raise ValueError("API Key not found or client not initialized.")
        
    model = config.FALLBACK_MODEL if use_fallback else config.MODEL_NAME
    
    # Check cache first
    from source import cache
    cache_key = cache.get_cache_key(image_bytes or b'', prompt, model, task_name)
    cached_data = cache.read_cache(cache_key)
    if cached_data:
        return response_schema.model_validate(cached_data)
    
    # 2 retries on 429/5xx
    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            time.sleep(config.RATE_LIMIT_DELAY) # Rate limit: 12 req/min
            
            contents = [prompt]
            if image_bytes:
                contents.append(
                    types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg')
                )
                
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=response_schema,
                    temperature=0.0,
                    seed=42
                )
            )
            
            # Record tokens
            tokens = 0
            if response.usage_metadata:
                tokens = response.usage_metadata.total_token_count
            record_usage(tokens=tokens)
            
            parsed = response_schema.model_validate_json(response.text)
            
            # Write to cache
            cache.write_cache(cache_key, parsed.model_dump(mode='json'))
            
            return parsed
            
        except Exception as e:
            err_str = str(e).lower()
            if "429" in err_str or "500" in err_str or "503" in err_str:
                if attempt < max_retries:
                    delay = (2 ** attempt) + random.uniform(0, 1)
                    print(f"API Error (rate limit/server). Retrying in {delay:.1f}s...")
                    time.sleep(delay)
                    continue
            if not use_fallback and attempt == max_retries:
                print("Primary model failed, trying fallback...")
                return generate_structured(prompt, image_bytes, response_schema, use_fallback=True, task_name=task_name)
            raise e
