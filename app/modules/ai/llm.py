from app.core.config import AI_PROVIDER

from app.modules.ai.local_llm import (
    generate_answer as generate_local_answer,
)

from app.modules.ai.api_llm import (
    generate_answer as generate_api_answer,
)


def generate_answer(
    question: str,
    context: str,
) -> str:

    if AI_PROVIDER == "local":
        return generate_local_answer(
            question,
            context,
        )

    if AI_PROVIDER == "api":
        return generate_api_answer(
            question,
            context,
        )

    raise ValueError(
        f"Unsupported AI provider: {AI_PROVIDER}"
    )