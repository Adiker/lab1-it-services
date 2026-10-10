# ai-generated: 100% - Codex implemented a single ASGI timer with bounded route labels.
"""One observation per HTTP response, including validation errors and 404s."""
from time import perf_counter

from prometheus_client import CollectorRegistry, Histogram, disable_created_metrics

disable_created_metrics()
REGISTRY = CollectorRegistry()
# Measured q=0.3534 s. Fine 20 ms buckets cover 0.28-0.46 s, including > +/-10%.
BUCKETS = (0.001, 0.0025, 0.005, 0.01, 0.02, 0.04, 0.06, 0.08, 0.1, 0.2,
           0.25, 0.28, 0.30, 0.32, 0.34, 0.36, 0.38, 0.4, 0.42, 0.44, 0.46,
           0.5, 0.75, 1, 2, 3)
DURATION = Histogram(
    "http_server_request_duration_seconds", "HTTP response duration in seconds",
    ("http_request_method", "http_route", "http_response_status_code"),
    buckets=BUCKETS, registry=REGISTRY,
)


class RequestMetrics:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["path"] == "/metrics":
            return await self.app(scope, receive, send)
        start = perf_counter()
        status = 500

        async def send_response(message):
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_response)
        finally:
            route = scope.get("route")
            template = getattr(route, "path", "unmatched")
            DURATION.labels(scope["method"], template, str(status)).observe(perf_counter() - start)
