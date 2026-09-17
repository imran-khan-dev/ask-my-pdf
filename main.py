from fastapi import FastAPI
from app.modules.documents.router import router as documents_router

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Ask My Document API is running"}


app.include_router(
    documents_router,
    prefix="/documents"
)

# uvicorn main:app --reload
