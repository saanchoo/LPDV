from app import app

if __name__ == '__main__':
    # 127.0.0.1 en vez de localhost — necesario para que las cookies de sesión
    # sean coherentes con el redirect URI registrado en Spotify Developer
    app.run(debug=True, host='127.0.0.1', port=5000)
