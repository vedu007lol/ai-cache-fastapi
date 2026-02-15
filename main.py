import time
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from cache import cache
from analytics import analytics
from config import AVG_TOKENS_PER_REQUEST
from embeddings import embed

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    application: str


@app.post("/")
def query_ai(req: QueryRequest):
    start = time.perf_counter()

    normalized = cache.normalize(req.query)

    # EXACT MATCH
    exact = cache.get_exact(normalized)
    if exact:
        latency = max(1, int((time.perf_counter() - start) * 1000))
        analytics.record_hit(latency, AVG_TOKENS_PER_REQUEST)
        return {
            "answer": exact,
            "cached": True,
            "latency": latency,
            "cacheKey": "exact"
        }

    # SEMANTIC MATCH
    query_embedding = embed(normalized)
    semantic = cache.get_semantic(query_embedding)
    if semantic:
        latency = max(1, int((time.perf_counter() - start) * 1000))
        analytics.record_hit(latency, AVG_TOKENS_PER_REQUEST)
        return {
            "answer": semantic,
            "cached": True,
            "latency": latency,
            "cacheKey": "semantic"
        }

    # MISS → Simulated realistic LLM latency
    time.sleep(1.2)   # IMPORTANT: force slow miss
    answer = f"Content moderation result for: {req.query}"

    cache.set(normalized, answer)

    latency = max(1, int((time.perf_counter() - start) * 1000))
    analytics.record_miss(latency)

    return {
        "answer": answer,
        "cached": False,
        "latency": latency,
        "cacheKey": None
    }


@app.get("/analytics")
def get_analytics():
    report = analytics.report()
    report["cacheSize"] = len(cache.store)
    report["strategies"] = [
        "exact match caching",
        "semantic similarity caching",
        "LRU eviction",
        "TTL expiration"
    ]
    return report


@app.post("/reset")
def reset_cache():
    cache.store.clear()
    analytics.reset()
    return {"status": "reset"}
