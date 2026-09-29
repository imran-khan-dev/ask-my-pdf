from pypdf import PdfReader


def extract_text(file_path: str) -> str:
    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


if __name__ == "__main__":
    text = extract_text("uploads/BIN Certification.PDF")

    print(text)