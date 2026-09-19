from app.core.database import Base, engine
from app.modules.documents.model import Document


Base.metadata.create_all(bind=engine)

print("Database tables created!")