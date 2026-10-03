# from ollama import chat


# def test_llm():
#     response = chat(
#         model="qwen3:4b",
#         messages=[
#             {
#                 "role": "user",
#                 "content": "Explain RAG in one simple sentence.",
#             }
#         ],
#     )

#     print(response.message.content)


# if __name__ == "__main__":
#     test_llm()

from ollama import chat


def generate_answer(
    question: str,
    chunks: list[dict],
) -> str:

    context_parts = []

    for chunk in chunks:
        context_parts.append(
            f"[Page {chunk['page_number']}]\n"
            f"{chunk['content']}"
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
You are a helpful document question-answering assistant.

Answer the user's question using ONLY the information provided in the context.

Rules:
1. Do not use outside knowledge.
2. Do not invent or assume information.
3. Give a natural, conversational answer.
4. Include the relevant information from the document directly in your answer.
5. Keep the answer concise, usually 1–3 sentences.
6. If the context does not contain enough information to answer the question,
   respond exactly:
   "I couldn't find the answer in the document."
7. Do not explain why the answer is missing.
8. When you use information from the document, add the relevant page citation
   at the end of the sentence in this format: [Page X].
9. Only cite pages that actually contain information used in your answer.
10. Do not invent page numbers.

Context:
{context}

Question:
{question}
"""

    response = chat(
        model="qwen3:4b",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response.message.content