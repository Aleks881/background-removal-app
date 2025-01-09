import streamlit as st
from rembg import remove
from PIL import Image
import numpy as np
import cv2
import io

# Инициализация состояния сессии
if "brush_size" not in st.session_state:
    st.session_state.brush_size = 10
if "erase_mode" not in st.session_state:
    st.session_state.erase_mode = False
if "x" not in st.session_state:
    st.session_state.x = 0
if "y" not in st.session_state:
    st.session_state.y = 0
if "mask" not in st.session_state:
    st.session_state.mask = None
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = None
if "output_image" not in st.session_state:
    st.session_state.output_image = None

# Заголовок приложения
st.title("Удаление фона с фотографии")

# Загрузка изображений
uploaded_files = st.file_uploader(
    "Выбрать изображения",
    type=["jpg", "jpeg", "png", "webp", "bmp"],
    accept_multiple_files=True,
)

if uploaded_files:
    st.session_state.uploaded_files = uploaded_files

if st.session_state.uploaded_files:
    # Настройки обработки
    st.sidebar.header("Настройки")
    alpha_matting = st.sidebar.checkbox("Использовать alpha matting", value=False)
    foreground_threshold = st.sidebar.slider("Порог переднего плана", 0, 255, 240)
    background_threshold = st.sidebar.slider("Порог заднего плана", 0, 255, 10)
    erode_size = st.sidebar.slider("Размер эрозии", 0, 20, 10)

    # Ручная коррекция
    st.sidebar.header("Ручная коррекция")
    st.session_state.brush_size = st.sidebar.slider("Размер кисти", 1, 50, st.session_state.brush_size, key="brush_size")
    st.session_state.erase_mode = st.sidebar.checkbox("Режим ластика", value=st.session_state.erase_mode, key="erase_mode")

    # Обработка изображений
    if st.button("Начать обработку"):
        for uploaded_file in st.session_state.uploaded_files:
            input_image = Image.open(uploaded_file)

            # Удаление фона с использованием параметров
            output_image = remove(
                input_image,
                alpha_matting=alpha_matting,
                alpha_matting_foreground_threshold=foreground_threshold,
                alpha_matting_background_threshold=background_threshold,
                alpha_matting_erode_size=erode_size,
            )

            # Создание маски для ручной коррекции
            if st.session_state.mask is None:
                st.session_state.mask = output_image.convert("L")  # Преобразование в черно-белую маску

            # Сохранение результата
            st.session_state.output_image = output_image

    # Ручная коррекция маски
    if st.session_state.output_image is not None:
        st.header("Ручная коррекция")
        st.write("Используйте слайдеры для выбора областей, которые нужно оставить или удалить.")

        # Отображение изображения и маски
        col1, col2 = st.columns(2)
        with col1:
            st.image(st.session_state.output_image, caption="Результат удаления фона", use_container_width=True)
        with col2:
            st.image(st.session_state.mask, caption="Маска", use_container_width=True)

        # Слайдеры для выбора областей
        st.session_state.x = st.slider("Выберите область по X", 0, st.session_state.output_image.width - 1, st.session_state.x, key="x_slider")
        st.session_state.y = st.slider("Выберите область по Y", 0, st.session_state.output_image.height - 1, st.session_state.y, key="y_slider")

        # Применение изменений к маске
        if st.button("Применить коррекцию", key="apply_correction"):
            mask_array = np.array(st.session_state.mask)
            if st.session_state.erase_mode:
                # Ластик: удаляем область
                cv2.circle(mask_array, (st.session_state.x, st.session_state.y), st.session_state.brush_size, 0, -1)
            else:
                # Кисть: добавляем область
                cv2.circle(mask_array, (st.session_state.x, st.session_state.y), st.session_state.brush_size, 255, -1)
            st.session_state.mask = Image.fromarray(mask_array)

        # Применение маски к изображению
        output_image = Image.composite(
            st.session_state.output_image,
            Image.new("RGB", st.session_state.output_image.size, (255, 255, 255)),
            st.session_state.mask
        )

        # Отображение результата
        st.image(output_image, caption="Результат после коррекции", use_container_width=True)

        # Скачивание результата
        output_path = "output_image.png"
        output_image.save(output_path)
        with open(output_path, "rb") as file:
            st.download_button(
                label="Скачать результат",
                data=file,
                file_name=output_path,
                mime="image/png",
            )