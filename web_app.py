import streamlit as st
from rembg import remove
from PIL import Image
import os

# Локализация
LANGUAGES = {
    "ru": {
        "title": "Удаление фона с фотографии",
        "select_image": "Выберите изображение",
        "uploaded_image": "Загруженное изображение",
        "remove_background": "Удалить фон",
        "result_image": "Результат удаления фона",
        "download_result": "Скачать результат",
        "format_label": "Выберите формат сохранения",
        "alpha_matting": "Использовать alpha matting",
        "foreground_threshold": "Порог переднего плана",
        "background_threshold": "Порог заднего плана",
        "erode_size": "Размер эрозии",
        "theme_label": "Выберите тему оформления",
        "language_label": "Выберите язык",
    },
    "en": {
        "title": "Background Removal",
        "select_image": "Select Image",
        "uploaded_image": "Uploaded Image",
        "remove_background": "Remove Background",
        "result_image": "Background Removal Result",
        "download_result": "Download Result",
        "format_label": "Select Save Format",
        "alpha_matting": "Use Alpha Matting",
        "foreground_threshold": "Foreground Threshold",
        "background_threshold": "Background Threshold",
        "erode_size": "Erode Size",
        "theme_label": "Select Theme",
        "language_label": "Select Language",
    }
}

# Инициализация языка и темы
if "language" not in st.session_state:
    st.session_state.language = "ru"
if "theme" not in st.session_state:
    st.session_state.theme = "Light"

# Функция для изменения языка
def set_language(lang):
    st.session_state.language = lang

# Функция для изменения темы
def set_theme(theme):
    st.session_state.theme = theme

# Заголовок приложения
st.title(LANGUAGES[st.session_state.language]["title"])

# Выбор языка
language = st.sidebar.selectbox(
    LANGUAGES[st.session_state.language]["language_label"],
    options=["ru", "en"],
    index=0 if st.session_state.language == "ru" else 1,
    on_change=lambda: set_language(language),
)

# Выбор темы
theme = st.sidebar.selectbox(
    LANGUAGES[st.session_state.language]["theme_label"],
    options=["Light", "Dark"],
    index=0 if st.session_state.theme == "Light" else 1,
    on_change=lambda: set_theme(theme),
)

# Применение темы
if theme == "Dark":
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #1E1E1E;
            color: #FFFFFF;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #FFFFFF;
            color: #000000;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Загрузка изображения
uploaded_file = st.file_uploader(
    LANGUAGES[st.session_state.language]["select_image"],
    type=["jpg", "jpeg", "png", "webp", "bmp"],
)

if uploaded_file is not None:
    # Отображение загруженного изображения
    st.image(uploaded_file, caption=LANGUAGES[st.session_state.language]["uploaded_image"], use_column_width=True)

    # Настройки обработки
    st.sidebar.header(LANGUAGES[st.session_state.language]["alpha_matting"])
    alpha_matting = st.sidebar.checkbox(LANGUAGES[st.session_state.language]["alpha_matting"], value=False)
    foreground_threshold = st.sidebar.slider(LANGUAGES[st.session_state.language]["foreground_threshold"], 0, 255, 240)
    background_threshold = st.sidebar.slider(LANGUAGES[st.session_state.language]["background_threshold"], 0, 255, 10)
    erode_size = st.sidebar.slider(LANGUAGES[st.session_state.language]["erode_size"], 0, 20, 10)

    # Выбор формата сохранения
    output_format = st.sidebar.selectbox(
        LANGUAGES[st.session_state.language]["format_label"],
        options=[".png", ".jpg", ".webp"],
    )

    # Кнопка для удаления фона
    if st.button(LANGUAGES[st.session_state.language]["remove_background"]):
        # Открываем изображение
        input_image = Image.open(uploaded_file)

        # Удаляем фон
        output_image = remove(
            input_image,
            alpha_matting=alpha_matting,
            alpha_matting_foreground_threshold=foreground_threshold,
            alpha_matting_background_threshold=background_threshold,
            alpha_matting_erode_size=erode_size,
        )

        # Сохраняем результат
        output_path = f"output{output_format}"
        output_image.save(output_path)

        # Отображаем результат
        st.image(output_image, caption=LANGUAGES[st.session_state.language]["result_image"], use_column_width=True)

        # Кнопка для скачивания результата
        with open(output_path, "rb") as file:
            btn = st.download_button(
                label=LANGUAGES[st.session_state.language]["download_result"],
                data=file,
                file_name=output_path,
                mime=f"image/{output_format[1:]}",  # Убираем точку из формата
            )