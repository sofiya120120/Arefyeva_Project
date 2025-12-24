from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import logging
from services import generate_cards

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SmartFlash AI API",
    description="API для генерации учебных карточек вопрос-ответ",
    version="1.1.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TextRequest(BaseModel):
    text: str


class CardResponse(BaseModel):
    cards: List[str]
    count: int
    status: str


@app.post("/generate", response_model=CardResponse)
def generate(req: TextRequest):
    """
    Генерирует карточки вопрос-ответ на основе входного текста
    """
    try:
        if not req.text or len(req.text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Текст должен содержать минимум 50 символов"
            )

        logger.info(f"Generating cards for text of length: {len(req.text)}")
        cards = generate_cards(req.text)

        return CardResponse(
            cards=cards,
            count=len(cards),
            status="success" if cards else "no_cards_generated"
        )

    except Exception as e:
        logger.error(f"Error generating cards: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check():
    """Проверка состояния API"""
    return {"status": "healthy", "service": "SmartFlash AI"}


@app.get("/")
def root():
    """Корневой endpoint с информацией об API"""
    return {
        "service": "SmartFlash AI",
        "version": "1.1.0",
        "endpoints": {
            "/generate": "POST - генерация карточек",
            "/health": "GET - проверка состояния",
            "/docs": "Swagger документация"
        }
    }