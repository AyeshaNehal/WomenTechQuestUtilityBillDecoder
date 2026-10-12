import json
import hashlib
import os
import config

def get_cache_key(image_bytes: bytes, prompt: str, model: str, task: str) -> str:
    h = hashlib.sha256()
    h.update(image_bytes)
    if task.startswith('explain'):
        h.update(prompt.encode('utf-8'))
    h.update(model.encode('utf-8'))
    h.update(task.encode('utf-8'))
    return h.hexdigest()

def read_cache(key: str):
    path = os.path.join(config.CACHE_DIR, f"{key}.json")
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def write_cache(key: str, data: dict):
    path = os.path.join(config.CACHE_DIR, f"{key}.json")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def clear_cache():
    for f in os.listdir(config.CACHE_DIR):
        if f.endswith('.json'):
            os.remove(os.path.join(config.CACHE_DIR, f))
