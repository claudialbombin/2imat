#!/bin/bash
# Limpiar todos los datos existentes
echo "=== LIMPIANDO DATOS EXISTENTES ==="
rm -rf quotes
mkdir -p quotes
echo "Datos anteriores eliminados"
echo ""

# Variables iniciales
web_page="http://www.quotationspage.com/quotes/"

# Función para mostrar ayuda
function show_help {
    echo "Uso: $0 [AUTORES]"
    echo ""
    echo "Ejemplos:"
    echo "  $0 Edgar_Allan_Poe"
    echo "  $0 Agatha_Christie William_Shakespeare"
    echo "  $0 \"Albert Einstein\" \"Mahatma Gandhi\""
    echo ""
    echo "Si no se especifican autores, se usarán los predeterminados."
    echo "Los nombres con espacios deben ir entre comillas."
}

# Procesar argumentos de la línea de comandos
if [ $# -eq 0 ]; then
    # Si no hay argumentos, usar autores predeterminados
    authors="Edgar_Allan_Poe Agatha_Christie William_Shakespeare"
    echo "No se especificaron autores. Usando autores predeterminados:"
    echo "$authors"
else
    # Convertir argumentos a formato adecuado (reemplazar espacios por _)
    authors=""
    for arg in "$@"; do
        if [ "$arg" = "-h" ] || [ "$arg" = "--help" ]; then
            show_help
            exit 0
        fi
        
        # Convertir espacios por _ y añadir a la lista
        author_formatted=$(echo "$arg" | sed 's/ /_/g')
        authors="$authors $author_formatted"
    done
    authors=$(echo $authors)  # Limpiar espacios extra
    echo "Autores especificados: $authors"
fi

echo ""

# Crear directorio quotes si no existe
mkdir -p quotes 2>/dev/null

# Función para convertir nombre con _ a espacios
function format_author_name {
    echo "$1" | tr '_' ' '
}

# Función para verificar si ya existe el archivo procesado
function is_already_processed {
    local author=$1
    if [ -f "quotes/${author}_processed_quotes.txt" ] && [ -s "quotes/${author}_processed_quotes.txt" ]; then
        return 0  # Ya existe y tiene contenido
    else
        return 1  # No existe o está vacío
    fi
}

# Función para descargar página web con mejor manejo de errores
function download_page {
    local url=$1
    local output_file=$2
    local author_name=$3
    
    echo "Descargando los datos de $author_name"
    echo "URL: $url"
    
    # Usar curl con opciones mejoradas
    if command -v curl &> /dev/null; then
        curl -L -s --retry 3 --connect-timeout 10 "$url" -o "$output_file"
    elif command -v wget &> /dev/null; then
        wget -q --timeout=10 --tries=3 "$url" -O "$output_file"
    else
        echo "Error: No se encontró curl ni wget para descargar los datos"
        return 1
    fi
    
    # Verificar que la descarga fue exitosa
    if [ $? -eq 0 ] && [ -f "$output_file" ]; then
        file_size=$(wc -c < "$output_file")
        line_count=$(wc -l < "$output_file" 2>/dev/null || echo "0")
        echo "✓ Descarga completada: $file_size bytes, $line_count líneas"
        
        # Mostrar primeras líneas para debugging
        if [ $line_count -gt 0 ]; then
            echo "Primeras 3 líneas del archivo:"
            head -3 "$output_file"
        else
            echo "El archivo está vacío"
        fi
        echo ""
        
        return 0
    else
        echo "✗ Error en la descarga de $author_name"
        return 1
    fi
}

# Apartado 1: Descarga de datos
echo "=== APARTADO 1: DESCARGANDO DATOS ==="
for author in $authors; do
    author_spaces=$(format_author_name "$author")
    
    # Verificar si ya existe el archivo procesado con contenido
    if is_already_processed "$author"; then
        echo "Ya existen datos procesados para $author_spaces. No se procede a la descarga"
        continue
    fi
    
    # Verificar si ya existe el archivo sin procesar con contenido
    if [ -f "quotes/${author}_unprocessed.txt" ] && [ -s "quotes/${author}_unprocessed.txt" ]; then
        echo "Los datos sin procesar de $author_spaces ya existen. Saltando descarga."
        continue
    fi
    
    # Si el archivo existe pero está vacío, eliminarlo
    if [ -f "quotes/${author}_unprocessed.txt" ] && [ ! -s "quotes/${author}_unprocessed.txt" ]; then
        rm "quotes/${author}_unprocessed.txt"
    fi
    
    # Probar diferentes formatos de URL
    url1="${web_page}${author}"
    url2="${web_page}${author}/"
    url3="http://www.quotationspage.com/search.php?Search=${author}&startsearch=Search"
    
    echo "Probando diferentes URLs para $author_spaces..."
    
    # Probar primera URL
    download_page "$url1" "quotes/${author}_unprocessed.txt" "$author_spaces"
    
    # Verificar si la descarga fue exitosa y tiene contenido
    if [ -f "quotes/${author}_unprocessed.txt" ] && [ -s "quotes/${author}_unprocessed.txt" ]; then
        echo "✓ URL exitosa: $url1"
    else
        echo "✗ Primera URL falló, probando segunda..."
        download_page "$url2" "quotes/${author}_unprocessed.txt" "$author_spaces"
        
        if [ -f "quotes/${author}_unprocessed.txt" ] && [ -s "quotes/${author}_unprocessed.txt" ]; then
            echo "✓ URL exitosa: $url2"
        else
            echo "✗ Segunda URL falló, probando tercera..."
            download_page "$url3" "quotes/${author}_unprocessed.txt" "$author_spaces"
            
            if [ -f "quotes/${author}_unprocessed.txt" ] && [ -s "quotes/${author}_unprocessed.txt" ]; then
                echo "✓ URL exitosa: $url3"
            else
                echo "✗ Todas las URLs fallaron para $author_spaces"
                # Crear archivo vacío para continuar
                touch "quotes/${author}_unprocessed.txt"
            fi
        fi
    fi
    echo ""
done

# Apartado 2: Filtrado de citas HTML
echo "=== APARTADO 2: FILTRANDO CITAS HTML ==="
for author in $authors; do
    author_spaces=$(format_author_name "$author")
    
    # Verificar si ya existe el archivo procesado final con contenido
    if is_already_processed "$author"; then
        echo "Los datos de $author_spaces ya están procesados. Saltando filtrado HTML."
        continue
    fi
    
    # Verificar si existe el archivo sin procesar con contenido
    if [ ! -f "quotes/${author}_unprocessed.txt" ] || [ ! -s "quotes/${author}_unprocessed.txt" ]; then
        echo "No existe archivo con contenido para $author_spaces. Saltando."
        # Crear archivo HTML vacío
        touch "quotes/${author}_html_quotes.txt"
        continue
    fi
    
    # Verificar si ya existe el archivo HTML de citas con contenido
    if [ -f "quotes/${author}_html_quotes.txt" ] && [ -s "quotes/${author}_html_quotes.txt" ]; then
        echo "Las citas HTML de $author_spaces ya existen. Saltando extracción."
        continue
    fi
    
    echo "Extrayendo citas HTML de $author_spaces"
    
    # Mostrar información del archivo descargado
    file_size=$(wc -c < "quotes/${author}_unprocessed.txt")
    line_count=$(wc -l < "quotes/${author}_unprocessed.txt")
    echo "Tamaño del archivo: $file_size bytes, $line_count líneas"
    
    # Buscar contenido que contenga citas - método más amplio
    echo "Buscando contenido de citas..."
    
    # Método 1: Buscar cualquier contenido que pueda ser una cita
    grep -i "$author_spaces" "quotes/${author}_unprocessed.txt" > "quotes/${author}_html_quotes.txt"
    
    # Método 2: Si no se encuentra, buscar patrones comunes
    if [ ! -s "quotes/${author}_html_quotes.txt" ]; then
        echo "Buscando patrones HTML comunes..."
        grep -E '<div|</div>|<p|</p>|<span|</span>|<dt|</dt>|<dd|</dd>' "quotes/${author}_unprocessed.txt" | head -50 > "quotes/${author}_html_quotes.txt"
    fi
    
    # Método 3: Si aún no se encuentra, mostrar contenido completo para análisis
    if [ ! -s "quotes/${author}_html_quotes.txt" ]; then
        echo "Mostrando contenido completo para análisis:"
        cat "quotes/${author}_unprocessed.txt"
        echo "Creando archivo con primeras líneas..."
        head -20 "quotes/${author}_unprocessed.txt" > "quotes/${author}_html_quotes.txt"
    fi
    
    # Mostrar resultados
    if [ -s "quotes/${author}_html_quotes.txt" ]; then
        result_lines=$(wc -l < "quotes/${author}_html_quotes.txt")
        echo "✓ Extracción completada: $result_lines líneas encontradas"
    else
        echo "✗ No se pudo extraer contenido para $author_spaces"
    fi
    echo ""
done

# Apartado 3: Eliminación de tags HTML
echo "=== APARTADO 3: ELIMINANDO TAGS HTML ==="
for author in $authors; do
    author_spaces=$(format_author_name "$author")
    
    if is_already_processed "$author"; then
        echo "Los datos de $author_spaces ya están procesados. Saltando eliminación de tags."
        continue
    fi
    
    if [ ! -f "quotes/${author}_html_quotes.txt" ] || [ ! -s "quotes/${author}_html_quotes.txt" ]; then
        echo "No existe archivo HTML con contenido para $author_spaces. Saltando."
        touch "quotes/${author}_processed_quotes.txt"
        continue
    fi
    
    echo "Procesando citas de $author_spaces"
    
    # Limpiar HTML manteniendo el texto
    sed 's/<[^>]*>//g' "quotes/${author}_html_quotes.txt" | \
    sed 's/&nbsp;/ /g' | \
    sed 's/&amp;/\&/g' | \
    sed 's/&lt;/</g' | \
    sed 's/&gt;/>/g' | \
    sed 's/&quot;/"/g' | \
    sed '/^[[:space:]]*$/d' | \
    sed 's/^[[:space:]]*//' | \
    sed 's/[[:space:]]*$//' | \
    sed 's/[[:space:]]\+/ /g' > "quotes/${author}_processed_quotes.txt"
    
    if [ -s "quotes/${author}_processed_quotes.txt" ]; then
        line_count=$(wc -l < "quotes/${author}_processed_quotes.txt")
        echo "✓ Procesamiento completado: $line_count citas"
        echo "Muestra:"
        head -3 "quotes/${author}_processed_quotes.txt"
    else
        echo "✗ No se pudo procesar el contenido"
        echo "Contenido original:"
        head -5 "quotes/${author}_html_quotes.txt"
    fi
    echo ""
done

# Apartado 4: Mostrar las citas
echo "=== APARTADO 4: MOSTRANDO CITAS ==="
for author in $authors; do
    author_spaces=$(format_author_name "$author")
    
    if [ ! -f "quotes/${author}_processed_quotes.txt" ] || [ ! -s "quotes/${author}_processed_quotes.txt" ]; then
        echo "No hay citas disponibles para $author_spaces"
        echo ""
        continue
    fi
    
    echo "Citas de $author_spaces"
    echo "================================"
    
    counter=1
    while IFS= read -r line; do
        if [ -n "$line" ] && [ ${#line} -gt 10 ]; then
            echo "Cita $counter"
            echo "$line"
            echo ""
            ((counter++))
        fi
    done < "quotes/${author}_processed_quotes.txt"
    
    if [ $counter -eq 1 ]; then
        echo "No se encontraron citas con formato adecuado"
    fi
    echo ""
done

echo "Proceso completado!"

# Resumen final
echo "=== RESUMEN ==="
echo "Archivos creados en la carpeta 'quotes/':"
ls -la quotes/
echo ""
echo "Autores procesados:"
for author in $authors; do
    author_spaces=$(format_author_name "$author")
    if [ -f "quotes/${author}_processed_quotes.txt" ] && [ -s "quotes/${author}_processed_quotes.txt" ]; then
        count=$(wc -l < "quotes/${author}_processed_quotes.txt")
        echo "✓ $author_spaces: $count citas"
    else
        echo "✗ $author_spaces: No se encontraron citas"
    fi
done
