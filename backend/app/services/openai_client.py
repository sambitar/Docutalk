from openai import AsyncOpenAI


def make_openai_client(api_key: str) -> AsyncOpenAI:
    return AsyncOpenAI(api_key=api_key)


async def validate_openai_key(api_key: str) -> None:
    client = make_openai_client(api_key)
    await client.models.list()


async def embed_texts(api_key: str, texts: list[str], model: str) -> list[list[float]]:
    if not texts:
        return []
    client = make_openai_client(api_key)
    # Batch in chunks of 100
    vectors: list[list[float]] = []
    batch_size = 100
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        resp = await client.embeddings.create(model=model, input=batch)
        ordered = sorted(resp.data, key=lambda d: d.index)
        vectors.extend([list(item.embedding) for item in ordered])
    return vectors


async def chat_completion(api_key: str, model: str, system: str, user: str) -> str:
    client = make_openai_client(api_key)
    resp = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content or ""
