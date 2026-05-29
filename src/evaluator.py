import os
import json
import asyncio
import logging
from openai import OpenAI
from src.config import MODEL_REGISTRY, get_gemini_api_key

class MultiLLMEvaluator:
    def __init__(self):
        self.main_client = OpenAI()
        self.responses = {}

    def generate_benchmark_question(self) -> str:
        prompt = (
            "Please come up with a challenging, nuanced logic or ethical question "
            "that I can ask a number of LLMs to evaluate their intelligence. "
            "Answer only with the question, no explanation."
        )
        try:
            response = self.main_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as error:
            logging.warning(f"Failed to generate challenge prompt: {error}. Using fallback.")
            return "If a predictive AI perfectly anticipates a human choice, where does the moral liability reside?"

    async def fetch_single_response(self, model_id: str, config: dict, question: str):
        messages = [{"role": "user", "content": question}]
        loop = asyncio.get_event_loop()
        
        if config["provider"] == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
        elif config["provider"] == "google":
            api_key = get_gemini_api_key()
        elif config["provider"] == "groq":
            api_key = os.getenv("GROQ_API_KEY")

        client = OpenAI(api_key=api_key, base_url=config["base_url"])

        try:
            def call_api():
                return client.chat.completions.create(model=model_id, messages=messages)
                
            response = await loop.run_in_executor(None, call_api)
            self.responses[model_id] = response.choices[0].message.content
            logging.info(f"Successfully retrieved response from {config['display_name']}")
            
        except Exception as error:
            logging.error(f"API call failed for {config['display_name']}: {error}")
            self.responses[model_id] = f"Error: Generation failed: {error}"

    async def execute_parallel_benchmark(self, question: str):
        tasks = [
            self.fetch_single_response(model, config, question) 
            for model, config in MODEL_REGISTRY.items()
        ]
        await asyncio.gather(*tasks)

    def judge_and_rank(self, question: str) -> list:
        compiled_data = ""
        index_map = {}
        
        for index, (model_id, answer) in enumerate(self.responses.items(), 1):
            compiled_data += f"### Competitor ID: {index} ({MODEL_REGISTRY[model_id]['display_name']})\n"
            compiled_data += f"{answer}\n\n---\n\n"
            index_map[str(index)] = model_id

        judge_prompt = f"""You are an elite AI evaluator. Your job is to judge an LLM responses contest.
The models were given the following prompt:
"{question}"

Carefully read their responses below. Rank them from best to worst based on depth, accuracy, logic, and nuance.
You must return your ranking strictly inside a valid JSON format. Do not use code blocks, markdown wrappers, or explanations.

Target Schema:
{{"results": ["1", "2", "3"]}}

Data to evaluate:
{compiled_data}"""

        try:
            response = self.main_client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                messages=[{"role": "user", "content": judge_prompt}]
            )
            
            raw_json = json.loads(response.choices[0].message.content)
            rank_indices = raw_json.get("results", [])
            
            return [index_map[str(idx)] for idx in rank_indices if str(idx) in index_map]
            
        except Exception as error:
            logging.error(f"Judging processing failure: {error}")
            return list(self.responses.keys())