from config import AVG_TOKENS_PER_REQUEST, MODEL_COST_PER_1M_TOKENS


class Analytics:
    def __init__(self):
        self.reset()

    def reset(self):
        self.total_requests = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_latency = 0
        self.cached_tokens = 0

    def record_hit(self, latency_ms, tokens_saved):
        self.total_requests += 1
        self.cache_hits += 1
        self.total_latency += latency_ms
        self.cached_tokens += tokens_saved

    def record_miss(self, latency_ms):
        self.total_requests += 1
        self.cache_misses += 1
        self.total_latency += latency_ms

    def report(self):
        hit_rate = (
            self.cache_hits / self.total_requests
            if self.total_requests else 0
        )

        total_tokens = self.total_requests * AVG_TOKENS_PER_REQUEST
        baseline_cost = (total_tokens / 1_000_000) * MODEL_COST_PER_1M_TOKENS

        savings = (self.cached_tokens / 1_000_000) * MODEL_COST_PER_1M_TOKENS
        savings_percent = (
            (savings / baseline_cost) * 100 if baseline_cost > 0 else 0
        )

        avg_latency = (
            int(self.total_latency / self.total_requests)
            if self.total_requests else 0
        )

        return {
            "hitRate": round(hit_rate, 4),
            "totalRequests": self.total_requests,
            "cacheHits": self.cache_hits,
            "cacheMisses": self.cache_misses,
            "costSavings": round(savings, 4),
            "savingsPercent": round(savings_percent, 2),
            "avgLatency": avg_latency
        }


analytics = Analytics()
