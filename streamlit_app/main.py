# streamlite_app.main.py
import streamlit as st
import pandas as pd
import requests
import pymongo
import psycopg2
from PIL import Image
import io
import base64
import os

# Настройки страницы
st.set_page_config(
        page_title = "Admin Panel", page_icon = "🖼️", layout = "wide"
        )


# Получение настроек из переменных окружения
def get_database_config():
    return {"POSTGRES_HOST": os.getenv("POSTGRES_HOST", "wine_host"),
            "POSTGRES_PORT": os.getenv("POSTGRES_PORT", "5432"),
            "POSTGRES_DB": os.getenv("POSTGRES_DB", "your_database"),
            "POSTGRES_USER": os.getenv("POSTGRES_USER", "your_username"),
            "POSTGRES_PASSWORD": os.getenv("POSTGRES_PASSWORD", "your_password"),
            "MONGO_HOST": os.getenv("MONGO_HOST", "mongo"), "MONGO_PORT": os.getenv("MONGO_PORT", "27017"),
            "MONGO_USER": os.getenv("MONGO_USER", "admin"), "MONGO_PASSWORD": os.getenv("MONGO_PASSWORD", "admin"),
            "FASTAPI_URL": os.getenv("FASTAPI_URL", "http://app:8000")}


# Подключение к базам данных
@st.cache_resource
def init_postgres_connection():
    try:
        config = get_database_config()
        conn = psycopg2.connect(
                host = config["POSTGRES_HOST"], port = config["POSTGRES_PORT"], database = config["POSTGRES_DB"],
                user = config["POSTGRES_USER"], password = config["POSTGRES_PASSWORD"]
                )
        return conn
    except Exception as e:
        st.error(f"PostgreSQL connection error: {e}")
        st.info("Check your database configuration")
        return None


@st.cache_resource
def init_mongo_connection():
    try:
        config = get_database_config()
        client = pymongo.MongoClient(
                host = config["MONGO_HOST"], port = int(config["MONGO_PORT"]), username = config["MONGO_USER"],
                password = config["MONGO_PASSWORD"], authSource = 'admin'
                )
        return client
    except Exception as e:
        st.error(f"MongoDB connection error: {e}")
        st.info("Check your MongoDB configuration")
        return None


def main():
    st.title("🖼️ Admin Panel - Images & Data Management")
    
    # Показать текущую конфигурацию (для отладки)
    if st.sidebar.checkbox("Show Configuration"):
        config = get_database_config()
        st.sidebar.json({k: v for k, v in config.items() if "PASSWORD" not in k})
    
    # Инициализация соединений
    pg_conn = init_postgres_connection()
    mongo_client = init_mongo_connection()
    
    if pg_conn and mongo_client:
        # Боковая панель навигации
        st.sidebar.title("Navigation")
        page = st.sidebar.radio("Go to", ["Dashboard", "Image Management", "Data Management", "API Integration"])
        
        if page == "Dashboard":
            show_dashboard(pg_conn, mongo_client)
        elif page == "Image Management":
            show_image_management(mongo_client)
        elif page == "Data Management":
            show_data_management(pg_conn)
        elif page == "API Integration":
            show_api_integration()
    else:
        st.error("Cannot connect to databases")
        st.info(
            """
        Troubleshooting steps:
        1. Check if all services are running: `docker-compose ps`
        2. Verify database credentials in environment variables
        3. Check container networking
        """
            )


# ... остальные функции остаются такими же ...

def show_dashboard(pg_conn, mongo_client):
    st.header("📊 Dashboard")
    
    # Проверка соединений
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success("✅ PostgreSQL Connected")
        try:
            cursor = pg_conn.cursor()
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            st.text(f"PostgreSQL: {version.split(',')[0]}")
        except Exception as e:
            st.error(f"PostgreSQL error: {e}")
    
    with col2:
        st.success("✅ MongoDB Connected")
        try:
            db = mongo_client['admin']
            info = db.command('serverStatus')
            st.text(f"MongoDB: {info['version']}")
        except Exception as e:
            st.error(f"MongoDB error: {e}")
    
    with col3:
        config = get_database_config()
        try:
            response = requests.get(f"{config['FASTAPI_URL']}/docs", timeout = 5)
            if response.status_code == 200:
                st.success("✅ FastAPI Connected")
            else:
                st.warning("⚠️ FastAPI accessible but returned non-200")
        except Exception as e:
            st.error(f"❌ FastAPI error: {e}")

# ... остальные функции без изменений ...