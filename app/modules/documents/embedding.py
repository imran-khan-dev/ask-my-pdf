# from openai import OpenAI
# from dotenv import load_dotenv
# import os

# load_dotenv()

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# def generate_embedding(text: str) -> list[float]:
#     response = client.embeddings.create(
#         model="text-embedding-3-small",
#         input=text,
#     )

#     return response.data[0].embedding


# if __name__ == "__main__":
#     text = "This is a test document chunk."

#     embedding = generate_embedding(text)

#     print("Number of dimensions:", len(embedding))
#     print("First 5 values:", embedding[:5])

from sentence_transformers import SentenceTransformer

model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)


def generate_embedding(text: str) -> list[float]:
    embedding = model.encode(text)

    return embedding.tolist()



if __name__ == "__main__":
    embedding = generate_embedding(
        "This document is about tax registration."
    )

    print("Number of dimensions:", len(embedding))
    print("First 5 numbers:", embedding[:5])