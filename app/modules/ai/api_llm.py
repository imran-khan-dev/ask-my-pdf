from openai import OpenAI

from app.core.config import (
    OPENAI_API_KEY,
    OPENAI_LLM_MODEL,
)


client = OpenAI(api_key=OPENAI_API_KEY)


def generate_answer(
    question: str,
    context: str,
) -> str:

    prompt = f"""
You are a helpful document question-answering assistant.

Answer the user's question using ONLY the information
provided in the context.

Rules:
1. Do not use outside knowledge.
2. Do not invent or assume information.
3. Give a natural, conversational answer.
4. Keep the answer concise.
5. If the context does not contain enough information,
   respond exactly:

"I couldn't find the answer in the document."

Context:
{context}

Question:
{question}
"""

    response = client.chat.completions.create(
        model=OPENAI_LLM_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response.choices[0].message.content