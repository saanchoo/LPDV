import os
from flask import Flask
from dotenv import load_dotenv

# Cargamos las variables del archivo .env
load_dotenv()

app = Flask(__name__)

# Necesario para gestionar sesiones de usuario (cookies)
app.secret_key = os.getenv('SECRET_KEY', 'una_clave_super_secreta_por_defecto')

from app import routes