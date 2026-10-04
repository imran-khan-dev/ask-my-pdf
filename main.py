from fastapi import FastAPI
from app.modules.documents.router import router as documents_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Ask My Document API is running"}


app.include_router(
    documents_router,
    prefix="/documents"
)

# uvicorn main:app --reload
# alembic revision --autogenerate -m "add extracted text to documents"
# alembic upgrade head

