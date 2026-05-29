import asyncio
import sys
import logging
import subprocess
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _run_from_project_root() -> None:
    run_script = _PROJECT_ROOT / "run.py"
    logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])
    logging.error(
        "Run this app from the project root, not from the src folder:\n"
        f"  cd {_PROJECT_ROOT}\n"
        f"  python run.py"
    )
    sys.exit(subprocess.call([sys.executable, str(run_script)], cwd=str(_PROJECT_ROOT)))


if __name__ == "__main__":
    _run_from_project_root()

from src.config import validate_environment, MODEL_REGISTRY
from src.evaluator import MultiLLMEvaluator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

async def main():
    try:
        validate_environment()
        runner = MultiLLMEvaluator()
        
        eval_question = runner.generate_benchmark_question()
        logging.info(f"Target Evaluation Prompt: {eval_question}")
        
        await runner.execute_parallel_benchmark(eval_question)
        
        leaderboard = runner.judge_and_rank(eval_question)
        
        logging.info("Final Leaderboard Rankings:")
        for position, model_id in enumerate(leaderboard, 1):
            name = MODEL_REGISTRY[model_id]['display_name']
            logging.info(f"Rank {position}: {name} ({model_id})")
            
    except Exception as exception:
        logging.error(f"Execution pipeline failed: {exception}")
        sys.exit(1)
