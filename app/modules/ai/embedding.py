from app.core.config import AI_PROVIDER

from app.modules.ai.local_embedding import (
    generate_embedding as generate_local_embedding,
)

from app.modules.ai.api_embedding import (
    generate_embedding as generate_api_embedding,
)

def generate_embedding(text: str) -> list[float]:

    if AI_PROVIDER == "local":
        return generate_local_embedding(text)

    if AI_PROVIDER == "api":
        return generate_api_embedding(text)

    raise ValueError(
        f"Unsupported AI provider: {AI_PROVIDER}"
    )