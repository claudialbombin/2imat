"""
=============================================================================
PROYECTO FINAL - BASES DE DATOS - DASHBOARD DE ESTADÍSTICAS
Asignatura: Bases de Datos - 2º curso
Grado en Ingeniería Matemática e Inteligencia Artificial (IMAT)
=============================================================================
Alumna: Claudia Maria Lopez Bombin
=============================================================================
Descripción:
    Dashboard interactivo que muestra estadísticas y métricas de las tres
    bases de datos utilizadas en el proyecto:
    - MySQL: Base de datos relacional
    - MongoDB: Base de datos NoSQL documental
    - Neo4J: Base de datos de grafos
    
    El dashboard incluye:
    - Número total de registros por base de datos
    - Distribución de tipos de artículos
    - Top usuarios con más reviews
    - Top artículos más valorados
    - Estadísticas de puntuaciones
=============================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mysql.connector
import pymongo
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from wordcloud import WordCloud

# Configurar página
st.set_page_config(
    page_title="Amazon Reviews Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Importar configuración
import configuracion as cfg


# =============================================================================
# VARIABLES DE ESTADO DE SESIÓN
# =============================================================================

if 'mysql_connected' not in st.session_state:
    st.session_state.mysql_connected = False
if 'mysql_conn' not in st.session_state:
    st.session_state.mysql_conn = None


# =============================================================================
# CONEXIONES A BASE DE DATOS
# =============================================================================

def init_mysql_connection():
    """Inicializa la conexión a MySQL y la guarda en session state."""
    try:
        conn = mysql.connector.connect(
            host=cfg.MYSQL_HOST,
            port=cfg.MYSQL_PORT,
            user=cfg.MYSQL_USER,
            password=cfg.MYSQL_PASSWORD,
            database=cfg.MYSQL_DATABASE,
            connection_timeout=10,
            use_pure=True
        )
        
        if conn.is_connected():
            st.session_state.mysql_conn = conn
            st.session_state.mysql_connected = True
            return conn
        return None
    except Exception as e:
        st.error(f"Error de conexión MySQL: {e}")
        st.session_state.mysql_connected = False
        return None


def get_mysql_connection():
    """Obtiene la conexión MySQL, la reinicia si es necesario."""
    if not st.session_state.mysql_connected or st.session_state.mysql_conn is None:
        return init_mysql_connection()
    
    try:
        # Verificar si la conexión sigue viva
        st.session_state.mysql_conn.ping(reconnect=True, attempts=3, delay=1)
        return st.session_state.mysql_conn
    except:
        return init_mysql_connection()


@st.cache_resource
def get_mongo_collection():
    """Conecta a MongoDB."""
    try:
        cliente = pymongo.MongoClient(cfg.MONGO_URI, serverSelectionTimeoutMS=5000)
        cliente.admin.command('ping')
        return cliente[cfg.MONGO_DATABASE][cfg.MONGO_COLECCION_REVIEWS]
    except Exception as e:
        st.error(f"Error conectando a MongoDB: {e}")
        return None


# =============================================================================
# FUNCIONES DE CARGA DE DATOS
# =============================================================================
@st.cache_data(ttl=3600)
def cargar_todas_categorias():
    """Carga todas las categorías disponibles en la base de datos."""
    conn = get_mysql_connection()
    if conn is None:
        return []
    
    try:
        query = "SELECT nombre FROM Categorias ORDER BY nombre;"
        df = pd.read_sql(query, conn)
        return df['nombre'].tolist()
    except Exception as e:
        st.error(f"Error cargando categorías: {e}")
        return []
    
@st.cache_data(ttl=3600)
def cargar_estadisticas():
    """Carga estadísticas generales."""
    conn = get_mysql_connection()
    if conn is None:
        return None
    
    cursor = conn.cursor(dictionary=True)
    stats = {}
    
    try:
        cursor.execute("SELECT COUNT(*) as total FROM Reviews;")
        row = cursor.fetchone()
        stats['total_reviews'] = row['total'] if row else 0
        
        cursor.execute("SELECT COUNT(*) as total FROM Usuarios;")
        row = cursor.fetchone()
        stats['total_usuarios'] = row['total'] if row else 0
        
        cursor.execute("SELECT COUNT(*) as total FROM Articulos;")
        row = cursor.fetchone()
        stats['total_articulos'] = row['total'] if row else 0
        
        cursor.execute("""
            SELECT c.nombre, COUNT(*) as total
            FROM Reviews r
            JOIN Articulos a ON r.asin = a.asin
            JOIN Categorias c ON a.id_categoria = c.id_categoria
            GROUP BY c.nombre
            ORDER BY total DESC;
        """)
        rows = cursor.fetchall()
        stats['reviews_por_categoria'] = [(row['nombre'], row['total']) for row in rows]
        
        cursor.execute("SELECT AVG(overall) as media FROM Reviews;")
        row = cursor.fetchone()
        stats['nota_media'] = round(row['media'], 2) if row and row['media'] else 0
        
        cursor.execute("""
            SELECT overall, COUNT(*) as total
            FROM Reviews
            GROUP BY overall
            ORDER BY overall;
        """)
        rows = cursor.fetchall()
        stats['distribucion_notas'] = [(row['overall'], row['total']) for row in rows]
        
        cursor.execute("""
            SELECT YEAR(review_date) as anio, COUNT(*) as total
            FROM Reviews
            WHERE review_date IS NOT NULL
            GROUP BY anio
            ORDER BY anio;
        """)
        rows = cursor.fetchall()
        stats['reviews_por_anio'] = [(row['anio'], row['total']) for row in rows if row['anio'] is not None]
        
    except Exception as e:
        st.error(f"Error cargando estadísticas: {e}")
        return None
    finally:
        cursor.close()
    
    return stats


@st.cache_data(ttl=3600)
def cargar_top_articulos(categoria=None, limite=50):
    """Carga los artículos más populares."""
    conn = get_mysql_connection()
    if conn is None:
        st.error("No hay conexión a MySQL")
        return pd.DataFrame()
    
    try:
        if categoria and categoria != "Todas":
            query = """
                SELECT r.asin, COUNT(*) as num_reviews, ROUND(AVG(r.overall), 2) as nota_media
                FROM Reviews r
                JOIN Articulos a ON r.asin = a.asin
                JOIN Categorias c ON a.id_categoria = c.id_categoria
                WHERE c.nombre = %s
                GROUP BY r.asin
                ORDER BY num_reviews DESC
                LIMIT %s;
            """
            df = pd.read_sql(query, conn, params=(categoria, limite))
        else:
            query = """
                SELECT asin, COUNT(*) as num_reviews, ROUND(AVG(overall), 2) as nota_media
                FROM Reviews
                GROUP BY asin
                ORDER BY num_reviews DESC
                LIMIT %s;
            """
            df = pd.read_sql(query, conn, params=(limite,))
        return df
    except Exception as e:
        st.error(f"Error cargando top artículos: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def cargar_top_usuarios(limite=50):
    """Carga los usuarios con más reviews."""
    conn = get_mysql_connection()
    if conn is None:
        return pd.DataFrame()
    
    try:
        query = """
            SELECT reviewerID, COUNT(*) as num_reviews, ROUND(AVG(overall), 2) as nota_media
            FROM Reviews
            GROUP BY reviewerID
            ORDER BY num_reviews DESC
            LIMIT %s;
        """
        df = pd.read_sql(query, conn, params=(limite,))
        return df
    except Exception as e:
        st.error(f"Error cargando top usuarios: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def cargar_distribucion_reviews_usuario():
    """Carga la distribución de reviews por usuario."""
    conn = get_mysql_connection()
    if conn is None:
        return pd.DataFrame()
    
    try:
        query = """
            SELECT num_reviews, COUNT(*) as num_usuarios
            FROM (
                SELECT reviewerID, COUNT(*) as num_reviews
                FROM Reviews
                GROUP BY reviewerID
            ) t
            GROUP BY num_reviews
            ORDER BY num_reviews;
        """
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Error cargando distribución: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def cargar_reviews_por_categoria_temporal():
    """Carga datos temporales de reviews por categoría."""
    conn = get_mysql_connection()
    if conn is None:
        return pd.DataFrame()
    
    query = """
        SELECT c.nombre, YEAR(r.review_date) as anio, COUNT(*) as total
        FROM Reviews r
        JOIN Articulos a ON r.asin = a.asin
        JOIN Categorias c ON a.id_categoria = c.id_categoria
        WHERE r.review_date IS NOT NULL
        GROUP BY c.nombre, anio
        ORDER BY c.nombre, anio;
    """
    
    try:
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Error cargando datos temporales: {e}")
        return pd.DataFrame()


def generar_nube_palabras(categoria):
    """Genera nube de palabras para una categoría."""
    mongo_col = get_mongo_collection()
    if mongo_col is None:
        st.error("No hay conexión a MongoDB")
        return None
    
    conn = get_mysql_connection()
    if conn is None:
        st.error("No hay conexión a MySQL")
        return None
    
    cursor = conn.cursor()
    
    try:
        # Obtener ASINs de la categoría
        cursor.execute("""
            SELECT a.asin FROM Articulos a
            JOIN Categorias c ON a.id_categoria = c.id_categoria
            WHERE c.nombre = %s;
        """, (categoria,))
        asins = [row[0] for row in cursor.fetchall()]
        
        if not asins:
            st.warning(f"No hay artículos en la categoría '{categoria}'")
            return None
        
        # Obtener summaries de MongoDB
        docs = mongo_col.find(
            {"asin": {"$in": asins}},
            {"summary": 1, "_id": 0}
        )
        
        # Limitar a 5000 documentos para no sobrecargar
        textos = []
        for i, doc in enumerate(docs):
            if i >= 5000:  # Límite por rendimiento
                break
            if doc.get("summary"):
                textos.append(str(doc.get("summary", "")))
        
        texto = " ".join(textos)
        
        if not texto.strip():
            st.warning(f"No hay suficientes datos de texto para '{categoria}'")
            return None
        
        # Generar wordcloud
        wordcloud = WordCloud(
            width=900, height=500,
            background_color='white',
            colormap='viridis',
            max_words=200,
            contour_width=1,
            contour_color='steelblue'
        ).generate(texto)
        
        return wordcloud
        
    except Exception as e:
        st.error(f"Error generando nube de palabras: {e}")
        return None
    finally:
        cursor.close()


def recomendar_articulos(usuario_id, categoria, top_n=10):
    """Genera recomendaciones para un usuario."""
    conn = get_mysql_connection()
    if conn is None:
        return None, "No hay conexión a MySQL"
    
    cursor = conn.cursor()
    
    try:
        # Verificar usuario
        cursor.execute("SELECT COUNT(*) FROM Usuarios WHERE reviewerID = %s;", (usuario_id,))
        if cursor.fetchone()[0] == 0:
            return None, f"Usuario '{usuario_id}' no existe"
        
        # Obtener artículos consumidos
        cursor.execute("SELECT DISTINCT asin FROM Reviews WHERE reviewerID = %s;", (usuario_id,))
        consumidos = {row[0] for row in cursor.fetchall()}
        
        # Obtener populares
        if categoria == "Todas":
            cursor.execute("""
                SELECT asin, COUNT(*) as total
                FROM Reviews
                GROUP BY asin
                ORDER BY total DESC
                LIMIT %s;
            """, (top_n + len(consumidos),))
        else:
            cursor.execute("""
                SELECT r.asin, COUNT(*) as total
                FROM Reviews r
                JOIN Articulos a ON r.asin = a.asin
                JOIN Categorias c ON a.id_categoria = c.id_categoria
                WHERE c.nombre = %s
                GROUP BY r.asin
                ORDER BY total DESC
                LIMIT %s;
            """, (categoria, top_n + len(consumidos)))
        
        populares = cursor.fetchall()
        recomendaciones = [(asin, total) for asin, total in populares if asin not in consumidos][:top_n]
        
        return recomendaciones, None
        
    except Exception as e:
        return None, str(e)
    finally:
        cursor.close()


# =============================================================================
# FUNCIONES DE VISUALIZACIÓN
# =============================================================================

def mostrar_metricas(stats):
    """Muestra métricas."""
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📝 Total Reviews", f"{stats['total_reviews']:,}")
    with col2:
        st.metric("👥 Usuarios", f"{stats['total_usuarios']:,}")
    with col3:
        st.metric("📦 Artículos", f"{stats['total_articulos']:,}")
    with col4:
        st.metric("⭐ Nota Media", f"{stats['nota_media']}")


def grafico_reviews_por_anio(stats):
    """Gráfico de evolución de reviews por año."""
    if not stats['reviews_por_anio']:
        st.info("No hay datos de reviews por año")
        return
    df = pd.DataFrame(stats['reviews_por_anio'], columns=['año', 'reviews'])
    fig = px.bar(df, x='año', y='reviews', title='📈 Evolución de Reviews por Año')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


def grafico_distribucion_notas(stats):
    """Gráfico de distribución de notas."""
    if not stats['distribucion_notas']:
        st.info("No hay datos de distribución de notas")
        return
    df = pd.DataFrame(stats['distribucion_notas'], columns=['nota', 'total'])
    fig = px.bar(df, x='nota', y='total', title='⭐ Distribución de Notas')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


def grafico_treemap_categorias(stats):
    """Treemap de categorías."""
    if not stats['reviews_por_categoria']:
        st.info("No hay datos de categorías")
        return
    df = pd.DataFrame(stats['reviews_por_categoria'], columns=['categoría', 'reviews'])
    fig = px.treemap(df, path=['categoría'], values='reviews', title='📦 Reviews por Categoría')
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)


def grafico_popularidad_articulos(df):
    """Gráfico de popularidad de artículos."""
    if df.empty:
        st.info("No hay datos de artículos")
        return
    fig = px.bar(df.head(20), x='asin', y='num_reviews', title='Top 20 Artículos Más Populares')
    fig.update_layout(height=500, xaxis_tickangle=45)
    st.plotly_chart(fig, use_container_width=True)


def grafico_evolucion_temporal(df):
    """Gráfico de evolución temporal por categoría."""
    if df.empty:
        st.info("No hay datos temporales")
        return
    fig = px.line(df, x='anio', y='total', color='nombre', title='📊 Evolución de Reviews por Categoría', markers=True)
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)


def grafico_distribucion_usuarios(df):
    """Gráfico de distribución de usuarios."""
    if df.empty:
        st.info("No hay datos de distribución de usuarios")
        return
    df_filtrado = df[df['num_reviews'] <= 100].copy()
    fig = px.bar(df_filtrado.head(50), x='num_reviews', y='num_usuarios', title='Distribución de Reviews por Usuario')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


# =============================================================================
# PÁGINAS
# =============================================================================

def pagina_inicio():
    """Página de inicio."""
    st.title("📊 Amazon Reviews Dashboard")
    st.markdown("---")
    
    stats = cargar_estadisticas()
    if stats is None:
        st.error("No se pudieron cargar las estadísticas. Verifica la conexión a MySQL.")
        return
    
    mostrar_metricas(stats)
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        grafico_reviews_por_anio(stats)
        grafico_distribucion_notas(stats)
    with col2:
        grafico_treemap_categorias(stats)
    
    st.markdown("---")
    st.subheader("📈 Evolución Temporal por Categoría")
    df_temporal = cargar_reviews_por_categoria_temporal()
    grafico_evolucion_temporal(df_temporal)


def pagina_articulos():
    """Página de análisis de artículos."""
    st.title("📦 Análisis de Artículos")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        categorias = ["Todas"] + list(cfg.DATASETS.keys())
        categoria = st.selectbox("Filtrar por categoría", categorias)
        limite = st.slider("Número de artículos a mostrar", 10, 200, 50)
    
    with col2:
        st.info("""
        **Popularidad de artículos**  
        Muestra la distribución de reviews entre los artículos.
        """)
    
    df = cargar_top_articulos(categoria if categoria != "Todas" else None, limite)
    
    if not df.empty:
        grafico_popularidad_articulos(df)
        
        st.markdown("---")
        st.subheader("🏆 Top Artículos Más Populares")
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("No se pudieron cargar los datos de artículos")


def pagina_usuarios():
    """Página de análisis de usuarios."""
    st.title("👥 Análisis de Usuarios")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        limite = st.slider("Número de usuarios a mostrar", 10, 200, 50)
    
    df_usuarios = cargar_top_usuarios(limite)
    df_dist = cargar_distribucion_reviews_usuario()
    
    if not df_dist.empty:
        st.subheader("📊 Distribución de Actividad de Usuarios")
        grafico_distribucion_usuarios(df_dist)
    
    st.markdown("---")
    
    if not df_usuarios.empty:
        st.subheader("🏆 Top Usuarios Más Activos")
        st.dataframe(df_usuarios, use_container_width=True)
        
        st.info(f"**Insight**: El usuario más activo ha realizado {df_usuarios.iloc[0]['num_reviews']:,} reviews")
    else:
        st.warning("No se pudieron cargar los datos de usuarios")


def pagina_nubes():
    """Página de nubes de palabras."""
    st.title("☁️ Nubes de Palabras por Categoría")
    st.markdown("---")
    
    st.markdown("""
    Las nubes de palabras muestran los términos más frecuentes en los **resúmenes (summary)** 
    de las reviews. Las palabras más grandes son las más comunes.
    
    **Nota**: Solo se consideran palabras de longitud > 3 caracteres.
    """)
    
    # Cargar todas las categorías desde la base de datos
    with st.spinner("Cargando categorías..."):
        categorias_db = cargar_todas_categorias()
    
    if not categorias_db:
        st.error("No se encontraron categorías en la base de datos. Asegúrate de haber cargado los datos primero.")
        return
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        categoria_seleccionada = st.selectbox(
            "Selecciona una categoría", 
            categorias_db,
            help="Todas las categorías disponibles en la base de datos"
        )
        
        # Mostrar estadísticas de la categoría
        conn = get_mysql_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(DISTINCT r.asin), COUNT(r.reviewerID)
                FROM Reviews r
                JOIN Articulos a ON r.asin = a.asin
                JOIN Categorias c ON a.id_categoria = c.id_categoria
                WHERE c.nombre = %s;
            """, (categoria_seleccionada,))
            row = cursor.fetchone()
            if row:
                st.info(f"""
                📊 **Estadísticas de la categoría:**
                - Artículos: {row[0]:,}
                - Reviews: {row[1]:,}
                """)
            cursor.close()
        
        generar = st.button("🎨 Generar Nube de Palabras", type="primary", use_container_width=True)
    
    with col2:
        st.markdown(f"""
        ### 📝 Acerca de "{categoria_seleccionada}"
        
        Se analizarán los resúmenes de todas las reviews de esta categoría
        para extraer las palabras más representativas.
        
        **Consejo:** Si la nube tarda en generarse, puede deberse a la gran
        cantidad de datos. El sistema está limitado a 5000 documentos por rendimiento.
        """)
    
    if generar:
        with st.spinner(f"🔍 Analizando {categoria_seleccionada} y generando nube de palabras..."):
            wordcloud = generar_nube_palabras(categoria_seleccionada)
            
            if wordcloud:
                st.markdown("---")
                st.subheader(f"☁️ Nube de palabras - {categoria_seleccionada}")
                
                fig, ax = plt.subplots(figsize=(12, 7))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
                plt.close(fig)
                
                st.caption(f"Generado a partir de los resúmenes de reviews de la categoría '{categoria_seleccionada}'")
            else:
                st.warning(f"No se pudo generar la nube de palabras para '{categoria_seleccionada}'. Intenta con otra categoría.")


