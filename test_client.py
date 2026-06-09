"""End-to-end test client for the Legal Multi-Agent System.

Sends a legal question to the Customer Agent and prints the response.
"""

import asyncio
import os
import sys

import httpx
from dotenv import load_dotenv

load_dotenv()

CUSTOMER_AGENT_URL = os.getenv("CUSTOMER_AGENT_URL", "http://localhost:10100")

QUESTION = (
    "If a company breaks a contract and avoids taxes, "
    "what are the legal and regulatory consequences?"
)


async def main() -> None:
    print(f"Connecting to Customer Agent at {CUSTOMER_AGENT_URL}")
    print(f"Question: {QUESTION}")
    print("-" * 60)

    async with httpx.AsyncClient(timeout=300.0) as http_client:
        # Resolve agent card
        card_url = f"{CUSTOMER_AGENT_URL}/.well-known/agent.json"
        try:
            card_resp = await http_client.get(card_url)
            card_resp.raise_for_status()
        except Exception as e:
            print(f"ERROR: Could not reach Customer Agent at {card_url}")
            print(f"  {e}")
            print("Make sure all services are running (./start_all.sh or .\\start_all.ps1)")
            sys.exit(1)

        from a2a.types import AgentCard, Message, Part, Role, TextPart, MessageSendParams
        from a2a.client import A2AClient
        from uuid import uuid4

        agent_card = AgentCard.model_validate(card_resp.json())
        print(f"Connected to agent: {agent_card.name} v{agent_card.version}")
        print("-" * 60)

        # Build the legacy A2AClient
        client = A2AClient(httpx_client=http_client, agent_card=agent_card)

        # Construct the message
        from a2a.types import SendMessageRequest, MessageSendParams as MSP
        message = Message(
            role=Role.user,
            parts=[Part(root=TextPart(text=QUESTION))],
            message_id=str(uuid4()),
        )
        request = SendMessageRequest(
            id=str(uuid4()),
            params=MSP(message=message),
        )

        print("Sending request (this may take 30-60s while agents chain)...\n")
        response = await client.send_message(request)

        # Parse response
        def extract_text_from_parts(parts) -> str:
            text = ""
            if not parts:
                return text
            for part in parts:
                p = part.root if hasattr(part, "root") else part
                if hasattr(p, "text") and p.text:
                    text += p.text
            return text

        result_text = ""
        task_state = None

        if hasattr(response, "root"):
            root = response.root
            if hasattr(root, "result"):
                result = root.result
                task_state = getattr(getattr(result, "status", None), "state", None)

                # Task with artifacts
                if hasattr(result, "artifacts") and result.artifacts:
                    for artifact in result.artifacts:
                        result_text += extract_text_from_parts(getattr(artifact, "parts", []))

                # Message with parts
                if not result_text and hasattr(result, "parts") and result.parts:
                    result_text += extract_text_from_parts(result.parts)

                # Failed task / status message fallback
                if not result_text and hasattr(result, "status") and result.status:
                    status_msg = getattr(result.status, "message", None)
                    if status_msg and hasattr(status_msg, "parts"):
                        result_text += extract_text_from_parts(status_msg.parts)

                # History fallback
                if not result_text and hasattr(result, "history") and result.history:
                    for msg in result.history:
                        result_text += extract_text_from_parts(getattr(msg, "parts", []))

        if result_text:
            if task_state:
                print(f"Task state: {task_state}")
            print("RESPONSE:")
            print("=" * 60)
            print(result_text)
            print("=" * 60)
        else:
            print("No text response received. Raw response:")
            print(response)


if __name__ == "__main__":
    asyncio.run(main())
