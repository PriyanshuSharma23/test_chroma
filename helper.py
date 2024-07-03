# from chromadb import Client
# from chromadb.config import Settings


# def create_chromadb_client(persist_directory=None):
#     # settings = Settings(
#     #     chroma_db_impl="duckdb+parquet",
#     #     persist_directory=persist_directory,
#     # )
#     # client = Client(settings=settings)
#     # return client

import json
import time
from typing import Callable


def pretty_print(data):
    print(json.dumps(data, indent=2, sort_keys=True))


def benchmark(fn: Callable, *args):
    t1 = time.time()
    val = fn(*args)
    t2 = time.time()

    print(f"{fn.__name__} took {t2 - t1} seconds to run")

    return val
