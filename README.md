# OmniEval: Multi-Provider LLM Benchmarking Framework

OmniEval is an asynchronous framework designed to automate prompt execution and evaluation across multiple LLM providers. The application wraps endpoints from OpenAI, Google (Gemini), and Groq through standardized, OpenAI-compatible APIs. It processes inputs concurrently to benchmark responses simultaneously and uses a centralized evaluation model to programmatically rank outputs.

## Architecture and Engineering Choices

* **Asynchronous Concurrency:** Utilizes Python's `asyncio` architecture and thread pool executors to handle real-time network inputs concurrently, mitigating I/O-bound delay overhead.
* **API Standardization:** Abstracts configuration parameters and interface signatures across distinct host platforms using uniform OpenAI client interfaces.
* **Deterministic Structured Data Output:** Configures model routing parameters to return JSON object payloads exclusively, ensuring predictable validation parsing.
* **Decoupled Module Strategy:** Isolates runtime environmental validations and functional tasks to simplify integration and scaling modifications.

## Process Workflow

1. **Prompt Generation:** A meta-prompt engine dynamically generates a nuanced, high-complexity logical question through a primary cloud model.
2. **Parallel Dispatch:** The core orchestration module concurrently serves the generated challenge prompt to all active model targets in the registry.
3. **Structured Review Evaluation:** Response arrays are consolidated and evaluated by a parsing agent, which generates an indexed ranking output in a structured JSON schema.

## Installation and Execution

1. Clone the repository and install dependencies:
   ```bash
   https://github.com/LORDE01V/MULTI-LLM-EVALUATOR.git
   cd multi-llm-evaluator
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and set your real API keys.

3. From the **project root** (not the `src` folder), run:
   ```bash
   python run.py
   ```