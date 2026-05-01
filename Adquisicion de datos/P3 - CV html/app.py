from flask import Flask, render_template, request

# Crear la aplicación Flask
app = Flask(__name__)

# Ruta para la página principal
@app.route('/')
def index():
    # Renderiza la plantilla index.html
    return render_template('index.html')

# Ruta para la página del CV
@app.route('/cv')
def cv():
    # Renderiza la plantilla cv.html
    return render_template('cv.html')

# Ruta para la página de contacto
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    # Si el método es POST (se envió el formulario)
    if request.method == 'POST':
        # Mostrar página de confirmación
        return render_template('contact.html', form_submitted=True)
    
    # Si el método es GET (acceso normal a la página)
    return render_template('contact.html', form_submitted=False)

# Ejecutar la aplicación en modo debug
if __name__ == '__main__':
    app.run(debug=True)
