# from pypdf import PdfReader


# def extract_text(file_path: str) -> str:
#     reader = PdfReader(file_path)

#     text = ""

#     for page in reader.pages:
#         page_text = page.extract_text()

#         if page_text:
#             text += page_text + "\n"

#     return text


# if __name__ == "__main__":
#     text = extract_text("uploads/BIN Certification.PDF")

#     print(text)

from pypdf import PdfReader


def extract_text(file_path: str) -> str:
    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    # Remove NUL characters
    text = text.replace("\x00", "")

    return text


def extract_pages(file_path: str) -> list[dict]:
    reader = PdfReader(file_path)

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text()

        if page_text:
            page_text = page_text.replace("\x00", "")

            pages.append(
                {
                    "page_number": page_number,
                    "text": page_text,
                }
            )

    return pages