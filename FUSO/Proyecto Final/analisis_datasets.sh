#!/bin/bash
# =============================================================================
# SCRIPT: analisis_datasets.sh
# DESCRIPCIÓN: Script completo para descargar, procesar y analizar datasets Gowalla
#              Cumple con TODOS los requisitos del tercer ejercicio
# AUTOR: Claudia Maria Lopez Bombin Y Gonzalo Velasco Lucas
# FECHA: Noviembre 2025
# =============================================================================

# =============================================================================
# CONFIGURACIÓN (SEGÚN ENUNCIADO - TODO EN UNA LÍNEA)
# =============================================================================
URL="https://drive.google.com/uc?export=download&id=1PHWBGuwDHw4ZEIlCbgMTiEUrG8FmlJK2"
PATH_GOWALLA_FILES="DatasetsGowalla/"
ARCHIVO_ZIP="DatasetsGowalla.zip"
PROJECT_DIR="ProyectoFUSO"
HTML_DIR="$PROJECT_DIR/templates/html_files"

echo "=== ANÁLISIS DE DATASETS GOWALLA ==="
echo "Fecha: $(date)"
echo "Usuario: $(whoami)"
echo ""

# =============================================================================
# PASO 1: CREAR DIRECTORIOS NECESARIOS
# =============================================================================
echo "Paso 1: Creando directorios necesarios..."
echo "----------------------------------------"

mkdir -p "$PATH_GOWALLA_FILES"
mkdir -p "$HTML_DIR"
mkdir -p "$PROJECT_DIR/static"

echo "Directorios creados:"
echo "  - $PATH_GOWALLA_FILES"
echo "  - $HTML_DIR"
echo "  - $PROJECT_DIR/static"
echo ""

# =============================================================================
# PASO 2: DESCARGAR DATASET (SI NO EXISTE)
# =============================================================================
echo "Paso 2: Descargando dataset..."
echo "------------------------------"

if [ ! -f "$ARCHIVO_ZIP" ]; then
    echo "Descargando dataset desde Google Drive..."
    echo "URL: $URL"
    wget --no-check-certificate "$URL" -O "$ARCHIVO_ZIP"
    
    if [ $? -eq 0 ]; then
        echo "Dataset descargado correctamente: $ARCHIVO_ZIP"
        echo "Tamaño: $(du -h "$ARCHIVO_ZIP" | cut -f1)"
    else
        echo "ERROR: No se pudo descargar el dataset"
        echo "  Verifica tu conexión a internet"
        echo "  Verifica que la URL sea correcta"
        exit 1
    fi
else
    echo "El archivo $ARCHIVO_ZIP ya existe"
    echo "  Tamaño: $(du -h "$ARCHIVO_ZIP" | cut -f1)"
fi
echo ""

# =============================================================================
# PASO 3: DESCOMPRIMIR DATASET
# =============================================================================
echo "Paso 3: Descomprimiendo dataset..."
echo "----------------------------------"

if [ -f "$ARCHIVO_ZIP" ]; then
    echo "Descomprimiendo $ARCHIVO_ZIP en $PATH_GOWALLA_FILES..."
    unzip -o "$ARCHIVO_ZIP" -d "$PATH_GOWALLA_FILES"
    
    if [ $? -eq 0 ]; then
        echo "Dataset descomprimido correctamente"
        echo "Archivos extraídos:"
        ls -la "$PATH_GOWALLA_FILES" | grep "Gowalla.txt"
    else
        echo "ERROR: No se pudo descomprimir el archivo"
        exit 1
    fi
else
    echo "ERROR: No se encuentra el archivo $ARCHIVO_ZIP"
    exit 1
fi
echo ""

# =============================================================================
# PASO 4: INICIALIZAR ARCHIVO ALL_LOCATIONS.txt
# =============================================================================
echo "Paso 4: Creando archivo ALL_LOCATIONS.txt..."
echo "--------------------------------------------"

