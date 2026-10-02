from flask import Blueprint, request, jsonify
import psycopg2
import random
import json

auth_bp = Blueprint('auth_bp', __name__)

# Diccionario temporal en memoria para guardar los códigos { "correo@dominio.com": "1234" }
codigos_recuperacion = {}


def obtener_conexion():
    return psycopg2.connect(
        host="localhost",
        database="hospital_db",
        user="postgres",
        password="tu_password",  # Asegúrate de poner tu contraseña real aquí
        port="5432"
    )


@auth_bp.route('/api/login', methods=['POST'])
def iniciar_sesion():
    datos = request.get_json()
    if not datos:
        return jsonify({"detail": "No se recibieron datos JSON"}), 400

    correo = datos.get('correo')
    contrasena = datos.get('contrasena')

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        query = "SELECT nombre, rol FROM usuarios WHERE correo = %s AND contrasena = %s"
        cursor.execute(query, (correo, contrasena))
        usuario = cursor.fetchone()
        cursor.close()
        conexion.close()

        if usuario:
            return jsonify({"mensaje": "Login exitoso", "rol": usuario[1], "usuario": usuario[0]}), 200
        else:
            return jsonify({"detail": "Credenciales incorrectas"}), 401
    except Exception as e:
        return jsonify({"detail": f"Error en el servidor: {str(e)}"}), 500


@auth_bp.route('/api/registro', methods=['POST'])
def registrar_usuario():
    datos = request.get_json()
    if not datos:
        return jsonify({"detail": "No se recibieron datos JSON"}), 400

    nombre = datos.get('nombre')
    correo = datos.get('correo')
    contrasena = datos.get('contrasena')
    rol = datos.get('rol', 'Paciente')  # Toma el rol enviado o 'Paciente' por defecto
    area = datos.get('area', 'Citas')  # Área por defecto para recepcionistas

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        query = "INSERT INTO usuarios (nombre, correo, contrasena, rol, area) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (nombre, correo, contrasena, rol, area))
        conexion.commit()
        cursor.close()
        conexion.close()
        return jsonify({"mensaje": "Registro exitoso"}), 201
    except Exception as e:
        return jsonify({"detail": f"El correo ya está registrado o hubo un error: {str(e)}"}), 400


# --- RUTAS DE RECUPERACIÓN AUTOMÁTICA ---

@auth_bp.route('/api/solicitar-recuperacion', methods=['POST'])
def solicitar_recuperacion():
    datos = request.get_json()
    if not datos:
        return jsonify({"detail": "No se recibieron datos JSON"}), 400

    correo = datos.get('correo')

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT id_usuario FROM usuarios WHERE correo = %s", (correo,))
        usuario = cursor.fetchone()
        cursor.close()
        conexion.close()

        if not usuario:
            return jsonify({"detail": "El correo no está registrado en el sistema."}), 404

        codigo = str(random.randint(1000, 9999))
        codigos_recuperacion[correo] = codigo

        print("\n" + "=" * 40)
        print(f"🔑 CÓDIGO DE RECUPERACIÓN PARA: {correo}")
        print(f"👉 CÓDIGO: {codigo}")
        print("=" * 40 + "\n")

        return jsonify({"mensaje": "Código generado con éxito"}), 200

    except Exception as e:
        return jsonify({"detail": f"Error en el servidor: {str(e)}"}), 500


@auth_bp.route('/api/verificar-codigo', methods=['POST'])
def verificar_codigo():
    datos = request.get_json()
    if not datos:
        return jsonify({"detail": "No se recibieron datos JSON"}), 400

    correo = datos.get('correo')
    codigo_ingresado = datos.get('codigo')

    if codigos_recuperacion.get(correo) == codigo_ingresado:
        return jsonify({"mensaje": "Código verificado correctamente"}), 200
    else:
        return jsonify({"detail": "Código incorrecto o expirado"}), 400


