import re

def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[str]:
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    # Normalize whitespace while keeping paragraph boundaries.
    paragraphs = re.split(r"\n\s*\n", text)

    paragraphs = [
        paragraph.strip()
        for paragraph in paragraphs
        if paragraph.strip()
    ]

    chunks = []
    current = ""

    for paragraph in paragraphs:
        # If adding this paragraph still fits, keep it together.
        if len(current) + len(paragraph) + 1 <= chunk_size:
            current = (
                f"{current}\n{paragraph}"
                if current
                else paragraph
            )
            continue

        # Save the current chunk.
        if current:
            chunks.append(current)

        # If a single paragraph is larger than chunk_size,
        # fall back to character-based splitting for that paragraph.
        if len(paragraph) > chunk_size:
            start = 0

            while start < len(paragraph):
                end = start + chunk_size
                chunks.append(paragraph[start:end])

                if end >= len(paragraph):
                    break

                start = end - overlap

            current = ""
        else:
            current = paragraph

    if current:
        chunks.append(current)

    return chunks