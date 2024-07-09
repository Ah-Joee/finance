import xai_sdk
import sys

async def grok(query):
    """
    Returns the response and the conversation from Grok. 
    If there's an existing conversation, continue it.
    Otherwise create a conversation.

    Args:
        query (str): question passed into the Grok
        conversation (tuple[AsyncGenerator[str, None], Future[StatelessResponse]]):
            A tuple of the form `token_strem, response` where `token_stream` is an async
            iterable that emits the individual string tokens of the newly sampled reseponse and
            `response` is a future that resolves to the Rsponse object created. 
    """
    client = xai_sdk.Client()
    conversation = client.grok.create_conversation()
    token_stream, _ = conversation.add_response(query)
    response = ""


    print('\n<<< Grok >>>\n')
    async for token in token_stream:
        print(token, end="")
        response += token
        sys.stdout.flush()

    return response