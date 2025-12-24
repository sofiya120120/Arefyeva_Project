import streamlit as st
import requests
import base64
import io
from PIL import Image
import time
import random

# Настройка страницы
st.set_page_config(
    page_title="SmartFlash AI - Умные карточки",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Кастомные стили
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    .main-container {
        background: white;
        border-radius: 20px;
        padding: 30px;
        margin: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.1);
    }

    .title-text {
        font-size: 4rem !important;
        font-weight: 900 !important;
        text-align: center;
        margin-bottom: 10px !important;
        color: #2c3e50 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        letter-spacing: 1px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    .subtitle-text {
        font-size: 1.4rem !important;
        text-align: center;
        margin-bottom: 40px !important;
        color: #e74c3c !important;
        font-weight: 600 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        padding: 10px;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        display: inline-block;
        box-shadow: 0 4px 15px rgba(231, 76, 60, 0.2);
    }

    .card-pair {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        border-left: 5px solid #667eea;
    }

    .card-title {
        color: #2c3e50;
        font-weight: bold;
        font-size: 1.3rem;
        margin-bottom: 10px;
    }

    .status-success {
        background: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #28a745;
    }

    .status-error {
        background: #f8d7da;
        color: #721c24;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
    }

    .generate-btn {
        background: linear-gradient(90deg, #e74c3c 0%, #e67e22 100%) !important;
        color: white !important;
        border: none !important;
        padding: 15px 40px !important;
        font-size: 1.2rem !important;
        border-radius: 50px !important;
        font-weight: bold !important;
        width: 100%;
        transition: transform 0.3s !important;
        box-shadow: 0 10px 30px rgba(231, 76, 60, 0.4) !important;
    }

    .generate-btn:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 15px 40px rgba(231, 76, 60, 0.6) !important;
        background: linear-gradient(90deg, #c0392b 0%, #d35400 100%) !important;
    }

    .text-input {
        border: 2px solid #e0e0e0 !important;
        border-radius: 15px !important;
        padding: 20px !important;
        font-size: 1.1rem !important;
        transition: border 0.3s !important;
    }

    .text-input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }

    .stats-box {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        margin: 10px 0;
    }

    .stats-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2c3e50;
    }

    .stats-label {
        color: #7f8c8d;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .image-container {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        transition: transform 0.3s;
        margin-bottom: 20px;
    }

    .image-container:hover {
        transform: translateY(-5px);
    }

    .card-badge {
        position: absolute;
        top: 10px;
        right: 10px;
        background: #667eea;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }

    .example-btn {
        background: #3498db !important;
        color: white !important;
        border: none !important;
        margin: 5px 0 !important;
    }

    .example-btn:hover {
        background: #2980b9 !important;
    }
</style>
""", unsafe_allow_html=True)

# Основной контейнер
with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    # Заголовок
    st.markdown('<h1 class="title-text">SmartFlash AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle-text">Создавайте умные учебные карточки с искусственным интеллектом</p>',
                unsafe_allow_html=True)

    # Две колонки
    col_left, col_right = st.columns([2, 1])

    with col_left:
        # Ввод текста
        st.markdown("### Введите учебный материал")
        text = st.text_area(
            "",
            height=250,
            placeholder="Например: Искусственный интеллект — это область компьютерных наук, занимающаяся созданием интеллектуальных машин...",
            help="Чем подробнее текст, тем лучше будут карточки. Рекомендуется 3-5 предложений.",
            key="text_input"
        )

        # Статистика текста
        if text:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="stats-box">
                    <div class="stats-number">{len(text.split())}</div>
                    <div class="stats-label">Слов</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="stats-box">
                    <div class="stats-number">{len([s for s in text.split('.') if len(s.strip()) > 5])}</div>
                    <div class="stats-label">Предложений</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="stats-box">
                    <div class="stats-number">{len(text)}</div>
                    <div class="stats-label">Символов</div>
                </div>
                """, unsafe_allow_html=True)

    with col_right:
        st.markdown("### Настройки")

        # Настройки API
        api_url = st.text_input(
            "URL сервера:",
            value="http://localhost:8000",
            help="Адрес вашего FastAPI сервера"
        )

        # Тест соединения
        if st.button("Проверить соединение", use_container_width=True):
            try:
                with st.spinner("Проверяем..."):
                    r = requests.get(f"{api_url}/health", timeout=5)
                    if r.status_code == 200:
                        st.success("Сервер доступен!")
                    else:
                        st.error(f"Ошибка: {r.status_code}")
            except Exception as e:
                st.error(f"Ошибка соединения: {str(e)[:50]}")

        st.markdown("---")

        # Примеры текста
        st.markdown("### Примеры")

        examples = {
            "Искусственный интеллект": "Искусственный интеллект — это область компьютерных наук, которая занимается созданием систем, способных выполнять задачи, требующие человеческого интеллекта. Эти задачи включают распознавание речи, принятие решений и визуальное восприятие. Машинное обучение является подразделом искусственного интеллекта и использует алгоритмы для обучения на данных.",
            "Фотосинтез": "Фотосинтез — это процесс, с помощью которого растения преобразуют световую энергию в химическую энергию. Этот процесс происходит в хлоропластах и требует наличие воды, углекислого газа и солнечного света. В результате фотосинтеза образуется глюкоза и выделяется кислород.",
            "Древний Рим": "Древний Рим был цивилизацией, которая началась на Апеннинском полуострове в 8 веке до нашей эры. Римская империя стала одной из крупнейших империй в древнем мире и оказала огромное влияние на современную западную культуру. Римское право, архитектура и инженерия до сих пор изучаются во всем мире."
        }

        selected_example = st.selectbox("Выберите пример:", list(examples.keys()))
        if st.button("Использовать пример", use_container_width=True, key="use_example"):
            st.session_state.example_text = examples[selected_example]
            st.rerun()

    # Кнопка генерации
    st.markdown("---")
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        generate_clicked = st.button(
            "СГЕНЕРИРОВАТЬ КАРТОЧКИ",
            type="primary",
            use_container_width=True,
            key="generate_main"
        )

    # Если был выбран пример
    if 'example_text' in st.session_state:
        text = st.text_area(
            "Введите учебный материал",
            value=st.session_state.example_text,
            height=250,
            key="text_input_example"
        )
        del st.session_state.example_text

    # Генерация карточек
    if generate_clicked and text:
        if len(text.strip()) < 50:
            st.warning("Пожалуйста, введите текст длиннее 50 символов для лучших результатов.")
        else:
            with st.spinner("Генерируем умные карточки... Это займет около 30 секунд"):
                try:
                    start_time = time.time()

                    # Индикатор прогресса
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    status_text.markdown("<div class='status-success'>Отправляем запрос на сервер...</div>",
                                         unsafe_allow_html=True)

                    # Отправка запроса
                    response = requests.post(
                        f"{api_url}/generate",
                        json={"text": text},
                        timeout=120
                    )

                    progress_bar.progress(30)
                    status_text.markdown("<div class='status-success'>Генерируем изображения...</div>",
                                         unsafe_allow_html=True)

                    elapsed_time = time.time() - start_time

                    if response.status_code == 200:
                        result = response.json()
                        cards = result.get("cards", [])

                        progress_bar.progress(70)
                        status_text.markdown("<div class='status-success'>Создаем карточки...</div>",
                                             unsafe_allow_html=True)

                        if cards:
                            progress_bar.progress(100)
                            status_text.markdown(f"""
                            <div class='status-success'>
                            Успешно создано {len(cards)} карточек за {elapsed_time:.1f} секунд!
                            </div>
                            """, unsafe_allow_html=True)

                            # Показываем карточки парами
                            st.markdown("### Ваши умные карточки")

                            for i in range(0, len(cards), 2):
                                col_q, col_a = st.columns(2)

                                with col_q:
                                    if i < len(cards):
                                        st.markdown("#### ВОПРОС")
                                        img = Image.open(io.BytesIO(base64.b64decode(cards[i])))
                                        st.image(img, use_container_width=True)

                                with col_a:
                                    if i + 1 < len(cards):
                                        st.markdown("#### ОТВЕТ")
                                        img = Image.open(io.BytesIO(base64.b64decode(cards[i + 1])))
                                        st.image(img, use_container_width=True)

                                if i + 2 < len(cards):
                                    st.markdown("---")

                            # Опции экспорта
                            st.markdown("---")
                            st.markdown("### Экспорт карточек")

                            exp_col1, exp_col2, exp_col3 = st.columns(3)

                            with exp_col1:
                                if st.button("Скачать все как ZIP", use_container_width=True, key="download_zip"):
                                    # Создаем ZIP архив
                                    import zipfile
                                    from io import BytesIO

                                    zip_buffer = BytesIO()
                                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                                        for idx, card_b64 in enumerate(cards):
                                            img_data = base64.b64decode(card_b64)
                                            card_type = "question" if idx % 2 == 0 else "answer"
                                            card_num = idx // 2 + 1
                                            zip_file.writestr(
                                                f"card_{card_num:02d}_{card_type}.png",
                                                img_data
                                            )

                                    zip_buffer.seek(0)

                                    st.download_button(
                                        label="Скачать ZIP архив",
                                        data=zip_buffer,
                                        file_name="smartflash_cards.zip",
                                        mime="application/zip",
                                        use_container_width=True,
                                        key="download_button"
                                    )

                            with exp_col2:
                                if st.button("Сгенерировать еще", use_container_width=True, key="regenerate"):
                                    st.rerun()

                            with exp_col3:
                                if st.button("Очистить", use_container_width=True, key="clear_all"):
                                    st.session_state.clear()
                                    st.rerun()

                        else:
                            status_text.markdown("""
                            <div class='status-error'>
                            Не удалось создать карточки. Попробуйте:
                            1. Увеличить текст
                            2. Проверить подключение к интернету
                            3. Попробовать другой текст
                            </div>
                            """, unsafe_allow_html=True)

                    elif response.status_code == 500:
                        status_text.markdown(f"""
                        <div class='status-error'>
                        Ошибка сервера: {response.text[:100]}...
                        </div>
                        """, unsafe_allow_html=True)

                        st.info("""
                        **Решение проблем:**
                        1. Убедитесь, что backend запущен: `uvicorn backend.main:app --reload`
                        2. Проверьте наличие токена HuggingFace в .env файле
                        3. Убедитесь, что интернет соединение стабильное
                        """)

                    else:
                        status_text.markdown(f"""
                        <div class='status-error'>
                        Ошибка {response.status_code}: {response.text[:100]}...
                        </div>
                        """, unsafe_allow_html=True)

                except requests.exceptions.ConnectionError:
                    status_text.markdown("""
                    <div class='status-error'>
                    Не удалось подключиться к серверу!
                    </div>
                    """, unsafe_allow_html=True)

                    st.info("""
                    **Чтобы запустить сервер:**
                    ```bash
                    cd backend
                    uvicorn main:app --reload --host 0.0.0.0 --port 8000
                    ```
                    """)

                except requests.exceptions.Timeout:
                    status_text.markdown("""
                    <div class='status-error'>
                    Время ожидания истекло! Генерация заняла слишком много времени.
                    </div>
                    """, unsafe_allow_html=True)

                except Exception as e:
                    status_text.markdown(f"""
                    <div class='status-error'>
                    Неожиданная ошибка: {str(e)[:100]}
                    </div>
                    """, unsafe_allow_html=True)

    elif generate_clicked:
        st.warning("Пожалуйста, сначала введите текст для генерации карточек.")

    # Футер
    st.markdown("---")
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f2:
        st.markdown(
            "<p style='text-align: center; color: #666;'>"
            "SmartFlash AI • Создано для эффективного обучения • "
            f"<span style='color: #e74c3c;'>Версия 2.0</span>"
            "</p>",
            unsafe_allow_html=True
        )

    st.markdown('</div>', unsafe_allow_html=True)  # Закрываем main-container