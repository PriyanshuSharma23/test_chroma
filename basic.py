import chromadb
import json


client = chromadb.Client()
collection = client.create_collection("my_collection")

collection.add(
    documents=[
        "This is a document about pineapple",
        "This is a document about oranges",
    ],
    ids=["id1", "id2"],
)


results = collection.query(
    query_texts=["orange query"],  # Chroma will embed this for you
    n_results=2,  # how many results to return
)
print(pretty_print(results))
