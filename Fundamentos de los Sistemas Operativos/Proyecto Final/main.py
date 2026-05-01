# main.py - Debería ejecutar la aplicación Flask
from flask import Flask
from app import app

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)