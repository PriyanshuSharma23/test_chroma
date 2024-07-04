import os

import openai
from openai import AsyncOpenAI
import sqlite3
import asyncio

from helper import pretty_print, pretty_print_json
from typing import List

openai.api_key = os.environ.get('OPENAI_API_KEY')

conn = sqlite3.connect("db")

# Create the necessary tables if they don't exist
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS vector_stores (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS assistants (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS threads (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL
)
''')
conn.commit()


async def create_vector_store(client: AsyncOpenAI, name = "test-db"):
    vector_store = await client.beta.vector_stores.create(
        name=name
    )

    cur = conn.cursor()
    cur.execute("INSERT INTO vector_stores VALUES (?, ?)", (vector_store.id, vector_store.name))
    conn.commit()


async def create_thread(client: AsyncOpenAI, name: str):
    thread = await client.beta.threads.create(
        metadata={"name": name}
    )

    cur = conn.cursor()
    cur.execute("INSERT INTO threads VALUES (?, ?)", (thread.id, thread.metadata['name']))
    conn.commit()


async def create_assistant(client: AsyncOpenAI, name: str = "test_bot", description: str = "You are an animal enthusiast. Use your knowledge to answer questions related to animals.", model: str = "gpt-4o"):

    assistant = await client.beta.assistants.create(
        name=name,
        description=description,
        model=model,
        tools=[{"type": "file_search"}]
    )

    cur = conn.cursor()
    cur.execute("INSERT INTO assistants VALUES (?, ?)", (assistant.id, assistant.name))
    conn.commit()


async def create_message(client: AsyncOpenAI, thread_id: str, message: str):
    return await client.beta.threads.messages.create(
        thread_id=thread_id,
        content=message,
        role="user"
    )


async def get_vector_store(vector_store_id: str, client: AsyncOpenAI):
    return await client.beta.vector_stores.retrieve(vector_store_id)


async def get_assistant(id: str, client: AsyncOpenAI):
    return await client.beta.assistants.retrieve(assistant_id=id)


async def get_thread(thread_id: str, client: AsyncOpenAI):
    return await client.beta.threads.retrieve(thread_id=thread_id)


async def get_thread_messages(client: AsyncOpenAI, thread_id: str):
    resp = await client.beta.threads.messages.list(
        thread_id=thread_id,
    )
    return resp.data


async def update_assistant(client: AsyncOpenAI, assistant_id: str, vector_store_id: str):
    assistant = await client.beta.assistants.update(
        assistant_id=assistant_id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
    )
    return assistant


async def add_files_to_vector_store(client: AsyncOpenAI, vector_store_id, files: List[str]):
    file_streams = [open(path, "rb") for path in files]
    return await client.beta.vector_stores.file_batches.upload_and_poll(
        files=file_streams,
        vector_store_id=vector_store_id
    )


def get_created_assistants():
    cur = conn.cursor()
    cur.execute("SELECT * FROM assistants")
    return cur.fetchall()


def get_created_vector_stores():
    cur = conn.cursor()
    cur.execute("SELECT * FROM vector_stores")
    return cur.fetchall()


def get_created_threads():
    cur = conn.cursor()
    cur.execute("SELECT * FROM threads")
    return cur.fetchall()


async def select_assistant(client):
    print("Created Assistants: ")
    assistants = get_created_assistants()
    for idx, assistant in enumerate(assistants):
        print(f"{idx + 1}. {assistant[1]}")

    assistant_choice = input("Do you want to create a new assistant? (y/N): ").strip().lower()
    if assistant_choice == 'y':
        name = input("Enter assistant name: ").strip()
        description = input("Enter assistant description: ").strip()
        model = input("Enter assistant model: ").strip()
        await create_assistant(client, name, description, model)
        await select_assistant(client)
    else:
        try:
            n = int(input("Choose an assistant (1-N): "))
            if 1 <= n <= len(assistants):
                chosen_assistant = assistants[n - 1]
                assistant_details = await get_assistant(chosen_assistant[0], client)
                print("Chosen Assistant Details:")
                pretty_print_json(assistant_details.json())
                return assistant_details
            else:
                print("Invalid choice")
                await select_assistant(client)
        except ValueError:
            print("Please enter a valid number")
            await select_assistant(client)


async def select_vector_store(client):
    print("Created Vector Stores: ")
    vector_stores = get_created_vector_stores()
    for idx, store in enumerate(vector_stores):
        print(f"{idx + 1}. {store[1]}")

    store_choice = input("Do you want to create a new vector store? (y/N): ").strip().lower()
    if store_choice == 'y':
        name = input("Enter vector store name: ").strip()
        await create_vector_store(client, name)
        await select_vector_store(client)
    else:
        try:
            n = int(input("Choose a vector store (1-N): "))
            if 1 <= n <= len(vector_stores):
                chosen_vector_store = vector_stores[n - 1]
                vector_store_details = await get_vector_store(chosen_vector_store[0], client)
                print("Chosen Vector Store Details:")
                pretty_print_json(vector_store_details.json())
                return vector_store_details
            else:
                print("Invalid choice")
                await select_vector_store(client)
        except ValueError:
            print("Please enter a valid number")
            await select_vector_store(client)


async def select_thread(client):
    print("Created Threads: ")
    threads = get_created_threads()
    for idx, thread in enumerate(threads):
        print(f"{idx + 1}. {thread[1]}")

    thread_choice = input("Do you want to create a new thread? (y/N): ").strip().lower()
    if thread_choice == 'y':
        name = input("Enter thread name: ").strip()
        await (create_thread(client, name))
        await select_thread(client)
    else:
        try:
            n = int(input("Choose a thread (1-N): "))
            if 1 <= n <= len(threads):
                chosen_thread = threads[n - 1]
                thread = await get_thread(chosen_thread[0], client)
                pretty_print_json(thread.json())
                return thread
            else:
                print("Invalid choice")
                await select_thread(client)
        except ValueError:
            print("Please enter a valid number")
            await select_thread(client)


def get_files_input():
    paths = input("Input file paths you want to add (comma separated): ")
    files = list(map(lambda x: x.strip(), paths.split(",")))

    if not files:
        print("Please enter atleast one file path")
        get_files_input()
    else:
        return files


async def add_file_to_vector_store(client):
    vector_store = await select_vector_store(client)
    files = get_files_input()

    batch = await add_files_to_vector_store(client, vector_store.id, files)
    print(f"Successfully added files to the vector store {vector_store.name}")
    print(batch)


async def update_assistant_cli(client):
    assistant = await select_assistant(client)
    vector_store = await select_vector_store(client)

    updated_assistant = await update_assistant(client, assistant.id, vector_store.id)
    print("Assistant updated:\n", pretty_print_json(updated_assistant.json()))


def print_messages(messages):
    for message in messages:
        print(f"{message.role}>", message.content[0].text.value)
        if message.content[0].text.annotations:
            print("Annotations: ")
            for i, annotation in enumerate(message.content[0].text.annotations):
                print(1 + i, annotation)


def get_user_message():
    text = input("user> ").strip()
    if not text:
        print("Message cannot be empty")
        get_user_message()

    return text


async def chat_session(client: AsyncOpenAI, thread_id, assistant_id):
    content = get_user_message()
    await create_message(client, thread_id, content)

    run = await client.beta.threads.runs.create_and_poll(
        thread_id=thread_id, assistant_id=assistant_id
    )

    messages = await client.beta.threads.messages.list(thread_id=thread_id, run_id=run.id)
    print_messages(messages.data)

    await chat_session(client, thread_id, assistant_id)


async def handle_chat(client: AsyncOpenAI):
    print("Choose an assistant for chat")
    assistant = await select_assistant(client)

    print("Choose a thread for chat")
    thread = await select_thread(client)

    messages = await get_thread_messages(client, thread.id)
    print_messages(reversed(messages))

    await chat_session(client, thread.id, assistant.id)


async def main():
    client = AsyncOpenAI(api_key=openai.api_key)

    options = [
        "Add files to vector store",
        "Add vector store to assistant",
        "Manage assistant",
        "Manage vector store",
        "Manage thread",
        "Message on thread"
    ]

    print("Welcome to OpenAI assistant test")
    for i, option in enumerate(options):
        print(f"{i + 1}. {option}")

    n = int(input(f"Choose one (1-{len(options)}): "))

    if n == 1:
        await add_file_to_vector_store(client)
    elif n == 2:
        await update_assistant_cli(client)
    elif n == 3:
        await select_assistant(client)
    elif n == 4:
        await select_vector_store(client)
    elif n == 5:
        await select_thread(client)
    elif n == 6:
        await handle_chat(client)
    else:
        print("Invalid option")

    await main()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