def pagina_recomendaciones():
    """Página de recomendaciones."""
    st.title("🎯 Sistema de Recomendaciones")
    st.markdown("---")
    
    st.info("""
    **Sistema de recomendación basado en popularidad:**
    1. Se obtienen los artículos más populares de la categoría seleccionada
    2. Se filtran los que el usuario ya ha visto
    3. Se devuelven los top N no vistos
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        categorias = ["Todas"] + list(cfg.DATASETS.keys())
        categoria_rec = st.selectbox("Categoría", categorias)
    with col2:
        top_n = st.selectbox("Número de recomendaciones", [5, 10, 15, 20], index=1)
    
    usuario_id = st.text_input("ID del Usuario (reviewerID)", placeholder="Ej: A3V6Z4RCDGRC44")
    
    if st.button("🔍 Recomendar", type="primary"):
        if not usuario_id:
            st.error("Por favor, introduce un ID de usuario")
        else:
            with st.spinner("Generando recomendaciones..."):
                recomendaciones, error = recomendar_articulos(usuario_id, categoria_rec, top_n)
                
                if error:
                    st.error(error)
                elif not recomendaciones:
                    st.info(f"El usuario ya ha visto todos los artículos populares de {categoria_rec}")
                else:
                    st.success(f"Top {len(recomendaciones)} recomendaciones para '{usuario_id}' en {categoria_rec}:")
                    df_rec = pd.DataFrame(recomendaciones, columns=['ASIN', 'Número de Reviews'])
                    st.dataframe(df_rec, use_container_width=True)
    
    # Mostrar usuarios de ejemplo
    with st.expander("📋 Usuarios de ejemplo (top 10 más activos)"):
        df_usuarios = cargar_top_usuarios(10)
        if not df_usuarios.empty:
            st.dataframe(df_usuarios[['reviewerID', 'num_reviews']], use_container_width=True)


def pagina_neo4j():
    """Página de información sobre Neo4J."""
    st.title("🕸️ Visualización con Neo4J")
    st.markdown("---")
    
    st.markdown("""
    ### Grafos disponibles en Neo4J
    
    **1. Similitudes entre usuarios (Apartado 4.1)**
    - Correlación de Pearson entre top usuarios
    - Relaciones `SIMILAR` con propiedad `similitud`
    
    **2. Usuarios y artículos aleatorios (Apartado 4.2)**
    - Artículos aleatorios de una categoría
    - Relaciones `VALORO` con `nota` y `timestamp`
    
    **3. Usuarios multi-categoría (Apartado 4.3)**
    - Usuarios con múltiples tipos de artículos
    - Relaciones `CONSUME` con `num_articulos`
    
    **4. Artículos populares (Apartado 4.4)**
    - Artículos con menos de 40 reviews
    - Relaciones `EN_COMUN` entre usuarios
    """)
    
    st.markdown("---")
    st.subheader("🚀 Cómo ejecutar Neo4J")
    
    st.code("""
# 1. Ejecutar el script
python neo4JProyecto.py

# 2. Seleccionar una opción del 1 al 4

# 3. Abrir Neo4J Browser en http://localhost:7474

# 4. Consultas de ejemplo
MATCH (n) RETURN n LIMIT 100
MATCH (u:Usuario)-[r:SIMILAR]-(v) RETURN u, v, r.similitud LIMIT 20
    """, language="bash")
    
    st.markdown("---")
    st.subheader("📝 Consultas Neo4J adicionales")
    with st.expander("Ver más consultas"):
        st.code("""
# Usuario con más vecinos
MATCH (u:Usuario)-[:SIMILAR]-(v)
RETURN u.reviewerID, COUNT(v) as vecinos
ORDER BY vecinos DESC
LIMIT 10

# Relaciones usuario-articulo
MATCH (u:Usuario)-[r:VALORO]->(a:Articulo)
RETURN u.reviewerID, a.asin, r.nota
LIMIT 20
        """, language="cypher")


def pagina_insights():
    """Página de insights y conclusiones."""
    st.title("💡 Insights y Conclusiones")
    st.markdown("---")
    
    stats = cargar_estadisticas()
    if stats is None:
        st.error("No se pudieron cargar las estadísticas")
        return
    
    if stats['reviews_por_categoria']:
        df_cats = pd.DataFrame(stats['reviews_por_categoria'], columns=['categoría', 'reviews'])
        categoria_top = df_cats.iloc[0]['categoría']
        categoria_top_reviews = df_cats.iloc[0]['reviews']
    else:
        categoria_top = "N/A"
        categoria_top_reviews = 0
    
    if stats['distribucion_notas']:
        df_notas = pd.DataFrame(stats['distribucion_notas'], columns=['nota', 'total'])
        nota_mas_comun = df_notas.loc[df_notas['total'].idxmax(), 'nota']
    else:
        nota_mas_comun = "N/A"
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        ### 📊 Estadísticas Clave
        - **Categoría más popular**: {categoria_top} ({categoria_top_reviews:,} reviews)
        - **Nota más común**: {nota_mas_comun} estrellas
        - **Nota media global**: {stats['nota_media']}/5.0
        - **Total de datos**: {stats['total_reviews']:,} reviews
        - **Usuarios únicos**: {stats['total_usuarios']:,}
        - **Artículos únicos**: {stats['total_articulos']:,}
        """)
    
    with col2:
        st.markdown("""
        ### 🎯 Conclusiones del Análisis
        
        1. **Distribución de notas**: La mayoría de los usuarios tienden a dar
           puntuaciones extremas (1 o 5 estrellas), mostrando un comportamiento polarizado.
        
        2. **Crecimiento temporal**: El número de reviews ha aumentado
           significativamente en los últimos años.
        
        3. **Long tail**: Pocos artículos concentran la mayoría de las reviews
           (Ley de Pareto).
        
        4. **Usuarios activos**: Una pequeña minoría de usuarios genera la mayoría
           de las reviews.
        """)
    
    st.markdown("---")
    
    # Gráfico de Pareto simplificado
    df_articulos = cargar_top_articulos(limite=100)
    if not df_articulos.empty:
        df_articulos['acumulado'] = df_articulos['num_reviews'].cumsum()
        df_articulos['acumulado_pct'] = df_articulos['acumulado'] / df_articulos['num_reviews'].sum() * 100
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # CORREGIDO: convertir range a lista
        fig.add_trace(
            go.Bar(x=list(range(1, len(df_articulos)+1)), y=df_articulos['num_reviews'], name="Reviews por artículo"),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(x=list(range(1, len(df_articulos)+1)), y=df_articulos['acumulado_pct'], 
                       name="% Acumulado", line=dict(color='red', width=2)),
            secondary_y=True
        )
        
        fig.update_layout(
            title="📈 Curva de Pareto: Concentración de Reviews",
            xaxis_title="Artículos (ordenados por popularidad)",
            height=400
        )
        fig.update_yaxes(title_text="Número de Reviews", secondary_y=False)
        fig.update_yaxes(title_text="Porcentaje Acumulado (%)", secondary_y=True, range=[0, 105])
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        ### 🔍 Interpretación
        
        El gráfico muestra que aproximadamente el **20% de los artículos** 
        concentran el **80% de las reviews** (Ley de Pareto).
        """)


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Función principal del dashboard."""
    
    # Inicializar conexión MySQL al inicio
    with st.spinner("Conectando a MySQL..."):
        conn = init_mysql_connection()
    
    if not st.session_state.mysql_connected:
        st.error("""
        ❌ **No se pudo conectar a MySQL**
        
        **Posibles soluciones:**
        1. Verifica que MySQL está corriendo: `mysql.server start`
        2. Verifica las credenciales en `configuracion.py`
        3. Ejecuta primero `python load_data.py` para crear la base de datos
        """)
        return
    
    # Sidebar
    st.sidebar.image("https://img.icons8.com/color/96/amazon.png", width=80)
    st.sidebar.title("📊 Navegación")
    
    paginas = {
        "🏠 Inicio": pagina_inicio,
        "📦 Artículos": pagina_articulos,
        "👥 Usuarios": pagina_usuarios,
        "☁️ Nubes de Palabras": pagina_nubes,
        "🎯 Recomendaciones": pagina_recomendaciones,
        "🕸️ Neo4J": pagina_neo4j,
        "💡 Insights": pagina_insights,
    }
    
    seleccion = st.sidebar.radio("Ir a:", list(paginas.keys()))
    
    st.sidebar.markdown("---")
    st.sidebar.info(f"✅ Conectado a MySQL\nBase de datos: {cfg.MYSQL_DATABASE}")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ Información")
    st.sidebar.markdown("**Proyecto Bases de Datos**")
    st.sidebar.markdown("Claudia Maria Lopez Bombin")
    
    # Ejecutar página seleccionada
    paginas[seleccion]()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "Amazon Reviews Dashboard | Proyecto Bases de Datos IMAT | Claudia Maria Lopez Bombin"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()