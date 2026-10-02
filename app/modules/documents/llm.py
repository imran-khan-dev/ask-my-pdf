from ollama import chat


def test_llm():
    response = chat(
        model="qwen3:4b",
        messages=[
            {
                "role": "user",
                "content": "Explain RAG in one simple sentence.",
            }
        ],
    )

    print(response.message.content)


if __name__ == "__main__":
    test_llm()