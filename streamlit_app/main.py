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
from datetime import datetime

# Настройки страницы
st.set_page_config(
        page_title = "Admin Panel", page_icon = "🖼️", layout = "wide", initial_sidebar_state = "expanded"
        )


# Конфигурация из переменных окружения
def get_config():
    return {"POSTGRES_HOST": os.getenv("POSTGRES_HOST", "wine_host"),
            "POSTGRES_PORT": os.getenv("POSTGRES_PORT", "5432"), "POSTGRES_DB": os.getenv("POSTGRES_DB", "postgres"),
            "POSTGRES_USER": os.getenv("POSTGRES_USER", "postgres"),
            "POSTGRES_PASSWORD": os.getenv("POSTGRES_PASSWORD", "password"),
            "MONGO_HOST": os.getenv("MONGO_HOST", "mongo"), "MONGO_PORT": os.getenv("MONGO_PORT", "27017"),
            "MONGO_USER": os.getenv("MONGO_USER", "admin"), "MONGO_PASSWORD": os.getenv("MONGO_PASSWORD", "admin"),
            "FASTAPI_URL": os.getenv("FASTAPI_URL", "http://app:8000")}


# Подключение к базам данных
@st.cache_resource
def init_postgres_connection():
    try:
        config = get_config()
        conn = psycopg2.connect(
                host = config["POSTGRES_HOST"], port = config["POSTGRES_PORT"], database = config["POSTGRES_DB"],
                user = config["POSTGRES_USER"], password = config["POSTGRES_PASSWORD"]
                )
        return conn
    except Exception as e:
        st.error(f"PostgreSQL connection error: {e}")
        return None


@st.cache_resource
def init_mongo_connection():
    try:
        config = get_config()
        client = pymongo.MongoClient(
                host = config["MONGO_HOST"], port = int(config["MONGO_PORT"]), username = config["MONGO_USER"],
                password = config["MONGO_PASSWORD"], authSource = 'admin', serverSelectionTimeoutMS = 5000
                )
        return client
    except Exception as e:
        st.error(f"MongoDB connection error: {e}")
        return None


# Автоматическая интеграция с FastAPI
@st.cache_data(ttl = 60)
def get_fastapi_endpoints():
    """Автоматически получает эндпоинты из FastAPI"""
    config = get_config()
    try:
        response = requests.get(f"{config['FASTAPI_URL']}/openapi.json", timeout = 5)
        if response.status_code == 200:
            openapi_spec = response.json()
            endpoints = []
            
            for path, methods in openapi_spec.get('paths', {}).items():
                for method, details in methods.items():
                    endpoints.append(
                            {'path': path, 'method': method.upper(), 'summary': details.get('summary', 'No summary'),
                                    'tags': details.get('tags', [])}
                            )
            return endpoints
        return []
    except:
        return []


def call_fastapi_endpoint(endpoint, method="GET", data=None):
    """Вызов эндпоинта FastAPI"""
    config = get_config()
    url = f"{config['FASTAPI_URL']}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout = 10)
        elif method.upper() == "POST":
            response = requests.post(url, json = data, timeout = 10)
        elif method.upper() == "PUT":
            response = requests.put(url, json = data, timeout = 10)
        elif method.upper() == "DELETE":
            response = requests.delete(url, timeout = 10)
        else:
            return None, "Unsupported method"
        
        return response, None
    except Exception as e:
        return None, str(e)


