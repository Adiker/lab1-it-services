---
lab3_genai_diff:
  instrumentation: opentelemetry-instrumentation-genai-openai 1.2b0
  spec_ref: semantic-conventions-genai@e57c543b4889619eb2a05702471937db5119165d
  attributes:
  - name: gen_ai.operation.name
    emitted: true
    in_spec: true
    stability: development
  - name: gen_ai.provider.name
    emitted: true
    in_spec: true
    stability: development
  - name: gen_ai.request.max_tokens
    emitted: true
    in_spec: true
    stability: development
  - name: gen_ai.request.model
    emitted: true
    in_spec: true
    stability: development
  - name: gen_ai.request.temperature
    emitted: true
    in_spec: true
    stability: development
  - name: gen_ai.request.top_p
    emitted: false
    in_spec: true
    stability: development
  - name: gen_ai.response.finish_reasons
    emitted: true
    in_spec: true
    stability: development
  - name: gen_ai.response.id
    emitted: true
    in_spec: true
    stability: development
  - name: gen_ai.response.model
    emitted: true
    in_spec: true
    stability: development
  - name: gen_ai.usage.input_tokens
    emitted: true
    in_spec: true
    stability: development
  - name: gen_ai.usage.output_tokens
    emitted: true
    in_spec: true
    stability: development
---
<!-- ai-generated: 100% - Codex compared the library export with the pinned upstream attribute registry. -->
# GenAI instrumentation against the pinned registry

This is a real local inference through Ollama's OpenAI-compatible endpoint, using qwen3:0.6b. `capture.py` makes one chat completion with the official OpenAI instrumentation 1.2b0 and exports its SDK span with FileSpanExporter. No span or token count was constructed by hand. The completion reached its configured 80-token limit (`finish_reasons: length`); inference succeeded, but the model used the budget on reasoning and returned no visible answer. This evidence demonstrates instrumentation, not answer quality. The prompt and response content are not captured. The file contains no API credential; the client uses the local-only placeholder `local-ollama`.

All ten emitted gen_ai keys exist in the pinned registry and have stability development. The exact attribute set is in the front matter, including a negative control: request.top_p exists in the spec but was not sent in this call and was not emitted. The library adds other useful fields, including server.address, server.port and openai.response.system_fingerprint; those are not gen_ai keys and are outside the compared set. A matching library is a valid result: this export shows no renamed or out-of-spec gen_ai key against this snapshot.

The provider name is openai because that is the protocol and client instrumentation being used; the actual model runs locally in Ollama. It does not establish a call to the OpenAI hosted service. Likewise, the scope's schemaUrl is 1.37.0; this is metadata emitted by the library, not a replacement for the explicit specification reference used in the comparison.

The comparison uses the [attribute registry at the course-pinned commit](https://github.com/open-telemetry/semantic-conventions-genai/blob/e57c543b4889619eb2a05702471937db5119165d/model/gen-ai/registry.yaml), not today's moving main branch. All stability claims come from its top-level attribute definitions.

To reproduce, run an Ollama server on localhost:21434 with qwen3:0.6b installed, install `genai/requirements.txt` in a virtual environment, then run `python genai/capture.py`. The measurement server was stopped afterwards to avoid competing with HTTP latency measurements. A fresh capture replaces spans.json; its trace IDs, timings and possibly token counts will differ.
