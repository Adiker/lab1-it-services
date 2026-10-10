# ai-generated: 100% - Codex instrumented a real local Ollama chat completion and exported its spans.
"""Run with the packages in requirements.txt and Ollama's qwen3:0.6b model."""
import os
from pathlib import Path

from openai import OpenAI
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.json.file import FileSpanExporter
from opentelemetry.instrumentation.genai.openai import OpenAIInstrumentor

output = Path(__file__).with_name("spans.json")
output.unlink(missing_ok=True)
provider = TracerProvider(resource=Resource.create({"service.name": "svcdesk-genai-lab3"}))
provider.add_span_processor(SimpleSpanProcessor(FileSpanExporter(path=str(output))))
trace.set_tracer_provider(provider)
OpenAIInstrumentor().instrument()
client = OpenAI(base_url=os.environ.get("GENAI_BASE_URL", "http://127.0.0.1:21434/v1"), api_key="local-ollama", max_retries=0)
response = client.chat.completions.create(
    model="qwen3:0.6b",
    messages=[{"role": "user", "content": "Reply with one short sentence: what is a service-level objective? /no_think"}],
    max_tokens=80,
    temperature=0,
)
print(response.choices[0].message.content)
provider.force_flush()
provider.shutdown()
