import gc
import io
import os
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import torch


def clear_vram():
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def get_font(size, bold=False):
    """Находит лучший доступный шрифт"""
    font_paths = []

    # Windows
    if os.name == 'nt':
        font_paths.extend([
            "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/timesbd.ttf" if bold else "C:/Windows/Fonts/times.ttf",
        ])
    # Linux
    elif os.name == 'posix':
        font_paths.extend([
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf" if bold else
            "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
        ])
    # macOS
    else:
        font_paths.extend([
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        ])

    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                continue

    # Запасной вариант
    try:
        return ImageFont.truetype("arial.ttf", size) if not bold else ImageFont.truetype("arialbd.ttf", size)
    except:
        return ImageFont.load_default(size)


def draw_card(base_img_bytes, text, label, card_type="question"):
    """Создает красивую карточку с текстом"""
    # Открываем изображение
    if isinstance(base_img_bytes, bytes):
        try:
            img = Image.open(io.BytesIO(base_img_bytes)).convert("RGB")
        except:
            # Если ошибка - создаем градиентный фон
            img = Image.new('RGB', (768, 512), color=(240, 248, 255))
    else:
        img = base_img_bytes

    draw = ImageDraw.Draw(img, "RGBA")
    w, h = img.size

    # БОЛЬШИЕ размеры шрифтов
    label_font_size = 38
    text_font_size = 34

    # Цветовые схемы
    color_schemes = {
        "question": {
            "label": (52, 152, 219),  # Яркий синий
            "bg": (255, 255, 255, 225),  # Почти непрозрачный
            "text": (44, 62, 80),  # Темно-серый
            "accent": (41, 128, 185),
        },
        "answer": {
            "label": (46, 204, 113),  # Яркий зеленый
            "bg": (255, 255, 255, 225),
            "text": (44, 62, 80),
            "accent": (39, 174, 96),
        }
    }

    colors = color_schemes[card_type]

    # Шрифты
    label_font = get_font(label_font_size, bold=True)
    text_font = get_font(text_font_size, bold=False)

    # Разбиваем текст с учетом ширины
    max_width = w - 80
    lines = []

    words = text.split()
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=text_font)
        text_width = bbox[2] - bbox[0]

        if text_width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    # Ограничение строк
    if len(lines) > 4:
        lines = lines[:4]
        if len(lines[-1]) > 30:
            lines[-1] = lines[-1][:27] + "..."

    # Рассчитываем размеры
    line_height = 44
    label_height = 48
    padding = 30
    total_height = label_height + (len(lines) * line_height) + (padding * 2)

    # Рисуем красивый фон с тенями
    bg_rect = [25, h - total_height - 25, w - 25, h - 25]

    # Тень
    shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle(
        [bg_rect[0] + 4, bg_rect[1] + 4, bg_rect[2] + 4, bg_rect[3] + 4],
        radius=15,
        fill=(0, 0, 0, 30)
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img.convert('RGBA'), shadow).convert('RGB')
    draw = ImageDraw.Draw(img, "RGBA")

    # Основной фон
    draw.rounded_rectangle(
        bg_rect,
        radius=15,
        fill=colors["bg"],
        outline=colors["accent"],
        width=3
    )

    # Метка карточки
    label_bg = [bg_rect[0] + 15, bg_rect[1] + 15, bg_rect[0] + 180, bg_rect[1] + label_height]
    draw.rounded_rectangle(
        label_bg,
        radius=10,
        fill=colors["label"]
    )

    # Текст метки
    label_bbox = draw.textbbox((0, 0), label, font=label_font)
    label_x = label_bg[0] + (label_bg[2] - label_bg[0] - (label_bbox[2] - label_bbox[0])) // 2
    label_y = label_bg[1] + (label_bg[3] - label_bg[1] - (label_bbox[3] - label_bbox[1])) // 2 - 3

    # Тень текста метки
    draw.text(
        (label_x + 1, label_y + 1),
        label,
        fill=(0, 0, 0, 60),
        font=label_font
    )

    # Основной текст метки
    draw.text(
        (label_x, label_y),
        label,
        fill="white",
        font=label_font
    )

    # Основной текст
    text_y = bg_rect[1] + label_height + padding

    for i, line in enumerate(lines):
        line_bbox = draw.textbbox((0, 0), line, font=text_font)
        line_x = bg_rect[0] + (bg_rect[2] - bg_rect[0] - (line_bbox[2] - line_bbox[0])) // 2

        # Тень текста
        draw.text(
            (line_x + 1, text_y + (i * line_height) + 1),
            line,
            fill=(0, 0, 0, 40),
            font=text_font
        )

        # Основной текст
        draw.text(
            (line_x, text_y + (i * line_height)),
            line,
            fill=colors["text"],
            font=text_font
        )

    # Декоративный элемент
    if card_type == "question":
        # Значок вопроса
        icon_color = colors["label"]
        icon_bg = (icon_color[0], icon_color[1], icon_color[2], 180)
        draw.ellipse(
            [w - 75, 25, w - 25, 75],
            fill=icon_bg,
            outline=icon_color,
            width=3
        )

        # Знак вопроса
        q_font = get_font(36, bold=True)
        q_bbox = draw.textbbox((0, 0), "?", font=q_font)
        q_x = w - 50 - (q_bbox[2] - q_bbox[0]) // 2
        q_y = 50 - (q_bbox[3] - q_bbox[1]) // 2
        draw.text((q_x, q_y), "?", fill="white", font=q_font)

    else:
        # Значок галочки
        icon_color = colors["label"]
        icon_bg = (icon_color[0], icon_color[1], icon_color[2], 180)
        draw.ellipse(
            [w - 75, 25, w - 25, 75],
            fill=icon_bg,
            outline=icon_color,
            width=3
        )

        # Галочка
        check_font = get_font(36, bold=True)
        check_bbox = draw.textbbox((0, 0), "✓", font=check_font)
        check_x = w - 50 - (check_bbox[2] - check_bbox[0]) // 2
        check_y = 50 - (check_bbox[3] - check_bbox[1]) // 2
        draw.text((check_x, check_y), "✓", fill="white", font=check_font)

    return img