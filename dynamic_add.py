from langchain.text_splitter import MarkdownTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from helper import benchmark
from vector_store_manager import VectorStoreManager


def parse_query(query: str, manager: VectorStoreManager):
    cmd = query.split(' ')
    if cmd[0] == 'add':
        path = cmd[1]
        benchmark(manager.add_file, path)
    elif cmd[0] == 'delete':
        doc_id = cmd[1]
        manager.delete_file(doc_id)
    elif cmd[0] == 'Q':
        question = " ".join(cmd[1:])
        ans = manager.query(question)
        for entry in ans:
            print(entry)
    elif cmd[0] == 'count':
        print(len(manager))


manager = benchmark(VectorStoreManager)

while True:
    query = input("> ")
    parse_query(query, manager)


