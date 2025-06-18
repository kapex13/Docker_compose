import os
os.environ["YFINANCE_USE_CURL"] = "false"

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import io
import warnings 
warnings.filterwarnings('ignore')

# Конфигурация страницы
st.set_page_config("Аналитика", layout="wide")

# Боковая панель
st.sidebar.title("Навигация")
page = st.sidebar.selectbox("Выберите страницу:", ["Котировки Apple", "Анализ чаевых"])

# Страница 1: Котировки Apple
if page == "Котировки Apple":
    st.title("Котировки компании Apple")

    period = st.sidebar.selectbox("Период данных", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=2)

    # Получаем данные
    hist = yf.download("AAPL", period=period, interval="1d", progress=False, threads=False)

    # Преобразуем мультииндексные колонки в обычные (если надо)
    if isinstance(hist.columns, pd.MultiIndex):
        hist.columns = hist.columns.get_level_values(0)

    # Строим график
    fig_line = px.line(hist, x=hist.index, y="Close", title=f"AAPL — Цена закрытия за {period}")
    st.plotly_chart(fig_line, use_container_width=True)

    # Кнопка скачивания графика
    buf = io.BytesIO()
    fig_line.write_image(buf, format="png")
    st.download_button("Скачать график AAPL", data=buf.getvalue(), file_name="aapl_chart.png", mime="image/png")

# Страница 2: Анализ чаевых
elif page == "Анализ чаевых":
    st.title("Анализ пользовательского CSV или tips.csv")

    uploaded_file = st.sidebar.file_uploader("Загрузите CSV-файл с данными", type=["csv"])
    use_default = st.sidebar.checkbox("Использовать пример (tips.csv)", value=True)

    if uploaded_file or use_default:
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_csv("tips.csv")

        st.dataframe(df.head())

        # Проверка нужных колонок
        if {"total_bill", "tip", "sex", "day"}.issubset(df.columns):
            st.subheader("Зависимость чаевых от счёта")
            fig2 = px.scatter(df, x="total_bill", y="tip", color="sex", title="Чаевые vs Счёт")
            st.plotly_chart(fig2, use_container_width=True)

            st.subheader("Средние чаевые по дням")
            mean_tips = df.groupby("day")["tip"].mean().reset_index()
            fig3 = px.bar(mean_tips, x="day", y="tip", title="Средние чаевые по дням")
            st.plotly_chart(fig3, use_container_width=True)

            buf2 = io.BytesIO()
            fig3.write_image(buf2, format="png")
            st.download_button("Скачать график чаевых", data=buf2.getvalue(), file_name="tips_chart.png", mime="image/png")
        else:
            st.warning("В загруженном файле нет нужных колонок: total_bill, tip, sex, day")
    else:
        st.info("Загрузите CSV или выберите 'Использовать пример'.")

# Подвал
st.markdown("---")