@auth_bp.route('/api/actualizar-contrasena', methods=['POST'])
def actualizar_contrasena():
    datos = request.get_json()
    if not datos:
        return jsonify({"detail": "No se recibieron datos JSON"}), 400

    correo = datos.get('correo')
    nueva_contrasena = datos.get('nueva_contrasena')

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        query = "UPDATE usuarios SET contrasena = %s WHERE correo = %s"
        cursor.execute(query, (nueva_contrasena, correo))
        conexion.commit()
        filas_afectadas = cursor.rowcount
        cursor.close()
        conexion.close()

        if filas_afectadas > 0:
            codigos_recuperacion.pop(correo, None)
            return jsonify({"mensaje": "Contraseña actualizada exitosamente"}), 200
        else:
            return jsonify({"detail": "El correo no está registrado"}), 404
    except Exception as e:
        return jsonify({"detail": f"Error en el servidor: {str(e)}"}), 500


# --- RUTA PARA CARGAR LOS USUARIOS Y SUS PERMISOS REALES DESDE LA BD ---

@auth_bp.route('/api/usuarios', methods=['GET'])
def obtener_usuarios():
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        query = "SELECT id_usuario, nombre, rol, permisos, area FROM usuarios"
        cursor.execute(query)
        usuarios_db = cursor.fetchall()

        cursor.close()
        conexion.close()

        lista_usuarios = []
        for u in usuarios_db:
            id_usuario = u[0]
            nombre = u[1]
            rol_actual = u[2]
            permisos_db = u[3]
            area_actual = u[4] if len(u) > 4 and u[4] else 'Citas'

            if isinstance(permisos_db, str):
                try:
                    permisos_db = json.loads(permisos_db)
                except:
                    permisos_db = None

            if not permisos_db:
                permisos_db = [
                    {"nombre": "Crear citas médicas", "activo": rol_actual in ['Recepcionista', 'Administrador']},
                    {"nombre": "Ver expedientes clínicos", "activo": rol_actual in ['Médico', 'Administrador']},
                    {"nombre": "Gestión de farmacia", "activo": rol_actual in ['Farmacia', 'Administrador']},
                    {"nombre": "Acceso total al sistema", "activo": rol_actual == 'Administrador'}
                ]

            lista_usuarios.append({
                "id": id_usuario,
                "nombre": nombre,
                "rol": rol_actual,
                "permisos": permisos_db,
                "area": area_actual
            })

        return jsonify(lista_usuarios), 200

    except Exception as e:
        print(f"Error en BD al obtener usuarios: {e}")
        return jsonify({"detail": f"Error al cargar usuarios: {str(e)}"}), 500


# --- RUTA PARA ELIMINAR UN USUARIO ---

@auth_bp.route('/api/usuarios/<int:usuario_id>', methods=['DELETE'])
def eliminar_usuario(usuario_id):
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        query = "DELETE FROM usuarios WHERE id_usuario = %s"
        cursor.execute(query, (usuario_id,))
        conexion.commit()
        cursor.close()
        conexion.close()
        return jsonify({"mensaje": "Usuario eliminado exitosamente"}), 200
    except Exception as e:
        return jsonify({"detail": f"Error al eliminar: {str(e)}"}), 500


# --- RUTA PARA GUARDAR PERMISOS Y ÁREA ---

@auth_bp.route('/api/seguridad/verificar-y-guardar', methods=['POST'])
def verificar_y_guardar_permisos():
    datos = request.get_json()
    if not datos:
        return jsonify({"detail": "No se recibieron datos JSON"}), 400

    usuario_id = datos.get("usuario_id")
    permisos = datos.get("permisos")
    area = datos.get("area")

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        permisos_json = json.dumps(permisos)

        query = "UPDATE usuarios SET permisos = %s, area = %s WHERE id_usuario = %s"
        cursor.execute(query, (permisos_json, area, usuario_id))
        conexion.commit()

        cursor.close()
        conexion.close()

        return jsonify({"mensaje": "Permisos y área actualizados correctamente"}), 200
    except Exception as e:
        return jsonify({"detail": f"Error al actualizar en la base de datos: {str(e)}"}), 500