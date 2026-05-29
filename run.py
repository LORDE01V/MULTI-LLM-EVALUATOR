"""Run from the project root: python run.py"""
import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from src.main import main

if __name__ == "__main__":
    asyncio.run(main())
