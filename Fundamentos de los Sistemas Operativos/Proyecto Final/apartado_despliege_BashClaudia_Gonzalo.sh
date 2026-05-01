#!/bin/bash
# =============================================================================
# SCRIPT: apartado_despliegue_BashClaudia_Gonzalo.sh
# DESCRIPCIÓN: Script completo para despliegue automático del proyecto Flask
#              Cumple con TODOS los requisitos del segundo ejercicio
# USO: Ejecutar como usuario alumnoimat después de apartado1Claudia_Gonzalo.sh
# AUTOR: Claudia Maria Lopez Bombin Y Gonzalo Velasco Lucas
# FECHA: Noviembre 2025
# =============================================================================

# =============================================================================
# CONFIGURACIÓN Y DECLARACIÓN DE VARIABLES
# =============================================================================

# Configuración del proyecto
PROJECT_DIR="ProyectoFUSO"
REPO_URL="https://github.com/pablosanchezp/ProyectoFUSO.git"
VENV_DIR="venv"
FLASK_APP="main.py"
FLASK_PORT="5000"

# =============================================================================
# PASO 1: VERIFICACIONES INICIALES
# =============================================================================

echo "=== DESPLIEGUE AUTOMÁTICO DEL PROYECTO FLASK ==="
echo "Fecha: $(date)"
echo "Usuario actual: $(whoami)"
echo "Directorio actual: $(pwd)"
echo ""

# Verificar que estamos ejecutando como alumnoimat (REQUISITO del enunciado)
if [ "$(whoami)" != "alumnoimat" ]; then
    echo "ERROR: Este script debe ejecutarse con el usuario 'alumnoimat'"
    echo "Por favor, cambia de usuario con: sudo su - alumnoimat"
    exit 1
fi

# Verificar que estamos en Alpine Linux
if ! command -v apk &> /dev/null; then
    echo "ADVERTENCIA: No parece que estés en Alpine Linux"
    echo "El comando 'apk' no está disponible."
    echo "Este script está optimizado para Alpine Linux."
    read -p "¿Continuar de todos modos? (s/n): " respuesta
    if [ "$respuesta" != "s" ] && [ "$respuesta" != "S" ]; then
        exit 1
    fi
fi

# =============================================================================
# PASO 2: INSTALAR DEPENDENCIAS DEL SISTEMA
# =============================================================================

echo "Paso 1: Instalando dependencias del sistema..."
echo "----------------------------------------------"

# Instalar Python3 y pip si no están instalados
if ! command -v python3 &> /dev/null; then
    echo "Instalando python3..."
    sudo apk add python3
else
    echo "python3 ya está instalado"
fi

if ! command -v pip3 &> /dev/null; then
    echo "Instalando pip..."
    sudo apk add py3-pip
else
    echo "pip ya está instalado"
fi

# Instalar git si no está instalado
if ! command -v git &> /dev/null; then
    echo "Instalando git..."
    sudo apk add git
else
    echo "git ya está instalado"
fi

echo ""

# =============================================================================
# PASO 3: CLONAR REPOSITORIO DEL PROYECTO
# =============================================================================

echo "Paso 2: Clonando repositorio del proyecto..."
echo "--------------------------------------------"

# Verificar si el directorio del proyecto ya existe
if [ -d "$PROJECT_DIR" ]; then
    echo "El directorio $PROJECT_DIR ya existe."
    read -p "¿Deseas actualizar el proyecto (u) o eliminar y clonar de nuevo (r)? (u/r): " opcion
    
    if [ "$opcion" = "r" ] || [ "$opcion" = "R" ]; then
        echo "Eliminando directorio existente..."
        rm -rf "$PROJECT_DIR"
        echo "Clonando repositorio desde $REPO_URL ..."
        git clone "$REPO_URL"
    else
        echo "Actualizando repositorio existente..."
        cd "$PROJECT_DIR"
        git pull
        cd ..
    fi
else
    echo "Clonando repositorio desde $REPO_URL ..."
    git clone "$REPO_URL"
    
    # Verificar que el clon fue exitoso
    if [ ! -d "$PROJECT_DIR" ]; then
        echo "ERROR: No se pudo clonar el repositorio"
        echo "Verifica la URL: $REPO_URL"
        echo "Verifica la conexión a internet"
        exit 1
    fi
fi

echo "Repositorio listo en: $PROJECT_DIR"
echo ""

# =============================================================================
# PASO 4: CREAR Y ACTIVAR ENTORNO VIRTUAL
# =============================================================================

echo "Paso 3: Configurando entorno virtual de Python..."
echo "--------------------------------------------------"

# Verificar si el entorno virtual ya existe
if [ -d "$VENV_DIR" ]; then
    echo "El entorno virtual $VENV_DIR ya existe."
    read -p "¿Deseas recrearlo? (s/n): " respuesta
    if [ "$respuesta" = "s" ] || [ "$respuesta" = "S" ]; then
        echo "Eliminando entorno virtual existente..."
        rm -rf "$VENV_DIR"
        echo "Creando nuevo entorno virtual..."
        python3 -m venv "$VENV_DIR"
    fi