def show_dashboard():
    st.header("📊 Dashboard")
    
    pg_conn = init_postgres_connection()
    mongo_client = init_mongo_connection()
    config = get_config()
    
    # Статусы подключений
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if pg_conn:
            st.success("✅ PostgreSQL")
            try:
                df = pd.read_sql(
                    "SELECT COUNT(*) as count FROM information_schema.tables WHERE table_schema = 'public'", pg_conn
                    )
                st.metric("Tables", df.iloc[0]['count'])
            except:
                st.metric("Tables", "N/A")
        else:
            st.error("❌ PostgreSQL")
    
    with col2:
        if mongo_client:
            st.success("✅ MongoDB")
            try:
                db = mongo_client.admin
                collections = db.list_collection_names()
                st.metric("Collections", len(collections))
            except:
                st.metric("Collections", "N/A")
        else:
            st.error("❌ MongoDB")
    
    with col3:
        try:
            response = requests.get(f"{config['FASTAPI_URL']}/docs", timeout = 5)
            if response.status_code == 200:
                st.success("✅ FastAPI")
                endpoints = get_fastapi_endpoints()
                st.metric("Endpoints", len(endpoints))
            else:
                st.warning("⚠️ FastAPI")
        except:
            st.error("❌ FastAPI")
    
    with col4:
        st.info("🔄 System")
        st.metric("Status", "Online" if pg_conn and mongo_client else "Offline")
    
    # Быстрый просмотр данных
    st.subheader("🔍 Quick Data Preview")
    
    tab1, tab2, tab3 = st.tabs(["PostgreSQL Data", "MongoDB Images", "FastAPI Endpoints"])
    
    with tab1:
        if pg_conn:
            try:
                tables_df = pd.read_sql(
                    """
                    SELECT table_name, table_type
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """, pg_conn
                    )
                
                selected_table = st.selectbox("Select Table", tables_df['table_name'].tolist())
                if selected_table:
                    data_df = pd.read_sql(f"SELECT * FROM {selected_table} LIMIT 10", pg_conn)
                    st.dataframe(data_df, use_container_width = True)
                    st.metric("Rows", len(data_df))
            except Exception as e:
                st.error(f"Error loading data: {e}")
    
    with tab2:
        if mongo_client:
            try:
                db = mongo_client.admin
                images_count = db.images.count_documents({}) if 'images' in db.list_collection_names() else 0
                st.metric("Total Images", images_count)
                
                if images_count > 0:
                    images = list(db.images.find().limit(4))
                    cols = st.columns(4)
                    for idx, img in enumerate(images):
                        with cols[idx]:
                            if 'image_data' in img:
                                try:
                                    image_data = base64.b64decode(img['image_data'])
                                    image = Image.open(io.BytesIO(image_data))
                                    st.image(image, caption = img.get('name', 'Unnamed'), width = 150)
                                except:
                                    st.info("Invalid image data")
                            else:
                                st.info("No image data")
                else:
                    st.info("No images in database")
            except Exception as e:
                st.error(f"Error loading images: {e}")
    
    with tab3:
        endpoints = get_fastapi_endpoints()
        if endpoints:
            for endpoint in endpoints[:5]:  # Показываем первые 5 эндпоинтов
                st.code(f"{endpoint['method']} {endpoint['path']}")
                st.caption(endpoint['summary'])
        else:
            st.info("No endpoints found or FastAPI not accessible")


