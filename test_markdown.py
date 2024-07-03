from langchain.text_splitter import MarkdownTextSplitter
from langchain_community.document_loaders import (
    TextLoader,
    DirectoryLoader,
    UnstructuredMarkdownLoader,
)
from typing import Callable
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores.chroma import Chroma
import time


def benchmark(fn: Callable, *args):
    t1 = time.time()
    val = fn(*args)
    t2 = time.time()

    print(f"{fn.__name__} took {t2 - t1} seconds to run")

    return val


def load_markdown():
    loader = DirectoryLoader(
        path="md", loader_cls=UnstructuredMarkdownLoader, show_progress=True
    )
    docs = loader.load()
    return docs


def split_markdown(documents):
    splitter = MarkdownTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    split_docs = splitter.split_documents(documents)
    return split_docs


def create_vector_store():
    embedding_fn = HuggingFaceEmbeddings()
    vector_store = Chroma(
        persist_directory="db",
        collection_name="markdown",
        embedding_function=embedding_fn
    )

    return vector_store


def initialize_vector_store(vector_store: Chroma):
    if len(vector_store) == 0:
        docs = load_markdown()
        split_docs = benchmark(split_markdown, docs)
        benchmark(vector_store.add_documents, split_docs)


def main():
    vector_store = benchmark(create_vector_store)
    benchmark(initialize_vector_store, vector_store)

    def search(query: str):
        return vector_store.similarity_search_with_relevance_scores(query, k=3)

    while True:
        q = input("> ")

        if q == "q":
            print("Bye")
            break

        print("performing query")

        docs = benchmark(search, q)
        for doc in docs:
            print(doc)


if __name__ == '__main__':
    main()
