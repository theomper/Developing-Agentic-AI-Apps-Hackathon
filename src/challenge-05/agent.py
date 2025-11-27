import asyncio
import os
import sys
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

async def run_agent_conversation():
    """Run an interactive conversation with the travel policy agent."""
    print("\nHello1")
    # Consider storing secrets in an .env file and loading
    # them using python-dotenv and load_dotenv()
    # See https://pypi.org/project/python-dotenv/.
    endpoint = "https://proj-cosbew-try2-resource.services.ai.azure.com/api/projects/proj-cosbew-try2"
    agent_id = "asst_wPbk4tzgcmmvcdlHwbcRQZWl"
    print("\nHello2")
    if not endpoint or not agent_id:
        print("Error: Set AZURE_AI_FOUNDRY_PROJECT_ENDPOINT and AZURE_AI_AGENT_ID environment variables")
        sys.exit(1)
    print("\nHello3")
    project_client = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
    print("\nHello4")
    # Get agents client
    agents_client = project_client.agents
    print("\nHello5")
    # Load your agent from Azure AI Foundry
    agent = agents_client.get_agent(agent_id)
    print(f"Loaded agent: {agent.name}")
    print("\nHello6")
    # Create a new thread for conversation
    thread = agents_client.threads.create()
    print(f"Created thread: {thread.id}")
    print("\nHello7")
    # Interactive conversation loop
    print("\nTravel Policy Compliance Agent")
    print("Ask me about travel policies. Type 'exit' to quit.\n")

    while True:
        # Get user input
        user_input = input("You: ").strip()

        if user_input.lower() == 'exit':
            break

        if not user_input:
            continue

        # Send message to agent
        agents_client.messages.create(
            thread_id=thread.id,
            role="user",
            content=[{"type": "text", "text": user_input}]
        )

        # Create a run to process the message
        run = agents_client.runs.create(thread_id=thread.id, agent_id=agent_id)

        # Poll until run completes
        while run.status in ["queued", "in_progress"]:
            await asyncio.sleep(1)
            run = agents_client.runs.get(thread_id=thread.id, run_id=run.id)

        if run.status != "completed":
            print(f"Agent: Error - Run failed with status: {run.status}")
            continue

        # Get and display agent response
        messages = list(agents_client.messages.list(thread_id=thread.id))

        # Find the last assistant message
        for msg in reversed(messages):
            if msg.role == "assistant":
                for content in msg.content:
                    if hasattr(content, 'text'):
                        print(f"Agent: {content.text.value}\n")
                break

# Main execution
if __name__ == "__main__":
    asyncio.run(run_agent_conversation())