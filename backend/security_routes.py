from flask import Blueprint, request, jsonify
import random
import json
from auth_routes import obtener_conexion

security_bp = Blueprint('security_bp', __name__)

tokens_temporales_db = {}
tokens_recuperacion_db = {}

# --- RUTAS DE RECUPERACIÓN DE CONTRASEÑA (SEPARADAS) ---

@security_bp.route("/api/auth/solicitar-recuperacion", methods=["POST"])
def solicitar_recuperacion():
    datos = request.get_json()
    correo = datos.get("correo")

    if not correo:
        return jsonify({"error": "El correo es obligatorio"}), 400

    codigo_recuperacion = str(random.randint(1000, 9999))
    tokens_recuperacion_db[correo] = codigo_recuperacion

    print("\n" + "=" * 40)
    print(f"🔑 RECUPERACIÓN DE CONTRASEÑA")
    print(f"👉 Correo: {correo}")
    print(f"👉 Código: {codigo_recuperacion}")
    print("=" * 40 + "\n")

    return jsonify({"status": "success", "message": "Código de recuperación enviado."}), 200


# Paso 1: Solo verifica si el código coincide con el del correo
@security_bp.route("/api/auth/verificar-codigo", methods=["POST"])
def verificar_codigo():
    datos = request.get_json()
    correo = datos.get("correo")
    codigo_ingresado = datos.get("codigo")

    codigo_guardado = tokens_recuperacion_db.get(correo)

    if not codigo_guardado or str(codigo_guardado) != str(codigo_ingresado):
        return jsonify({"error": "Código incorrecto o expirado."}), 400

    return jsonify({"status": "success", "message": "Código válido."}), 200


# Paso 2: Cambia la contraseña en la base de datos
@security_bp.route("/api/auth/cambiar-password", methods=["POST"])
def cambiar_password():
    datos = request.get_json()
    correo = datos.get("correo")
    codigo_ingresado = datos.get("codigo")
    nueva_contrasena = datos.get("nueva_contrasena")

    codigo_guardado = tokens_recuperacion_db.get(correo)

    if not codigo_guardado or str(codigo_guardado) != str(codigo_ingresado):
        return jsonify({"error": "Código incorrecto o expirado."}), 400

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("UPDATE usuarios SET contrasena = %s WHERE correo = %s", (nueva_contrasena, correo))
        conexion.commit()

        cursor.close()
        conexion.close()

        # Limpiamos el token usado
        if correo in tokens_recuperacion_db:
            del tokens_recuperacion_db[correo]

        return jsonify({"status": "success", "message": "Contraseña actualizada con éxito en la BD."}), 200
    except Exception as e:
        return jsonify({"error": f"Error al actualizar contraseña: {str(e)}"}), 500