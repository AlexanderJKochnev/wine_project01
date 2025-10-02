# streamlite_app.main.py
import streamlit as st
import pandas as pd
import requests
import pymongo
import psycopg2
from PIL import Image
import io
import base64
from config.project_config import settings


# Настройки страницы
st.set_page_config(
    page_title="Admin Panel", page_icon="🖼️", layout="wide"
)


# Подключение к базам данных
@st.cache_resource
def init_postgres_connection():
    try:
        conn = psycopg2.connect(
            host=st.secrets[settings.POSTGRES_HOST], port=st.secrets[settings.POSTGRES_PORT],
            database=st.secrets[settings.POSTGRES_DB], user=st.secrets[settings.POSTGRES_USER],
            password=st.secrets[settings.POSTGRES_PASSWORD]
        )
        return conn
    except Exception as e:
        st.error(f"PostgreSQL connection error: {e}")
        return None


@st.cache_resource
def init_mongo_connection():
    try:
        client = pymongo.MongoClient(
            host=st.secrets[settings.MONGO_HOST], port=int(st.secrets[settings.MONGO_PORT]),
            username=st.secrets[settings.MONGO_USER], password=st.secrets[settings.MONGO_PASSWORD],
            authSource='admin')
        return client
    except Exception as e:
        st.error(f"MongoDB connection error: {e}")
        return None


def main():
    st.title("🖼️ Admin Panel - Images & Data Management")

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


def show_dashboard(pg_conn, mongo_client):
    st.header("📊 Dashboard")

    col1, col2 = st.columns(2)

    with col1:
        # Статистика PostgreSQL
        st.subheader("PostgreSQL Data")
        try:
            df_pg = pd.read_sql("SELECT * FROM your_main_table LIMIT 10", pg_conn)
            st.dataframe(df_pg)
            st.metric("Records in main table", len(df_pg))
        except Exception as e:
            st.error(f"PostgreSQL error: {e}")

    with col2:
        # Статистика MongoDB
        st.subheader("MongoDB Images")
        try:
            db = mongo_client['admin']
            images_count = db.images.count_documents({})
            st.metric("Images in MongoDB", images_count)

            # Показать последнее изображение
            last_image = db.images.find_one(sort=[('_id', -1)])
            if last_image:
                if 'image_data' in last_image:
                    image_data = base64.b64decode(last_image['image_data'])
                    image = Image.open(io.BytesIO(image_data))
                    st.image(image, caption="Latest Image", width=200)
        except Exception as e:
            st.error(f"MongoDB error: {e}")


def show_image_management(mongo_client):
    st.header("🖼️ Image Management")

    tab1, tab2, tab3 = st.tabs(["Upload Images", "Browse Images", "Search Images"])

    with tab1:
        st.subheader("Upload New Images")
        uploaded_files = st.file_uploader(
            "Choose images", accept_multiple_files=True, type=['png', 'jpg', 'jpeg', 'gif'])

        if uploaded_files:
            for uploaded_file in uploaded_files:
                col1, col2 = st.columns([1, 2])
                with col1:
                    # Предпросмотр
                    image = Image.open(uploaded_file)
                    st.image(image, caption=uploaded_file.name, width=150)

                with col2:
                    # Метаданные
                    with st.form(f"form_{uploaded_file.name}"):
                        name = st.text_input(
                            "Image Name", value=uploaded_file.name, key=f"name_{uploaded_file.name}"
                        )
                        category = st.selectbox(
                            "Category", ["Product", "Banner", "Gallery"], key=f"cat_{uploaded_file.name}"
                        )
                        tags = st.text_input("Tags (comma separated)", key=f"tags_{uploaded_file.name}")

                        if st.form_submit_button("Save to MongoDB"):
                            save_image_to_mongodb(mongo_client, uploaded_file, name, category, tags)

    with tab2:
        st.subheader("Browse Images")
        try:
            db = mongo_client['admin']
            images = list(db.images.find().limit(20))

            if images:
                cols = st.columns(4)
                for idx, img in enumerate(images):
                    with cols[idx % 4]:
                        if 'image_data' in img:
                            image_data = base64.b64decode(img['image_data'])
                            image = Image.open(io.BytesIO(image_data))
                            st.image(image, width=150)
                            st.caption(img.get('name', 'Unnamed'))
                            if st.button("Delete", key=f"del_{idx}"):
                                db.images.delete_one({'_id': img['_id']})
                                st.rerun()
            else:
                st.info("No images found in MongoDB")
        except Exception as e:
            st.error(f"Error loading images: {e}")


def save_image_to_mongodb(mongo_client, uploaded_file, name, category, tags):
    try:
        db = mongo_client['admin']
        image_data = base64.b64encode(uploaded_file.getvalue()).decode()

        document = {'name': name, 'filename': uploaded_file.name, 'category': category,
                    'tags': [tag.strip() for tag in tags.split(',')] if tags else [], 'image_data': image_data,
                    'size': len(uploaded_file.getvalue()), 'content_type': uploaded_file.type}

        db.images.insert_one(document)
        st.success(f"Image {name} saved to MongoDB!")
    except Exception as e:
        st.error(f"Error saving image: {e}")


def show_data_management(pg_conn):
    st.header("📈 Data Management")

    try:
        # Получить список таблиц
        cursor = pg_conn.cursor()
        cursor.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            """
        )
        tables = [row[0] for row in cursor.fetchall()]

        selected_table = st.selectbox("Select Table", tables)

        if selected_table:
            df = pd.read_sql(f"SELECT * FROM {selected_table} LIMIT 100", pg_conn)
            st.dataframe(df, use_container_width=True)

            # Экспорт данных
            st.download_button(
                "Export to CSV", df.to_csv(index=False), f"{selected_table}.csv", "text/csv"
            )
    except Exception as e:
        st.error(f"Data management error: {e}")


def show_api_integration():
    st.header("🔗 API Integration")

    fastapi_url = st.secrets.get(settings.FASTAPI_URL, "http://app:8000")

    if st.button("Test FastAPI Connection"):
        try:
            response = requests.get(f"{fastapi_url}/docs")
            if response.status_code == 200:
                st.success("✅ FastAPI is accessible")
            else:
                st.error(f"❌ FastAPI returned status: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Cannot connect to FastAPI: {e}")


if __name__ == "__main__":
    main()