def show_image_management():
    st.header("🖼️ Image Management")
    
    mongo_client = init_mongo_connection()
    
    if not mongo_client:
        st.error("MongoDB not connected")
        return
    
    db = mongo_client.admin
    
    tab1, tab2, tab3 = st.tabs(["📤 Upload Images", "🖼️ Browse Images", "🔍 Search & Edit"])
    
    with tab1:
        st.subheader("Upload New Images")
        
        uploaded_files = st.file_uploader(
                "Choose images", accept_multiple_files = True, type = ['png', 'jpg', 'jpeg', 'gif'],
                help = "Select one or multiple images to upload"
                )
        
        if uploaded_files:
            for uploaded_file in uploaded_files:
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    # Предпросмотр
                    image = Image.open(uploaded_file)
                    st.image(image, caption = uploaded_file.name, use_column_width = True)
                
                with col2:
                    with st.form(f"form_{uploaded_file.name}"):
                        name = st.text_input(
                            "Image Name", value = uploaded_file.name, key = f"name_{uploaded_file.name}"
                            )
                        category = st.selectbox(
                            "Category", ["Product", "Banner", "Gallery", "Other"], key = f"cat_{uploaded_file.name}"
                            )
                        tags = st.text_input("Tags (comma separated)", key = f"tags_{uploaded_file.name}")
                        description = st.text_area("Description", key = f"desc_{uploaded_file.name}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("💾 Save to MongoDB", use_container_width = True):
                                save_image_to_mongodb(db, uploaded_file, name, category, tags, description)
                        with col2:
                            if st.form_submit_button("🚫 Cancel", use_container_width = True):
                                st.info("Upload cancelled")
    
    with tab2:
        st.subheader("Image Gallery")
        
        # Фильтры
        col1, col2, col3 = st.columns(3)
        with col1:
            category_filter = st.selectbox("Filter by Category", ["All", "Product", "Banner", "Gallery", "Other"])
        with col2:
            sort_by = st.selectbox("Sort by", ["Newest", "Oldest", "Name"])
        with col3:
            items_per_page = st.selectbox("Images per page", [12, 24, 48])
        
        # Пагинация
        if 'page' not in st.session_state:
            st.session_state.page = 0
        
        # Загрузка изображений
        try:
            query = {}
            if category_filter != "All":
                query["category"] = category_filter
            
            sort_field = {"Newest": "_id", "Oldest": "_id", "Name": "name"}[sort_by]
            sort_order = -1 if sort_by == "Newest" else 1
            
            total_images = db.images.count_documents(query)
            total_pages = (total_images + items_per_page - 1) // items_per_page
            
            images = list(
                db.images.find(query).sort(sort_field, sort_order).skip(st.session_state.page * items_per_page).limit(
                    items_per_page
                    )
                )
            
            if images:
                st.write(f"Showing {len(images)} of {total_images} images")
                
                # Галерея
                cols = st.columns(4)
                for idx, img in enumerate(images):
                    with cols[idx % 4]:
                        with st.container():
                            if 'image_data' in img:
                                try:
                                    image_data = base64.b64decode(img['image_data'])
                                    image = Image.open(io.BytesIO(image_data))
                                    st.image(image, use_column_width = True)
                                except:
                                    st.error("❌ Invalid image")
                            
                            st.caption(f"**{img.get('name', 'Unnamed')}**")
                            st.caption(f"Category: {img.get('category', 'N/A')}")
                            st.caption(f"Size: {img.get('size', 0) // 1024} KB")
                            
                            col_btn1, col_btn2 = st.columns(2)
                            with col_btn1:
                                if st.button("👁️", key = f"view_{idx}", help = "View details"):
                                    st.session_state.selected_image = img
                            with col_btn2:
                                if st.button("🗑️", key = f"del_{idx}", help = "Delete"):
                                    db.images.delete_one({'_id': img['_id']})
                                    st.rerun()
                
                # Навигация по страницам
                col_prev, col_info, col_next = st.columns([1, 2, 1])
                with col_prev:
                    if st.button("⬅️ Previous") and st.session_state.page > 0:
                        st.session_state.page -= 1
                        st.rerun()
                with col_info:
                    st.write(f"Page {st.session_state.page + 1} of {total_pages}")
                with col_next:
                    if st.button("Next ➡️") and st.session_state.page < total_pages - 1:
                        st.session_state.page += 1
                        st.rerun()
            else:
                st.info("No images found")
        
        except Exception as e:
            st.error(f"Error loading images: {e}")
    
    with tab3:
        st.subheader("Image Details & Search")
        
        if 'selected_image' in st.session_state:
            img = st.session_state.selected_image
            col1, col2 = st.columns(2)
            
            with col1:
                if 'image_data' in img:
                    try:
                        image_data = base64.b64decode(img['image_data'])
                        image = Image.open(io.BytesIO(image_data))
                        st.image(image, use_column_width = True)
                    except:
                        st.error("Invalid image data")
            
            with col2:
                st.subheader("Image Details")
                st.write(f"**Name:** {img.get('name', 'N/A')}")
                st.write(f"**Filename:** {img.get('filename', 'N/A')}")
                st.write(f"**Category:** {img.get('category', 'N/A')}")
                st.write(f"**Tags:** {', '.join(img.get('tags', []))}")
                st.write(f"**Size:** {img.get('size', 0) // 1024} KB")
                st.write(f"**Uploaded:** {img.get('upload_date', 'N/A')}")
                
                if st.button("Close Details"):
                    del st.session_state.selected_image
                    st.rerun()
        else:
            st.info("Select an image from the gallery to view details")


def save_image_to_mongodb(db, uploaded_file, name, category, tags, description):
    try:
        image_data = base64.b64encode(uploaded_file.getvalue()).decode()
        
        document = {'name': name, 'filename': uploaded_file.name, 'category': category,
                'tags': [tag.strip() for tag in tags.split(',')] if tags else [], 'description': description,
                'image_data': image_data, 'size': len(uploaded_file.getvalue()), 'content_type': uploaded_file.type,
                'upload_date': datetime.now().isoformat()}
        
        result = db.images.insert_one(document)
        st.success(f"✅ Image '{name}' saved successfully! (ID: {result.inserted_id})")
        
        # Очистка формы
        st.rerun()
    
    except Exception as e:
        st.error(f"❌ Error saving image: {e}")


def show_data_management():
    st.header("📈 Data Management")
    
    pg_conn = init_postgres_connection()
    
    if not pg_conn:
        st.error("PostgreSQL not connected")
        return
    
    tab1, tab2, tab3 = st.tabs(["📋 Table Explorer", "🔧 SQL Query", "📊 Data Analysis"])
    
    with tab1:
        st.subheader("Database Tables")
        
        try:
            # Получить список таблиц
            tables_df = pd.read_sql(
                """
                SELECT
                    table_name,
                    table_type,
                    (SELECT COUNT(*) FROM information_schema.columns
                     WHERE table_schema = 'public' AND table_name = t.table_name) as column_count
                FROM information_schema.tables t
                WHERE table_schema = 'public'
                ORDER BY table_name
            """, pg_conn
                )
            
            selected_table = st.selectbox("Select Table", tables_df['table_name'].tolist())
            
            if selected_table:
                # Показать схему таблицы
                schema_df = pd.read_sql(
                    f"""
                    SELECT
                        column_name,
                        data_type,
                        is_nullable,
                        column_default
                    FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = '{selected_table}'
                    ORDER BY ordinal_position
                """, pg_conn
                    )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Table Schema")
                    st.dataframe(schema_df, use_container_width = True)
                
                with col2:
                    st.subheader("Data Preview")
                    data_df = pd.read_sql(f"SELECT * FROM {selected_table} LIMIT 100", pg_conn)
                    st.dataframe(data_df, use_container_width = True)
                    
                    # Статистика
                    st.metric("Total Rows", len(data_df))
                    st.metric("Columns", len(data_df.columns))
                    
                    # Экспорт
                    csv = data_df.to_csv(index = False)
                    st.download_button(
                            "📥 Export to CSV", csv, f"{selected_table}.csv", "text/csv"
                            )
        
        except Exception as e:
            st.error(f"Error exploring tables: {e}")
    
    with tab2:
        st.subheader("SQL Query Editor")
        
        query = st.text_area(
            "Enter SQL Query", height = 150, placeholder = "SELECT * FROM your_table WHERE ..."
            )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("▶️ Execute Query", use_container_width = True):
                if query:
                    try:
                        result_df = pd.read_sql(query, pg_conn)
                        st.success(f"✅ Query executed successfully. Returned {len(result_df)} rows.")
                        st.dataframe(result_df, use_container_width = True)
                        
                        # Показать информацию о результате
                        col_info1, col_info2, col_info3 = st.columns(3)
                        with col_info1:
                            st.metric("Rows", len(result_df))
                        with col_info2:
                            st.metric("Columns", len(result_df.columns))
                        with col_info3:
                            st.metric("Memory", f"{result_df.memory_usage(deep = True).sum() // 1024} KB")
                    
                    except Exception as e:
                        st.error(f"❌ Query error: {e}")
                else:
                    st.warning("Please enter a SQL query")
    
    with tab3:
        st.subheader("Data Analysis")
        
        try:
            # Автоматический анализ таблиц
            tables = pd.read_sql(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
            """, pg_conn
                )['table_name'].tolist()
            
            selected_table_analysis = st.selectbox("Select Table for Analysis", tables)
            
            if selected_table_analysis:
                data_df = pd.read_sql(f"SELECT * FROM {selected_table_analysis} LIMIT 1000", pg_conn)
                
                st.subheader("Basic Statistics")
                st.dataframe(data_df.describe(), use_container_width = True)
                
                st.subheader("Data Types")
                dtype_df = pd.DataFrame(
                        {'Column': data_df.columns, 'Data Type': data_df.dtypes.values,
                                'Non-Null Count': data_df.count().values, 'Null Count': data_df.isnull().sum().values}
                        )
                st.dataframe(dtype_df, use_container_width = True)
        
        except Exception as e:
            st.error(f"Error in data analysis: {e}")


def show_api_integration():
    st.header("🔗 FastAPI Integration")
    
    config = get_config()
    
    # Автоматическое обнаружение эндпоинтов
    endpoints = get_fastapi_endpoints()
    
    if not endpoints:
        st.error("Cannot connect to FastAPI or no endpoints found")
        st.info(f"Trying to connect to: {config['FASTAPI_URL']}")
        
        if st.button("Retry Connection"):
            st.rerun()
        return
    
    tab1, tab2, tab3 = st.tabs(["🚀 API Explorer", "📞 Manual Call", "📊 API Monitor"])
    
    with tab1:
        st.subheader("Automatically Discovered Endpoints")
        
        # Группировка по тегам
        tags = set()
        for endpoint in endpoints:
            tags.update(endpoint['tags'])
        
        selected_tag = st.selectbox("Filter by Tag", ["All"] + sorted(list(tags)))
        
        filtered_endpoints = endpoints
        if selected_tag != "All":
            filtered_endpoints = [ep for ep in endpoints if selected_tag in ep['tags']]
        
        for endpoint in filtered_endpoints:
            with st.expander(f"{endpoint['method']} {endpoint['path']}"):
                st.write(f"**Summary:** {endpoint['summary']}")
                st.write(f"**Tags:** {', '.join(endpoint['tags'])}")
                
                # Автоматический вызов GET эндпоинтов
                if endpoint['method'] == 'GET':
                    if st.button(f"Test {endpoint['path']}", key = f"test_{endpoint['path']}"):
                        with st.spinner(f"Calling {endpoint['path']}..."):
                            response, error = call_fastapi_endpoint(endpoint['path'], endpoint['method'])
                            
                            if error:
                                st.error(f"Error: {error}")
                            else:
                                st.success(f"Status: {response.status_code}")
                                try:
                                    if response.headers.get('content-type') == 'application/json':
                                        st.json(response.json())
                                    else:
                                        st.text(response.text)
                                except:
                                    st.text(response.text)
    
    with tab2:
        st.subheader("Manual API Call")
        
        col1, col2 = st.columns(2)
        with col1:
            method = st.selectbox("HTTP Method", ["GET", "POST", "PUT", "DELETE"])
            endpoint_path = st.text_input("Endpoint Path", value = "/api/")
        with col2:
            if method in ["POST", "PUT"]:
                json_body = st.text_area("JSON Body", height = 150, value = '{"key": "value"}')
            else:
                json_body = "{}"
        
        if st.button("Make API Call", type = "primary"):
            with st.spinner("Making API call..."):
                data = None
                if method in ["POST", "PUT"]:
                    try:
                        data = eval(json_body) if json_body else None
                    except:
                        st.error("Invalid JSON format")
                        return
                
                response, error = call_fastapi_endpoint(endpoint_path, method, data)
                
                if error:
                    st.error(f"❌ Error: {error}")
                else:
                    st.success(f"✅ Status Code: {response.status_code}")
                    
                    col_res1, col_res2 = st.columns(2)
                    with col_res1:
                        st.subheader("Response Headers")
                        headers_dict = dict(response.headers)
                        st.json(headers_dict)
                    
                    with col_res2:
                        st.subheader("Response Body")
                        try:
                            if response.headers.get('content-type', '').startswith('application/json'):
                                st.json(response.json())
                            else:
                                st.text(response.text)
                        except:
                            st.text(response.text)
    
    with tab3:
        st.subheader("API Health Monitoring")
        
        # Проверка здоровья всех сервисов
        services = [{"name": "FastAPI", "url": f"{config['FASTAPI_URL']}/docs"},
                {"name": "PostgreSQL", "url": "internal"}, {"name": "MongoDB", "url": "internal"}]
        
        for service in services:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                st.write(f"**{service['name']}**")
            with col2:
                if service['url'] == 'internal':
                    if service['name'] == 'PostgreSQL':
                        status = "✅ Healthy" if init_postgres_connection() else "❌ Unhealthy"
                    else:  # MongoDB
                        status = "✅ Healthy" if init_mongo_connection() else "❌ Unhealthy"
                else:
                    try:
                        response = requests.get(service['url'], timeout = 5)
                        status = "✅ Healthy" if response.status_code == 200 else "⚠️ Degraded"
                    except:
                        status = "❌ Unhealthy"
                st.write(status)
            with col3:
                st.write(f"`{service['url']}`")


def main():
    st.sidebar.title("🖼️ Admin Panel")
    st.sidebar.markdown("---")
    
    # Показ статуса подключений в сайдбаре
    pg_conn = init_postgres_connection()
    mongo_client = init_mongo_connection()
    
    with st.sidebar:
        st.subheader("Connection Status")
        if pg_conn and mongo_client:
            st.success("✅ All Systems Online")
        else:
            st.error("⚠️ Connection Issues")
        
        st.markdown("---")
    
    # Навигация
    page = st.sidebar.radio(
            "Navigation", ["📊 Dashboard", "🖼️ Image Management", "📈 Data Management", "🔗 API Integration"], index = 0
            )
    
    # Показ конфигурации в сайдбаре
    with st.sidebar.expander("⚙️ Configuration"):
        config = get_config()
        st.json({k: v for k, v in config.items() if "PASSWORD" not in k})
    
    st.sidebar.markdown("---")
    st.sidebar.info(
        """
    **Admin Panel Features:**
    - 📊 Real-time dashboard
    - 🖼️ Image management (MongoDB)
    - 📈 Data exploration (PostgreSQL)
    - 🔗 FastAPI integration
    - 🔍 Automatic endpoint discovery
    """
        )
    
    # Отображение выбранной страницы
    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "🖼️ Image Management":
        show_image_management()
    elif page == "📈 Data Management":
        show_data_management()
    elif page == "🔗 API Integration":
        show_api_integration()


if __name__ == "__main__":
    main()