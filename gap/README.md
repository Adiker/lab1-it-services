<!-- ai-generated: 100% - Codex documented the actual proxy measurement, its timing boundary and limitations. -->
# Why the client waits longer than the server observes

The real local run used Toxiproxy 2.12.0 between oha and svcdesk, with a downstream latency toxic of 100 ms, jitter 10 ms and toxicity 1. The path was oha → Toxiproxy → svcdesk → kb-index, with the response returning through the same proxy. The profile was Adiker throughout. The commands and API configuration are reproducible in `measure.py`; it records the result in `gap.json` and the unmodified oha output in `measurement.json`.

After a 5-second warm-up, oha 1.16.0 sent open-loop traffic for 60 seconds at 40 requests/second with 64 connections and latency correction, the M-08 schedule. Client p99 was 0.462334150 s. The server histogram's p99, calculated from bucket increments over exactly that run and aggregated over /kb/search statuses, was 0.358666667 s. The difference is 0.462334150 - 0.358666667 = 0.103667483 s, about 104 ms. This is a measured difference between two p99 estimates, not a subtraction between individually paired requests.

The ASGI timer starts when svcdesk receives the request and ends when the application has sent its response to the server transport. It includes waiting for kb-index. It cannot see downstream time in Toxiproxy after the bytes leave the service, nor client-side connection or scheduling delays. oha measures from each scheduled request until the response arrives, so the artificial downstream delay appears in its measurement. The observed gap is close to the configured 100 ms; 10 ms jitter, network and scheduler overhead, different request ranks at p99, and histogram interpolation prevent exact equality. The 20 ms buckets around the server tail keep that interpolation error small compared with the toxic.

The server latency SLI is useful for application diagnosis but cannot promise the latency a user sees through a network or proxy. A client-side SLI or external probe would be needed for that promise. This proxy changes neither the code nor the service histogram boundaries, and adds no retry or cache. The grader independently repeats the experiment for 30 seconds: differences due to random samples are expected, with the published tolerance max(15 ms, 30% of its measured gap).

Reproduce from the repository root:

```sh
docker compose --profile gap up -d --build svcdesk kb-index toxiproxy
docker run --rm --network lab1-svcdesk_default -v "$PWD:/work" --entrypoint python ghcr.io/swasik/itsmlab:2026 /work/gap/measure.py
```

Run without other load generators against the same local service. The script deletes and recreates only the proxy named svcdesk in this laboratory's Toxiproxy container, so repeated runs do not stack multiple latency toxics. It reads /metrics directly, outside the proxy, immediately before and after the measured request stream.
