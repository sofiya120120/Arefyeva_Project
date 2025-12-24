import requests
import time
import io
import base64
import random

from config import API_URL, HF_TOKEN
from models import qg_pipeline, to_en, to_ru
from utils import draw_card, clear_vram

headers = {"Authorization": f"Bearer {HF_TOKEN}"}


def query_flux(prompt, retries=3):
    for i in range(retries):
        try:
            # Более мягкий негативный промпт
            payload = {
                "inputs": prompt,
                "parameters": {
                    "negative_prompt": "text, writing, letters, words, typography",
                    "num_inference_steps": 25,
                    "guidance_scale": 7.5,
                    "height": 512,
                    "width": 768
                }
            }
            r = requests.post(
                API_URL,
                headers=headers,
                json=payload,
                timeout=40
            )
            if r.status_code == 200:
                return r.content
            if r.status_code == 503:
                time.sleep(20)
        except Exception as e:
            print(f"Attempt {i + 1} failed: {e}")
            time.sleep(3)
    return None


def get_visual_prompt(question_en):
    """Создает промпт для визуализации"""
    # Убираем вопросительные слова
    clean_q = question_en.lower()
    for word in ['what', 'how', 'why', 'when', 'where', 'who', 'which', '?']:
        clean_q = clean_q.replace(word, '')

    # Берем ключевые слова
    words = [w for w in clean_q.split() if len(w) > 3][:3]

    if not words:
        words = ['learning', 'education', 'knowledge']

    # Темы для промптов
    themes = [
        "minimalist illustration of {concept}, flat design, clean background",
        "abstract representation of {concept}, geometric shapes, modern art",
        "educational visual of {concept}, simple vector style, white background",
        "conceptual art about {concept}, colorful, clean composition",
        "visual metaphor for {concept}, artistic interpretation, elegant design"
    ]

    concept = ' '.join(words)
    theme = random.choice(themes)

    return theme.format(concept=concept) + ", professional, high quality, no text"


def create_fallback_image():
    """Создает красивый фолбэк фон"""
    from PIL import Image, ImageDraw
    import random

    width, height = 768, 512

    # Красивые градиенты
    gradients = [
        [(135, 206, 235), (176, 224, 230)],  # Небесный
        [(230, 230, 250), (255, 240, 245)],  # Лавандовый
        [(240, 255, 240), (224, 255, 255)],  # Мятный
        [(255, 250, 205), (255, 245, 238)],  # Лимонный
        [(240, 248, 255), (230, 230, 250)],  # Голубой
    ]

    color1, color2 = random.choice(gradients)

    img = Image.new('RGB', (width, height), color1)
    draw = ImageDraw.Draw(img)

    # Рисуем градиент
    for y in range(height):
        ratio = y / height
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Добавляем абстрактные элементы
    for _ in range(5):
        shape_type = random.choice(['circle', 'blob', 'wave'])
        size = random.randint(80, 200)
        x = random.randint(-50, width)
        y = random.randint(-50, height)

        color = (
            random.randint(150, 220),
            random.randint(150, 220),
            random.randint(150, 220),
            60
        )

        if shape_type == 'circle':
            draw.ellipse(
                [x, y, x + size, y + size],
                fill=color[:3] + (30,),
                outline=None
            )
        elif shape_type == 'blob':
            # Рисуем неровный круг
            points = []
            for i in range(10):
                angle = 2 * 3.14159 * i / 10
                radius = size // 2 + random.randint(-20, 20)
                px = x + size // 2 + radius * 0.8 * (i / 10 - 0.5)
                py = y + size // 2 + radius * 0.8 * (i / 10 - 0.5)
                points.append((px, py))

            if len(points) > 2:
                draw.polygon(points, fill=color[:3] + (40,), outline=None)

    buf = io.BytesIO()
    img.save(buf, format='PNG', quality=95)
    return buf.getvalue()


def generate_cards(text: str):
    sentences = []
    current_sentence = ""

    for char in text:
        current_sentence += char
        if char in ['.', '!', '?'] and len(current_sentence.strip()) > 15:
            sentences.append(current_sentence.strip())
            current_sentence = ""

    if current_sentence.strip():
        sentences.append(current_sentence.strip())

    sentences = [s for s in sentences if len(s.strip()) > 12][:4]

    if not sentences:
        return []

    cards = []

    for idx, sent in enumerate(sentences):
        try:
            print(f"\n--- Обработка предложения {idx + 1} ---")

            # Перевод
            en = to_en.translate(sent)
            print(f"Перевод: {en[:50]}...")

            # Генерация вопроса
            q = qg_pipeline(
                f"generate question about: {en}",
                max_new_tokens=60,
                num_beams=4,
                temperature=0.8,
                do_sample=True
            )[0]["generated_text"]

            q = q.replace("question:", "").strip()
            if not q.endswith('?'):
                q += '?'

            ru_q = to_ru.translate(q)
            print(f"Вопрос (RU): {ru_q}")

            # Генерация изображения
            prompt = get_visual_prompt(q)
            print(f"Промпт для изображения: {prompt}")

            img_bytes = query_flux(prompt)

            if img_bytes:
                print("Изображение сгенерировано через AI")
            else:
                print("Используем фолбэк изображение")
                img_bytes = create_fallback_image()

            # Создание карточек
            front = draw_card(img_bytes, ru_q, "ВОПРОС", card_type="question")
            back = draw_card(img_bytes, sent, "ОТВЕТ", card_type="answer")

            # Сохранение
            for card_type, card in [("front", front), ("back", back)]:
                buf = io.BytesIO()
                card.save(buf, format="PNG", optimize=True, quality=95)
                cards.append(base64.b64encode(buf.getvalue()).decode())

            clear_vram()
            print(f"Карточки {idx * 2 + 1} и {idx * 2 + 2} созданы")

        except Exception as e:
            print(f"Ошибка: {e}")
            import traceback
            traceback.print_exc()
            continue

    print(f"\nВсего создано карточек: {len(cards)}")
    return cards