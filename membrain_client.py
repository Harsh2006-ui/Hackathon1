# membrain_client.py

import requests
import time
from config import MEMBRAIN_API_KEY, MEMBRAIN_BASE_URL

HEADERS = {
    "X-API-Key": MEMBRAIN_API_KEY,
    "Content-Type": "application/json"
}

def search_memory(query, k=5, keyword_filter=None, response_format="both"):
    url = f"{MEMBRAIN_BASE_URL}/memories/search"

    payload = {
        "query": query,
        "k": k,
        "response_format": response_format
    }

    if keyword_filter:
        payload["keyword_filter"] = keyword_filter

    try:
        res = requests.post(url, json=payload, headers=HEADERS)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        return {"error": str(e)}


def add_memory(content, tags=None, timeout=20):
    url = f"{MEMBRAIN_BASE_URL}/memories"

    payload = {
        "content": content,
        "tags": tags or []
    }

    try:
        res = requests.post(url, json=payload, headers=HEADERS)
        res.raise_for_status()

        job = res.json()
        status_url = job.get("status_url")

        start_time = time.time()

        while True:
            status_res = requests.get(status_url, headers=HEADERS)
            status_res.raise_for_status()
            status = status_res.json()

            if status["status"] == "completed":
                return status.get("result", {})

            if status["status"] == "failed":
                return {"error": "Memory failed"}

            if time.time() - start_time > timeout:
                return {"error": "Timeout"}

            time.sleep(1)

    except Exception as e:
        return {"error": str(e)}