else
    echo "Creando entorno virtual en: $VENV_DIR"
    python3 -m venv "$VENV_DIR"
fi

# Verificar que el entorno virtual se creó correctamente
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "ERROR: No se pudo crear el entorno virtual"
    exit 1
fi

echo "Activando entorno virtual..."
source "$VENV_DIR/bin/activate"

# Mostrar información del entorno activado
echo "Python en uso: $(which python3)"
echo "Pip en uso: $(which pip)"
echo ""

# =============================================================================
# PASO 5: INSTALAR DEPENDENCIAS PYTHON
# =============================================================================

echo "Paso 4: Instalando dependencias Python..."
echo "----------------------------------------"

# Actualizar pip primero
echo "Actualizando pip..."
pip install --upgrade pip

# Verificar si existe requirements.txt en el proyecto
if [ -f "$PROJECT_DIR/requirements.txt" ]; then
    echo "Instalando dependencias desde $PROJECT_DIR/requirements.txt"
    pip install -r "$PROJECT_DIR/requirements.txt"
    
    # Verificar si hubo errores
    if [ $? -ne 0 ]; then
        echo "ADVERTENCIA: Hubo errores al instalar desde requirements.txt"
        echo "Instalando dependencias básicas manualmente..."
        
        # Instalar dependencias básicas una por una
        pip install flask==2.3.3
        pip install Werkzeug==2.3.7
        pip install scikit-learn==1.3.0
        pip install pandas
        pip install numpy
        pip install matplotlib
        pip install seaborn
        pip install requests
    fi
else
    echo "No se encontró requirements.txt en el proyecto"
    echo "Instalando dependencias básicas..."
    
    # Instalar dependencias según lo mencionado en el enunciado
    pip install flask==2.3.3
    pip install Werkzeug==2.3.7
    pip install scikit-learn==1.4.0  # Versión mencionada en el enunciado
    pip install pandas
    pip install numpy
    pip install matplotlib
    pip install seaborn
    pip install requests
    
    # Dependencias adicionales para funcionalidades específicas
    pip install memory-profiler  # Para compare_execution
    pip install joblib          # Para procesamiento paralelo
fi

echo ""
echo "Verificando instalación de dependencias críticas..."
# Verificar que las dependencias críticas estén instaladas
for paquete in flask scikit-learn pandas numpy; do
    if python3 -c "import $paquete; print('✓ $paquete instalado')" 2>/dev/null; then
        echo "  $paquete: OK"
    else
        echo "  $paquete: FALLO"
    fi
done

echo ""

# =============================================================================
# PASO 6: CONFIGURAR DIRECTORIOS NECESARIOS
# =============================================================================

echo "Paso 5: Configurando estructura de directorios..."
echo "-------------------------------------------------"

# Crear directorios necesarios si no existen
echo "Creando directorios necesarios para la aplicación..."

# Directorio para imágenes estáticas (requerido por Flask)
if [ ! -d "$PROJECT_DIR/static" ]; then
    echo "  Creando: $PROJECT_DIR/static"
    mkdir -p "$PROJECT_DIR/static"
else
    echo "  $PROJECT_DIR/static ya existe"
fi

# Directorio para templates HTML
if [ ! -d "$PROJECT_DIR/templates" ]; then
    echo "  Creando: $PROJECT_DIR/templates"
    mkdir -p "$PROJECT_DIR/templates"
else
    echo "  $PROJECT_DIR/templates ya existe"
fi

# Directorio para archivos HTML de mapas (mencionado en el enunciado)
if [ ! -d "$PROJECT_DIR/templates/html_files" ]; then
    echo "  Creando: $PROJECT_DIR/templates/html_files"
    mkdir -p "$PROJECT_DIR/templates/html_files"
else
    echo "  $PROJECT_DIR/templates/html_files ya existe"
fi

# Asegurar permisos adecuados
echo "Ajustando permisos..."
chmod 755 "$PROJECT_DIR"
chmod 755 "$PROJECT_DIR/static"
chmod 755 "$PROJECT_DIR/templates"

echo ""

# =============================================================================
# PASO 7: VERIFICAR ESTRUCTURA DEL PROYECTO
# =============================================================================

echo "Paso 6: Verificando estructura del proyecto..."
echo "---------------------------------------------"

cd "$PROJECT_DIR"

# Verificar archivos esenciales
echo "Verificando archivos esenciales:"

archivos_esenciales=("$FLASK_APP" "app.py" "src/model.py")
for archivo in "${archivos_esenciales[@]}"; do
    if [ -f "$archivo" ]; then
        echo "  $archivo encontrado"
    else
        echo "  $archivo NO encontrado"
    fi
done

# Verificar estructura de directorios
echo "Estructura del proyecto:"
ls -la

echo ""

