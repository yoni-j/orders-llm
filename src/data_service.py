import os

import redis
from typing import List
import json


REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True)


class DataService:
    @staticmethod
    def update_data(key: str, new_data: List[tuple]):
        r.set(key, json.dumps(new_data, ensure_ascii=False))

    @staticmethod
    def get_data(key) -> str:
        return r.get(key) or '[]'

    @staticmethod
    def format_history(history: list[list]):
        return [tuple(item) for item in history]