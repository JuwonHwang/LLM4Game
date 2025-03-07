from random_agent import RandomAgentClient
from llm_agent import LLMAgentClient

import asyncio

# Function to load URL from a text file
def load_server_url(filename=".server"):
    try:
        with open(filename, "r") as file:
            return file.readline().strip()
    except FileNotFoundError:
        print("⚠ config.txt not found. Using default URL.")
        return "http://localhost:5000"

SERVER_URL = load_server_url()

async def only_random():
    agents = []
    tasks = []

    for i in range(8):
        print(f"random_agent{i+1} created")
        client = RandomAgentClient(f"random_agent{i+1}", SERVER_URL)
        agents.append(client)
        tasks.append(asyncio.create_task(client.connect_to_server()))
        await asyncio.sleep(0.1)

    await asyncio.gather(*tasks)  # Wait for all agents to complete
    print("All tasks completed.")
    return

async def single_llm():
    agents = []
    tasks = []

    for i in range(7):
        print(f"random_agent{i+1} created")
        client = RandomAgentClient(f"random_agent{i+1}", SERVER_URL)
        agents.append(client)
        tasks.append(asyncio.create_task(client.connect_to_server()))
        await asyncio.sleep(2)
    client = LLMAgentClient(f"llm_agent1", SERVER_URL)
    agents.append(client)
    tasks.append(asyncio.create_task(client.connect_to_server()))
    
    await asyncio.gather(*tasks)  # Wait for all agents to complete
    print("All tasks completed.")
    return

async def repeat(func, num):
    for i in range(num):
        print(f"Iter {i+1}")
        await func()
        await asyncio.sleep(10)
    return

# Ensure proper event loop management
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(repeat(single_llm, 6))
    print("End")