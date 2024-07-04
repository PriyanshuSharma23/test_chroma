from langchain.text_splitter import MarkdownTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from typing import List


class VectorStore:
    def add_documents(self, documents: List[Document]):
        pass

class VectorStoreManager:
    def __init__(self, vector_store: VectorStore):
        embedding = HuggingFaceEmbeddings()
        self.db = Chroma(
            collection_name="temporary",
            embedding_function=embedding
        )

    def add_file(self, document_path: str):
        loader = TextLoader(
            file_path=document_path
        )

        docs = loader.load()
        splitter = MarkdownTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            add_start_index=True
        )

        split_doc = splitter.split_documents(docs)

        print("Length of split docs:", len(split_doc))
        return self.db.add_documents(split_doc)

    def delete_file(self, id: str):
        self.db.delete(ids=[id])

    def query(self, q: str):
        return self.db.similarity_search_with_relevance_scores(query=q, k=5)

    def __len__(self):
        return len(self.db)

