# =========================
#  SISTEMA BIOMÉDICO - FLASK
#  Autor: PINTO PEÑA ,Valery Georgina,ROMERO RIVAS, Romina Ariadna ,QUISPE INOÑAN, Roy Salvador,GONZALES POCCO, Jesus Martin
#  Descripción: App principal para gestión de usuarios y OTMs
# =========================

# ---- IMPORTACIONES ----
from usuariosdelsistema import licenciadas, tecnicosingenieros, secretarias
from datos_otm_detalle import otm_detalle_data
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime
from DownloadPDFformat import generar_pdf_otm_completo_formato
import json
import os
import pandas as pd
from Download import generar_excel_otm

# ---- CONFIGURACIÓN FLASK ----
app = Flask(__name__)
app.secret_key = 'supersecreto'  # Clave para sesiones

# ---- VARIABLES GLOBALES ----
otm_parcial = {}   # Guarda temporalmente los datos del Formulario 1
otm_data = [
    # Lista de OTMs de ejemplo (puedes cargar desde archivo o base de datos)
    {"numero": "OTM001", "fecha": "2024-06-01", "estado": "Por Archivar"},
    # ... (más OTMs)
]
otm_data_completo = []   # Lista de OTMs completas

# ---- FUNCIONES PARA USUARIOS REGISTRADOS (JSON) ----
USUARIOS_FILE = 'usuarios_registrados.json'

