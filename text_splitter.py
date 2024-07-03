from langchain_community.vectorstores.chroma import Chroma
from typing import Union
from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
import time
import os


vector_store: Union[Chroma, None] = None


def load_doc():
    global vector_store

    if os.path.isdir("db"):
        print("db already exists")
        return

    else:
        print("chunking content")
        with open("openai.txt") as f:
            content = f.read()
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=100,
                chunk_overlap=20,
                length_function=len,
                is_separator_regex=False,
            )

            chunks = splitter.create_documents([content])

            for i, chunk in enumerate(chunks):
                chunk.id = f"Document 1 - Chunk {i + 1}"
                chunk.metadata["documentId"] = 1

        print("insert chunks")

        embedding_fn = HuggingFaceEmbeddings()
        vector_store = Chroma(
            embedding_function=embedding_fn,
            persist_directory="db",
            collection_name="splittext",
        )

        ids = vector_store.add_documents(chunks)
        print("Added documents:", *ids)


def initialize():
    global vector_store

    load_doc()
    embedding_fn = HuggingFaceEmbeddings()

    if not vector_store:
        vector_store = Chroma(
            embedding_function=embedding_fn,
            persist_directory="db",
            collection_name="splittext",
        )

    print("loaded model")


def benchmark(fn):
    t1 = time.time()
    val = fn()
    t2 = time.time()

    print(f"{t2 - t1} seconds to run")

    return val


benchmark(initialize)
print(len(vector_store))


def search(q):
    global vector_store
    return vector_store.similarity_search_with_relevance_scores(q, k=3)


while True:
    q = input("> ")

    if q == "q":
        print("Bye")
        break

    print("performing query")

    docs = benchmark(lambda: search(q))
    for doc in docs:
        print(doc)


