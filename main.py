from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def home():
    return {
        "message": "Ask My Document API is running"
    }

@app.get("/documents/{document_id}")
def get_document(document_id: int):
    return {
        "document_id": document_id
    }