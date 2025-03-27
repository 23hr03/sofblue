from flask import Flask, jsonify, request, render_template, redirect, url_for, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
import re
from flask_talisman import Talisman
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
import hashlib
import random
import string
from flask_mail import Mail, Message
from flask import current_app as app
from itsdangerous import URLSafeTimedSerializer as Serializer, BadSignature
from flask_migrate import Migrate



# Crear una instancia de la clase Flask
app = Flask(__name__, static_url_path='/static', static_folder='static')


#======================================================================================================================
# ======================= Configuración de la política de seguridad de contenido (CSP) ===============================
#======================================================================================================================
csp = {
    'default-src': ["'self'"],  # Permite solo recursos del mismo dominio
    'script-src': [
        "'self'", 
        'https://unpkg.com', 
        'https://cdnjs.cloudflare.com',  # Si estás usando un CDN para scripts
        'http://localhost:5000',  # Permite scripts desde tu backend local
        "'unsafe-eval'"  # Asegura que 'eval' se permite si lo necesitas
        
        
    ],
    'style-src': [
        "'self'", 
        'https://cdnjs.cloudflare.com',  # Si estás usando un CDN para estilos
        'https://cdn.jsdelivr.net',  # Otro CDN que podrías estar usando
        "'unsafe-inline'"  # Permite estilos en línea, por si usas <style> en el HTML
    ],
    'img-src': [
        "'self'", 
        'http://localhost:5000',  # Si usas imágenes desde tu servidor
        'https://example.com',  # Si cargas imágenes de otro dominio, añádelo aquí
        'https://wallpaper.forfun.com',
        'https://definicion.com',
        'https://definicion.com '
        '*'
    ],
    'font-src': [
        "'self'", 
        'https://fonts.gstatic.com' , # Permite cargar fuentes desde Google Fonts
        'https://cdnjs.cloudflare.com',
        '*'
    ],
    'connect-src': [
        "'self'", 
        'http://localhost:5000' , # Permite conexiones a tu backend
        'https://localhost:5000',
        '*'
    ]
}
talisman = Talisman(app, content_security_policy=csp)
#======================================================================================================================
# ========================= Configuración de la base de datos ========================================================
#======================================================================================================================

CORS(app, resources={r"/*": {"origins": "http://localhost:8080"}})


app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:hector2303@localhost:3306/usuario"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
mail = Mail(app)  # Instancia de Mail
app.config['TALISMAN_CONTENT_SECURITY_POLICY'] = None
app.secret_key = "secret_key"  # Secreto para sesiones

db = SQLAlchemy(app)
migrate = Migrate(app, db)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'index'  # Redirigir a login si no está autenticadoo

# Definición del modelo
class Registro(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(100))
    email = db.Column(db.String(255))
    contraseña = db.Column(db.String(255))
    def __init__(self, usuario, email, contraseña):
        self.usuario = usuario
        self.email = email
        self.contraseña = contraseña
        

# Crear tablas en la base de datos
with app.app_context():
    db.create_all()

# Esquema de Marshmallow para el registro
class RegistroSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Registro
        fields = ("id", "usuario", "email", "contraseña")

# Inicializar esquema
registro_schema = RegistroSchema()  # Objeto para serializar/deserializar un registro
registros_schema = RegistroSchema(many=True)  # Objeto para serializar/deserializar múltiples registros

#=====================================================================================================================
# =================================== Cargar usuario por id =========================================================
#====================================================================================================================
@login_manager.user_loader
def load_user(user_id):
    return Registro.query.get(int(user_id))

def validar_email(email):
    # Expresión regular simple para validar formato de correo
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None
#======================================================================================================================
# ====================================== Endpoints de registro ========================================================
#========================================================================================================================

@app.route("/registro", methods=["GET"])
def get_registro():
    all_registro = Registro.query.all()  # Obtener todos los registros de la tabla
    result = registros_schema.dump(all_registro)  # Serializar los registros en formato JSON
    return jsonify(result)  # Retornar los registros en JSON

@app.route("/registro/<id>", methods=["GET"])
def get_registro_by_id(id):
    registro = Registro.query.get(id)  # Obtener el registro por ID
    if registro is None:
        return jsonify({"message": f"Registro con ID {id} no encontrado"}), 404
    return registro_schema.jsonify(registro)  # Retornar el registro en formato JSON

