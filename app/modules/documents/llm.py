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


def generate_answer(question: str, chunks: list[str]) -> str:
    context = "\n\n".join(chunks)

    prompt = f"""
You are a document question-answering assistant.

Answer the user's question using ONLY the information in the provided context.

Rules:
1. Do not use outside knowledge.
2. Do not invent or assume information.
3. Give a natural, conversational answer rather than returning only a raw value.
4. Include the relevant information from the document directly in your answer.
5. Keep the answer concise, usually 1–3 sentences.
6. If the context does not contain enough information to answer the question,
   respond exactly:
   "I couldn't find the answer in the document."
7. Do not explain why the answer is missing.

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