def cargar_usuarios():
    """Carga usuarios registrados desde el archivo JSON."""
    if os.path.exists(USUARIOS_FILE):
        with open(USUARIOS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def guardar_usuarios(usuarios):
    """Guarda la lista de usuarios registrados en el archivo JSON."""
    with open(USUARIOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(usuarios, f, ensure_ascii=False, indent=2)

usuarios_registrados = cargar_usuarios()

# ---- RUTAS PRINCIPALES ----

@app.route('/')
def inicio():
    """Redirige a la página de login."""
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login de usuarios.
    Busca en técnicos, licenciadas, secretarias y usuarios registrados (JSON).
    Redirige al panel correspondiente según el rol.
    """
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Buscar en técnicos
        for user in tecnicosingenieros:
            if user['username'] == username and user['password'] == password:
                session['usuario'] = user
                return redirect(url_for('formulario'))

        # Buscar en licenciadas
        for user in licenciadas:
            if user['username'] == username and user['password'] == password:
                session['usuario'] = user
                return redirect(url_for('dashboardLicenciada'))

        # Buscar en secretarias
        for user in secretarias:
            if user['username'] == username and user['password'] == password:
                session['usuario'] = user
                return redirect(url_for('dashboardSecretaria'))

        # Buscar en usuarios registrados (JSON)
        for user in usuarios_registrados:
            if user['username'] == username and user['password'] == password:
                session['usuario'] = user
                if user['rol'] == 'SEC':
                    return redirect(url_for('dashboardSecretaria'))
                elif user['rol'] == 'ING':
                    return redirect(url_for('formulario'))
                elif user['rol'] == 'LIC':
                    return redirect(url_for('dashboardLicenciada'))

        error = 'Usuario o contraseña incorrectos'

    return render_template('login.html', error=error)

# ---- FORMULARIOS DE OTM (TÉCNICO/INGENIERO) ----

@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    """
    Primer formulario para crear OTM (Técnico/Ingeniero).
    Guarda datos parciales y redirige al segundo formulario.
    """
    global otm_parcial
    if request.method == 'POST':
        datos = {}
        campos = [
            'dependencia', 'numero', 'fecha', 'area', 'ubicacion',
            'denominacion', 'marca', 'modelo', 'serie', 'codigo_patrimonial',
            'problema', 'fecha_solicitud', 'fecha_recepcion', 'diagnostico',
            'encargado', 'fecha_mantenimiento', 'trabajo', 'fecha_inicio',
            'fecha_termino', 'garantia', 'costo', 'recomendaciones'
        ]
        for campo in campos:
            datos[campo] = request.form.get(campo, '').strip()
        datos['prioridad'] = request.form.get('prioridad', '')
        datos['modalidad'] = request.form.getlist('modalidad[]')
        otm_parcial = datos
        return redirect(url_for('formulario2'))
    return render_template('formulario.html')

@app.route('/formulario2', methods=['GET', 'POST'])
def formulario2():
    """
    Segundo formulario para crear OTM (Técnico/Ingeniero).
    Fusiona datos y guarda la OTM completa.
    """
    global otm_parcial, otm_data_completo
    if request.method == 'POST':
        datos_form2 = {}
        campos_form2 = [
            'nombre_tecnico', 'especialidad', 'horas', 'valor_hora', 'costo_mo',
            'origen', 'descripcion_material', 'um', 'cantidad', 'costo_unitario',
            'costo_parcial', 'total_mo', 'total_materiales', 'otros_gastos',
            'impuestos', 'total_general'
        ]
        for campo in campos_form2:
            datos_form2[campo] = request.form.get(campo, '').strip()
        # Fusionar los datos del formulario 1 y 2
        otm_completa = {**otm_parcial, **datos_form2}
        otm_data_completo.append(otm_completa)
        otm_parcial = {}  # Limpiar datos parciales
        return redirect(url_for('resumen'))
    return render_template('formulario2.html')

@app.route('/resumen')
def resumen():
    """
    Muestra el resumen de OTMs completas para el usuario.
    """
    if 'usuario' not in session:
        return redirect(url_for('login'))
    usuario = session['usuario']
    return render_template('resumen.html', otms=otm_data_completo, usuario=usuario)

# ---- LOGOUT ----

@app.route('/logout')
def logout():
    """Cierra la sesión del usuario."""
    session.pop('usuario', None)
    return redirect(url_for('login'))

# ---- DESCARGA DE EXCEL Y PDF ----

@app.route('/descargar_excel')
def descargar_excel():
    """
    Descarga todas las OTMs completas en formato Excel.
    Requiere pandas y openpyxl instalados.
    """
    output, error, status = generar_excel_otm(otm_data_completo)
    if status != 200:
        return error, status
    return send_file(
        output,
        download_name=f'OTM-{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.route('/descargar_pdf/<int:index>')
def descargar_pdf(index):
    """
    Descarga una OTM específica en formato PDF.
    Requiere reportlab instalado.
    """
    if 0 <= index < len(otm_data_completo):
        otm = otm_data_completo[index]
        buffer = generar_pdf_otm_completo_formato(otm)
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'OTM-{index+1}.pdf',
            mimetype='application/pdf'
        )
    return "OTM no encontrada", 404

# ---- DASHBOARD SECRETARÍA ----

@app.route("/dashboardSecretaria", methods=["GET", "POST"])
def dashboardSecretaria():
    """
    Panel principal para Secretaría.
    Permite filtrar y ver OTMs.
    """
    if 'usuario' not in session:
        return redirect(url_for('login'))
    usuario = session['usuario']
    filtradas = otm_data  # Por defecto se muestran todas

    if request.method == "POST":
        desde = request.form.get("fecha_inicio")
        hasta = request.form.get("fecha_fin")
        estado = request.form.get("estado")
        numero = request.form.get("codigo")

        def cumple(otm):
            cumple_fecha = True
            cumple_estado = True
            cumple_numero = True
            if desde:
                cumple_fecha = datetime.strptime(otm["fecha"], "%Y-%m-%d") >= datetime.strptime(desde, "%Y-%m-%d")
            if hasta:
                cumple_fecha = cumple_fecha and datetime.strptime(otm["fecha"], "%Y-%m-%d") <= datetime.strptime(hasta, "%Y-%m-%d")
            if estado:
                cumple_estado = otm["estado"].lower() == estado.lower()
            if numero:
                cumple_numero = numero.lower() in otm["numero"].lower()
            return cumple_fecha and cumple_estado and cumple_numero

        filtradas = [otm for otm in otm_data if cumple(otm)]

    return render_template("dashboardSecretaria.html", otms=filtradas, usuario=usuario)

# ---- ACCIONES SOBRE OTM ----

@app.route('/archivar_otm/<numero>', methods=['POST'])
def archivar_otm(numero):
    """
    Cambia el estado de una OTM a 'Archivado'.
    """
    for otm in otm_data:
        if otm["numero"] == numero:
            otm["estado"] = "Archivado"
    return redirect(url_for('dashboardSecretaria'))

@app.route('/ver_detalle/<numero>')
def ver_detalle(numero):
    """
    Muestra el detalle de una OTM específica.
    """
    detalle_otm = next((otm for otm in otm_detalle_data if otm["numero"] == numero), None)
    if not detalle_otm:
        return "OTM no encontrada", 404
    return render_template('verDetalle.html', otm=detalle_otm)

# ---- CRUD DE OTMs EN RESUMEN ----

@app.route('/eliminar_otm/<int:index>', methods=['POST'])
def eliminar_otm(index):
    """Elimina una OTM del resumen."""
    if 0 <= index < len(otm_data_completo):
        otm_data_completo.pop(index)
    return redirect(url_for('resumen'))

@app.route('/editar_otm/<int:index>', methods=['GET', 'POST'])
def editar_otm(index):
    """Edita una OTM existente."""
    if 0 <= index < len(otm_data_completo):
        if request.method == 'POST':
            for key in otm_data_completo[index]:
                otm_data_completo[index][key] = request.form.get(key, otm_data_completo[index][key])
            return redirect(url_for('resumen'))
        return render_template('editar_otm.html', otm=otm_data_completo[index], index=index)
    return redirect(url_for('resumen'))

# ---- PERFIL DE USUARIO ----

@app.route('/perfil')
def perfil():
    """Muestra el perfil del usuario en sesión."""
    if 'usuario' not in session:
        return redirect(url_for('login'))
    usuario = session['usuario']
    return render_template('perfil.html', usuario=usuario)

# ---- DASHBOARD LICENCIADA ----

@app.route('/dashboardLicenciada', methods=['GET', 'POST'])
def dashboardLicenciada():
    """
    Panel principal para Licenciada.
    Permite filtrar y ver OTMs, descargar datos, etc.
    """
    if 'usuario' not in session:
        return redirect(url_for('login'))
    usuario = session['usuario']
    filtradas = otm_data  # Por defecto se muestran todas

    if request.method == "POST":
        desde = request.form.get("fecha_inicio")
        hasta = request.form.get("fecha_fin")
        estado = request.form.get("estado")
        numero = request.form.get("codigo")

        def cumple(otm):
            cumple_fecha = True
            cumple_estado = True
            cumple_numero = True
            if desde:
                cumple_fecha = datetime.strptime(otm["fecha"], "%Y-%m-%d") >= datetime.strptime(desde, "%Y-%m-%d")
            if hasta:
                cumple_fecha = cumple_fecha and datetime.strptime(otm["fecha"], "%Y-%m-%d") <= datetime.strptime(hasta, "%Y-%m-%d")
            if estado:
                cumple_estado = otm["estado"].lower() == estado.lower()
            if numero:
                cumple_numero = numero.lower() in otm["numero"].lower()
            return cumple_fecha and cumple_estado and cumple_numero

        filtradas = [otm for otm in otm_data if cumple(otm)]

    return render_template("dashboardLicenciada.html", otms=filtradas, usuario=usuario)

# ---- REGISTRO DE USUARIOS ----

@app.route('/registrarse', methods=['GET'])
def registrarse():
    """Muestra el formulario de registro de usuario."""
    return render_template('registrarse.html')

@app.route('/registrate', methods=['POST'])
def registrate():
    """
    Procesa el registro de un nuevo usuario.
    Guarda en JSON y redirige al panel según el rol.
    """
    nombre = request.form['nombre']
    correo = request.form['correo']
    username = request.form['username']
    password = request.form['password']
    rol = request.form['rol']

    # Verifica si el usuario ya existe
    for lista in [licenciadas, tecnicosingenieros, secretarias, usuarios_registrados]:
        for user in lista:
            if user['username'] == username:
                error = "El usuario ya existe"
                return render_template('registrarse.html', error=error)

    # Define la profesión y panel según el rol
    if rol == 'SEC':
        profesion = 'Secretaria'
        redirect_url = 'dashboardSecretaria'
    elif rol == 'ING':
        profesion = 'Técnico/Ingeniero'
        redirect_url = 'formulario'
    elif rol == 'LIC':
        profesion = 'Licenciada'
        redirect_url = 'dashboardLicenciada'
    else:
        profesion = ''
        redirect_url = 'login'

    nuevo_usuario = {
        'username': username,
        'password': password,
        'nombre': nombre,
        'profesion': profesion,
        'correo': correo,
        'rol': rol
    }
    usuarios_registrados.append(nuevo_usuario)
    guardar_usuarios(usuarios_registrados)
    session['usuario'] = nuevo_usuario
    return redirect(url_for(redirect_url))

# ---- INICIO DE LA APP ----
if __name__ == '__main__':
    app.run(debug=True)