@app.route("/registro", methods=["POST"])
def create_registro():
    if not request.is_json:
        return jsonify({"message": "La solicitud debe tener formato JSON"}), 400
    
    data = request.get_json()
    usuario = data.get("usuario")
    email = data.get("email")
    contraseña = data.get("contraseña")

    if not usuario or not email or not contraseña:
        return jsonify({"message": "Todos los campos son obligatorios"}), 400

    # Validar email
    if not validar_email(email):
        return jsonify({"message": "Correo electrónico inválido"}), 400

    # Verificar si el email ya está registrado en la base de datos
    if Registro.query.filter_by(email=email).first():
        return jsonify({"message": "El correo electrónico ya está registrado"}), 400

    # Hashear la contraseña antes de almacenarla
    hashed_password = bcrypt.generate_password_hash(contraseña).decode('utf-8')

    # Crear un nuevo registro en la base de datos
    nuevo_registro = Registro(usuario=usuario, email=email, contraseña=hashed_password)
    
    try:
        db.session.add(nuevo_registro)
        db.session.commit()
        return jsonify({"message": "Registro exitoso"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error al guardar en la base de datos: {str(e)}"}), 500
#=======================================================================================================================
# ===================================== endpoint para iniciar session ==================================================
#=======================================================================================================================
@app.route("/ingresar", methods=["POST"])
def iniciar_Session():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    print(f"Recibido: Email: {email}, Contraseña: {password}") 
    
    if len(password) < 6:
        return jsonify({"message": "La contraseña debe contener 6 o más caracteres"}), 400


    if not email or not password:
        return jsonify({"message": "Correo o contraseña faltante"}), 400
    
     # Buscar el usuario en la base de datos por el correo electrónico
    usuario = Registro.query.filter_by(email=email).first()
    if usuario and bcrypt.check_password_hash(usuario.contraseña, password):
        login_user(usuario)  # Autentica al usuario con Flask-Login
        session['nombre'] = usuario.usuario  # Guardar el nombre en la sesión
        print("usuario encontrado:",session)
        return jsonify({
            "message": "Login exitoso",
            "redirect": url_for('Home', _external=True)  # URL completa para /Home
        }), 200
    else:
        return jsonify({"message": "Credenciales inválidas"}), 401
    


#==================================================================================================================
#=============================================== Ruta para cerrar sesión ===========================================
#===================================================================================================================
@app.route("/logout")
@login_required
def logout():
    logout_user()  # Finalizar sesión del usuario
    return redirect(url_for('index'))  # Redirigir al login

#======================================================================================================================
#================================ Cambiar de contraseña de forma basica ==============================================
#=====================================================================================================================

# @app.route("/usuario/<usuario>/<email>", methods=["PUT"])
# def actualizar_usuario(usuario, email):
#     # Buscar el usuario por su nombre de usuario y correo electrónico
#     usuario_encontrado = Registro.query.filter_by(usuario=usuario, email=email).first()

#     if not usuario_encontrado:
#         return jsonify({"message": "Usuario no encontrado"}), 404

#     # Actualizar la contraseña si se proporciona
#     nueva_contraseña = request.json.get("password")

#     if nueva_contraseña:
#         usuario_encontrado.contraseña = bcrypt.generate_password_hash(nueva_contraseña).decode('utf-8')
#         db.session.commit()
#         print(nueva_contraseña)
#         return jsonify({"message": "Contraseña actualizada exitosamente"}), 200
    
    
    

#     return jsonify({"message": "No se proporcionó una nueva contraseña"}), 400
#=============================================================================================================
# ============================nuevo forma de hacer el cambio de contraseña====================================
#===============================================================================================================
# Ruta para buscar usuario
@app.route("/buscar_usuario/<usuario>/<email>", methods=["GET"])  
def buscar_usuario(usuario, email):
    encontrado = Registro.query.filter_by(usuario=usuario, email=email).first()
    
    if not encontrado:
        return jsonify({"message": "Usuario no encontrado"}), 404
    
    # Redirigir a la página de cambio de contraseña pasando el ID del usuario
    return redirect(url_for('cambiar_contraseña', usuario_id=encontrado.id))

#Ruta para cambiar contraseña
@app.route("/cambiar_contraseña/<int:usuario_id>", methods=["GET", "POST"])
def cambiar_contraseña(usuario_id):
    usuario = Registro.query.get_or_404(usuario_id)
    
    if request.method == "POST":
        data = request.get_json()
        nueva_contraseña = data.get("nueva_contraseña")
        if not nueva_contraseña:
            return jsonify({"message": "La nueva contraseña es requerida"}), 400
        
        usuario.contraseña = bcrypt.generate_password_hash(nueva_contraseña).decode('utf-8')
        db.session.commit()
        return jsonify({"message": "Contraseña actualizada exitosamente"}), 200
    
    return jsonify({"message": "Usuario encontrado", "usuario": usuario.usuario}), 200
#====================================================================================================================
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'OPTIONS, POST, GET, PUT, DELETE')
    return response
#=============================================================================================================
#================================= Endpoint para renderizar el HTML ==========================================
#==============================================================================================================
@app.route("/actualizar")
def actualizar():
    return render_template("cambiar_contraseña.html")
#=============================================================
@app.route("/index")
def index():
    return render_template("index.html")
#=============================================
@app.route("/Home")
@login_required  # Requiere que el usuario esté autenticado
def Home():
    return render_template("Home.html", usuario=current_user.usuario)
#============================================

@app.route("/blog")
def blog():
    return render_template("blog.html")
#===============================================
@app.route("/curso")
def cursos():
    return render_template("cursos.html")

#============================================================================================================
# =================== Ejecutar la aplicación ===============================================================
#=============================================================================================================
if __name__ == "__main__":
    app.run(debug=True, port=5000)





