from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite que React se conecte sin bloqueos de origen (CORS)

@app.route('/api/test', methods=['GET'])
def test_api():
    return jsonify({"mensaje": "¡Conexión exitosa entre Flask y React!"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)