> ALL_LOCATIONS.txt  # Vaciar o crear el archivo
echo "Archivo ALL_LOCATIONS.txt creado/vaciado"
echo ""

# =============================================================================
# PASO 5: PROCESAR CADA CIUDAD
# =============================================================================
echo "Paso 5: Procesando cada ciudad..."
echo "---------------------------------"

ciudades=("ElPaso" "Glasgow" "Manchester" "WashingtonDC")

for ciudad in "${ciudades[@]}"; do
    echo ""
    echo "========================================"
    echo "CIUDAD: $ciudad"
    echo "========================================"
    
    # Definir nombres de archivos
    archivo_original="${PATH_GOWALLA_FILES}${ciudad}Gowalla.txt"
    archivo_filtrado="${ciudad}filtered.txt"
    
    # Verificar que el archivo original existe
    if [ ! -f "$archivo_original" ]; then
        echo "ERROR: No se encuentra el archivo $archivo_original"
        continue  # Saltar a la siguiente ciudad
    fi
    
    echo "Archivo original: $archivo_original"
    echo "Archivo filtrado: $archivo_filtrado"
    echo ""
    
    # -------------------------------------------------------------------------
    # TAREA A: Extraer columnas a archivos correspondientes
    # -------------------------------------------------------------------------
    echo "A. Extrayendo columnas..."
    
    # Columnas 3,4,5 → ALL_LOCATIONS.txt
    echo "  - Columnas 3,4,5 → ALL_LOCATIONS.txt"
    cut -f3,4,5 "$archivo_original" >> "ALL_LOCATIONS.txt"
    
    # Columnas 1,2,5 → archivo filtrado de la ciudad
    echo "  - Columnas 1,2,5 → $archivo_filtrado"
    cut -f1,2,5 "$archivo_original" > "$archivo_filtrado"
    
    # -------------------------------------------------------------------------
    # TAREA B: Mostrar estadísticas con comandos Bash
    # -------------------------------------------------------------------------
    echo ""
    echo "B. Estadísticas con comandos Bash:"
    echo "  ---------------------------------"
    
    # Número de usuarios distintos (columna 1)
    usuarios_distintos=$(cut -f1 "$archivo_original" | sort | uniq | wc -l)
    echo "  Número de usuarios distintos: $usuarios_distintos"
    
    # Número de lugares distintos (columna 5)
    lugares_distintos=$(cut -f5 "$archivo_original" | sort | uniq | wc -l)
    echo "  Número de lugares distintos: $lugares_distintos"
    
    # Número de filas completas (todas las líneas)
    filas_completas=$(wc -l < "$archivo_original")
    echo "  Número de filas completas: $filas_completas"
    
    # Número de check-ins en julio 2010 (columna 2 empieza con "2010-07")
    checkins_julio=$(cut -f2 "$archivo_original" | grep -c '^2010-07')
    echo "  Número de check-ins en 2010-07: $checkins_julio"
    
    # Número de check-ins en agosto 2010 (columna 2 empieza con "2010-08")
    checkins_agosto=$(cut -f2 "$archivo_original" | grep -c '^2010-08')
    echo "  Número de check-ins en 2010-08: $checkins_agosto"
    
    # -------------------------------------------------------------------------
    # TAREA C: Llamar al script Python para comparar estadísticas
    # -------------------------------------------------------------------------
    echo ""
    echo "C. Comparando con script Python (estadísticas.py):"
    echo "  ------------------------------------------------"
    python3 estadisticas.py "$archivo_original"
    
    # -------------------------------------------------------------------------
    # TAREA D: Generar mapa de la ciudad con generate_maps.py
    # -------------------------------------------------------------------------
    echo ""
    echo "D. Generando mapa HTML de la ciudad..."
    echo "  ------------------------------------"
    
    # Nombre del archivo HTML de salida
    html_salida="${HTML_DIR}/${ciudad}GowallaMap.html"
    
    # Verificar que generate_maps.py existe
    if [ -f "generate_maps.py" ]; then
        python3 generate_maps.py \
            --input_file "$archivo_filtrado" \
            --city_name "$ciudad" \
            --output_html "$html_salida"
        
        if [ -f "$html_salida" ]; then
            echo "  Mapa generado: $html_salida"
            echo "  Tamaño: $(du -h "$html_salida" | cut -f1)"
        else
            echo "  ERROR: No se generó el archivo HTML"
        fi
    else
        echo "  ERROR: No se encuentra generate_maps.py"
    fi
    
    # -------------------------------------------------------------------------
    # TAREA E: Generar mapa individual para un usuario con al menos 2 visitas
    # -------------------------------------------------------------------------
    echo ""
    echo "E. Buscando usuario con al menos 2 visitas..."
    echo "  -------------------------------------------"
    
    # Encontrar un usuario con al menos 2 visitas
    # Usamos awk para contar y filtrar
    usuario_con_visitas=$(cut -f1 "$archivo_filtrado" | sort | uniq -c | awk '$1 >= 2 {print $2; exit}')
    
    if [ -n "$usuario_con_visitas" ]; then
        echo "  Usuario encontrado: $usuario_con_visitas (con al menos 2 visitas)"
        
        # Generar mapa individual
        html_individual="${HTML_DIR}/user_${usuario_con_visitas}_${ciudad}.html"
        
        if [ -f "generate_individual_maps.py" ]; then
            python3 generate_individual_maps.py \
                --user_id "$usuario_con_visitas" \
                --city_name "$ciudad" \
                --input_file "$archivo_original" \
                --output_html "$html_individual"
            
            if [ -f "$html_individual" ]; then
                echo "  Mapa individual generado: $html_individual"
            else
                echo "  ERROR: No se generó el mapa individual"
            fi
        else
            echo "  ERROR: No se encuentra generate_individual_maps.py"
        fi
    else
        echo "  No se encontró ningún usuario con al menos 2 visitas en $ciudad"
    fi
    
    # -------------------------------------------------------------------------
    # TAREA F: Generar top 5 usuarios con topn_selection_Claudia_Gonzalo.py
    # -------------------------------------------------------------------------
    echo ""
    echo "F. Generando top 5 usuarios..."
    echo "  -----------------------------"
    
    archivo_top5="top_5_${ciudad}.txt"
    
    if [ -f "topn_selection_Claudia_Gonzalo.py" ]; then
        # Renombrar el script según enunciado (pero usamos el existente)
        python3 topn_selection_Claudia_Gonzalo.py "$archivo_filtrado" 5 "$archivo_top5"
        
        if [ -f "$archivo_top5" ]; then
            echo "  Top 5 generado: $archivo_top5"
            echo "  Contenido:"
            cat "$archivo_top5"
            
            # -----------------------------------------------------------------
            # TAREA G: Generar mapas individuales para los top 5 usuarios
            # -----------------------------------------------------------------
            echo ""
            echo "  G. Generando mapas para los top 5 usuarios..."
            echo "    -------------------------------------------"
            
            contador=0
            while read -r linea; do
                if [ -n "$linea" ]; then
                    usuario_top=$(echo "$linea" | awk '{print $1}')
                    contador=$((contador + 1))
                    
                    echo "    $contador. Procesando usuario: $usuario_top"
                    
                    html_top="${HTML_DIR}/top_user_${usuario_top}_${ciudad}.html"
                    
                    python3 generate_individual_maps.py \
                        --user_id "$usuario_top" \
                        --city_name "$ciudad" \
                        --input_file "$archivo_original" \
                        --output_html "$html_top"
                    
                    if [ -f "$html_top" ]; then
                        echo "      Mapa generado: $html_top"
                    else
                        echo "      Error generando mapa"
                    fi
                fi
            done < "$archivo_top5"
        else
            echo "  ERROR: No se generó el archivo top 5"
        fi
    else
        echo "  ERROR: No se encuentra topn_selection_Claudia_Gonzalo.py"
    fi
    
    echo ""
    echo "Procesamiento de $ciudad completado"
    echo "========================================"
