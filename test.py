"""A simple example demonstrating text completion without using streams."""

import asyncio

import xai_sdk


async def main():
    """Runs the example."""
    client = xai_sdk.Client()

    conversation = client.chat.create_conversation()

    print("Enter an empty message to quit.\n")

    while True:
        user_input = input("Human: ")
        print("")

        if not user_input:
            return

        response = await conversation.add_response_no_stream(user_input)
        print(f"Grok: {response.message}\n")


asyncio.run(main())