import xai_sdk

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
    response = ""

    async for token in client.sampler.sample(prompt="", inputs=(query,), max_len=2000):
        response += (token.token_str)
    return response