# =============================================================================
# PASO 8: INFORMACIÓN IMPORTANTE PARA EL USUARIO
# =============================================================================

echo "Paso 7: Mostrando información de acceso..."
echo "-----------------------------------------"

# Obtener IP de la máquina (útil para acceso desde host)
echo "INFORMACIÓN DE CONEXIÓN:"
echo "========================"

# Intentar obtener la IP de la máquina
if command -v ip &> /dev/null; then
    IP_MAQUINA=$(ip addr show eth0 | grep "inet " | awk '{print $2}' | cut -d/ -f1)
elif command -v ifconfig &> /dev/null; then
    IP_MAQUINA=$(ifconfig eth0 | grep "inet " | awk '{print $2}')
else
    IP_MAQUINA="localhost"
fi

if [ -z "$IP_MAQUINA" ]; then
    IP_MAQUINA="localhost"
fi

echo "IP de la máquina Alpine: $IP_MAQUINA"
echo "Puerto Flask: $FLASK_PORT"
echo ""
echo "URLs de acceso desde tu navegador:"
echo "  • Local: http://localhost:$FLASK_PORT"
echo "  • Desde host: http://$IP_MAQUINA:$FLASK_PORT"
echo ""
echo "SERVICIOS DISPONIBLES (según el enunciado):"
echo "==========================================="
echo "1. Train and Evaluate:"
echo "   URL: http://$IP_MAQUINA:$FLASK_PORT/train"
echo "   Descripción: Entrena modelos ML con diferentes datasets"
echo ""
echo "2. Dataset Statistics:"
echo "   URL: http://$IP_MAQUINA:$FLASK_PORT/statistics/<dataset>"
echo "   Ejemplo: http://$IP_MAQUINA:$FLASK_PORT/statistics/iris"
echo "   Datasets disponibles: iris, wine, breast_cancer"
echo ""
echo "3. Exploratory Data Analysis:"
echo "   URL: http://$IP_MAQUINA:$FLASK_PORT/eda/<dataset>"
echo "   Ejemplo: http://$IP_MAQUINA:$FLASK_PORT/eda/iris"
echo ""
echo "4. Clean Images:"
echo "   URL: http://$IP_MAQUINA:$FLASK_PORT/clean_images"
echo "   Descripción: Elimina imágenes generadas anteriormente"
echo ""
echo "5. Generate Synthetic Dataset:"
echo "   URL: http://$IP_MAQUINA:$FLASK_PORT/generate_synthetic"
echo "   Descripción: Genera dataset artificial para pruebas"
echo ""
echo "6. Compare Execution:"
echo "   URL: http://$IP_MAQUINA:$FLASK_PORT/compare_execution"
echo "   Descripción: Compara tiempo secuencial vs paralelo"
echo "   NOTA: Requiere el código de multiplicación de matrices"
echo ""
echo "7. Show HTML files:"
echo "   URL: http://$IP_MAQUINA:$FLASK_PORT/show_html_files"
echo "   Descripción: Muestra mapas HTML generados"
echo ""
echo "==========================================="
echo ""

# =============================================================================
# PASO 9: INICIAR LA APLICACIÓN FLASK
# =============================================================================

echo "Paso 8: Iniciando la aplicación Flask..."
echo "---------------------------------------"
echo "Directorio actual: $(pwd)"
echo "Comando: python $FLASK_APP"
echo ""
echo "IMPORTANTE:"
echo "==========="
echo "1. La aplicación se ejecutará en primer plano"
echo "2. Para detenerla, presiona Ctrl+C"
echo "3. Los logs se mostrarán en esta terminal"
echo "4. Puede tardar unos segundos en iniciarse"
echo ""
echo "INICIANDO APLICACIÓN FLASK..."
echo "=============================="

# Verificar que estamos en el directorio correcto
if [ ! -f "$FLASK_APP" ]; then
    echo "ERROR: No se encuentra $FLASK_APP en $(pwd)"
    echo "Saliendo..."
    exit 1
fi

# Iniciar la aplicación Flask con los parámetros requeridos
# host="0.0.0.0" permite acceso desde otras máquinas
# debug=True para desarrollo (se desactiva en producción)
# port=5000 según el enunciado

python "$FLASK_APP"

# =============================================================================
# NOTAS FINALES (se mostrarán si la aplicación se detiene)
# =============================================================================

echo ""
echo "==========================================="
echo "APLICACIÓN DETENIDA"
echo "==========================================="
echo ""
echo "Para reiniciar la aplicación:"
echo "1. Asegúrate de estar en el directorio $PROJECT_DIR"
echo "2. Activa el entorno virtual: source ../$VENV_DIR/bin/activate"
echo "3. Ejecuta: python $FLASK_APP"
echo ""
echo "Para pruebas adicionales:"
echo "- Revisa los archivos generados en: static/"
echo "- Verifica los logs en la terminal"
echo "- Prueba cada servicio desde tu navegador"
echo ""
echo "FIN DEL SCRIPT"
echo "==========================================="