done

# =============================================================================
# PASO 6: RESUMEN FINAL
# =============================================================================
echo ""
echo "Paso 6: Resumen final..."
echo "-----------------------"

echo "ARCHIVOS GENERADOS:"
echo "==================="

echo "1. Archivos de datos:"
echo "   - ALL_LOCATIONS.txt (todas las ubicaciones)"
for ciudad in "${ciudades[@]}"; do
    if [ -f "${ciudad}filtered.txt" ]; then
        echo "   - ${ciudad}filtered.txt"
    fi
done

echo ""
echo "2. Archivos HTML de mapas:"
echo "   (En directorio: $HTML_DIR)"
if [ -d "$HTML_DIR" ]; then
    html_count=$(ls -1 "$HTML_DIR"/*.html 2>/dev/null | wc -l)
    echo "   Total de mapas HTML generados: $html_count"
    echo "   Lista:"
    ls -1 "$HTML_DIR"/*.html 2>/dev/null | head -10
    if [ "$html_count" -gt 10 ]; then
        echo "   ... y $(($html_count - 10)) más"
    fi
fi

echo ""
echo "3. Archivos top 5:"
for ciudad in "${ciudades[@]}"; do
    if [ -f "top_5_${ciudad}.txt" ]; then
        echo "   - top_5_${ciudad}.txt"
    fi
done

# =============================================================================
# PASO 7: INICIAR APLICACIÓN FLASK (PARA VER MAPAS)
# =============================================================================
echo ""
echo "Paso 7: Iniciando aplicación Flask para visualizar mapas..."
echo "----------------------------------------------------------"

# Verificar si Flask ya está corriendo
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null ; then
    echo "Flask ya está corriendo en el puerto 5000"
    echo "Puedes acceder a los mapas en: http://localhost:5000/show_html_files"
else
    echo "Iniciando Flask en segundo plano..."
    
    # Navegar al directorio del proyecto
    cd "$PROJECT_DIR"
    
    # Verificar que main.py existe
    if [ -f "main.py" ]; then
        # Iniciar Flask en segundo plano
        python3 main.py &
        FLASK_PID=$!
        
        echo "Flask iniciado con PID: $FLASK_PID"
        echo "Esperando 5 segundos para que Flask se inicie completamente..."
        sleep 5
        
        echo ""
        echo "APLICACIÓN FLASK INICIADA CORRECTAMENTE"
        echo "=========================================="
        echo ""
        echo "ACCESO A LOS MAPAS:"
        echo "==================="
        echo "1. Abre tu navegador web"
        echo "2. Ve a la dirección: http://localhost:5000"
        echo "3. Haz clic en 'Show HTML Files'"
        echo "4. Selecciona cualquier mapa HTML para visualizarlo"
        echo ""
        echo "O accede directamente: http://localhost:5000/show_html_files"
        echo ""
        echo "Para detener Flask, ejecuta: kill $FLASK_PID"
        echo ""
        echo "RECOMENDACIÓN: Ejecuta en otra terminal:"
        echo "  htop"
        echo "Para monitorear el uso de recursos mientras pruebas los mapas"
    else
        echo "ERROR: No se encuentra main.py en $PROJECT_DIR"
        echo "  Verifica que el proyecto Flask esté correctamente clonado"
    fi
fi

# echo ""
# echo "=========================================="
# echo "SCRIPT COMPLETADO EXITOSAMENTE"
# echo "=========================================="
# echo ""
# echo "NEXT STEPS:"
# echo "1. Abre http://localhost:5000/show_html_files en tu navegador"
# echo "2. Prueba al menos 2 mapas de diferentes ciudades"
# echo "3. Toma capturas de pantalla para la memoria"
# echo "4. En otra terminal, ejecuta 'htop' para monitorear recursos"
# echo ""
# echo "¡Los mapas están listos para visualizar!"