from app.modules.documents.pdf import extract_text

# def chunk_text(
#     text: str,
#     chunk_size: int = 1000,
#     overlap: int = 200,
# ) -> list[str]:

#     if overlap >= chunk_size:
#         raise ValueError("overlap must be smaller than chunk_size")

#     chunks = []

#     start = 0

#     while start < len(text):
#         end = start + chunk_size

#         chunk = text[start:end]

#         chunks.append(chunk)

#         if end >= len(text):
#             break

#         start = end - overlap

#     return chunks


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[str]:

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size

        chunk = text[start:end]

        chunks.append(chunk)

        if end >= len(text):
            break

        start = end - overlap

    return chunks

if __name__ == "__main__":
    text = extract_text("uploads/BIN Certification.PDF")

    chunks = chunk_text(text, chunk_size=100, overlap=20)

    print(f"Total chunks: {len(chunks)}")

    for index, chunk in enumerate(chunks[:3]):
        print(f"\n===== CHUNK {index + 1} =====")
        print(chunk)