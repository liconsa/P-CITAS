from flask import Flask, jsonify
from flask_cors import CORS

# Importamos ambos blueprints
from auth_routes import auth_bp
from security_routes import security_bp  # <--- Registrado correctamente

app = Flask(__name__)
CORS(app)

# Registramos ambos blueprints para que Flask reconozca todas las rutas
app.register_blueprint(auth_bp)
app.register_blueprint(security_bp)  # <--- Registrado correctamente

@app.route('/api/test', methods=['GET'])
def test_api():
    return jsonify({"mensaje": "¡Conexión exitosa entre Flask y Angular modular!"})

if __name__ == '__main__':
    app.run(debug=True, port=8000)