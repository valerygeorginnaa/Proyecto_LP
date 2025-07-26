
#primero se descarga el  flask , si no lo tienes usa esto en tu temrinal -> pip install flask
#leugo lo ejecutas 
#el temrinal eses http://127.0.0.1:5000/login
from usuariosdelsistema import licenciadas, tecnicosingenieros, secretarias
from datos_otm_detalle import otm_detalle_data
from flask import Flask, render_template, request, redirect, url_for, session,send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
from datetime import datetime
import os
from DownloadPDFformat import generar_pdf_otm_completo_formato
app = Flask(__name__)
app.secret_key = 'supersecreto'  # Necesario para sesiones

# Variables globales para almacenar datos de OTM
otm_parcial = {}   # Guarda temporalmente los datos del Formulario 1
otm_data = [
    {"numero": "OTM001", "fecha": "2024-06-01", "estado": "Por Archivar"},
    {"numero": "OTM002", "fecha": "2024-06-03", "estado": "Archivado"},
    {"numero": "OTM003", "fecha": "2024-06-05", "estado": "Por Archivar"},
    {"numero": "OTM004", "fecha": "2024-06-07", "estado": "Archivado"},
    {"numero": "OTM005", "fecha": "2024-06-09", "estado": "Por Archivar"},
    {"numero": "OTM006", "fecha": "2024-06-11", "estado": "Archivado"},
    {"numero": "OTM007", "fecha": "2024-06-13", "estado": "Por Archivar"},
    {"numero": "OTM008", "fecha": "2024-06-15", "estado": "Archivado"},
    {"numero": "OTM009", "fecha": "2024-06-17", "estado": "Por Archivar"},
    {"numero": "OTM010", "fecha": "2024-06-19", "estado": "Archivado"},
    {"numero": "OTM011", "fecha": "2024-06-21", "estado": "Por Archivar"},
    {"numero": "OTM012", "fecha": "2024-06-23", "estado": "Archivado"},
    {"numero": "OTM013", "fecha": "2024-06-25", "estado": "Por Archivar"},
    {"numero": "OTM014", "fecha": "2024-06-27", "estado": "Archivado"},
    {"numero": "OTM015", "fecha": "2024-06-29", "estado": "Por Archivar"},
    {"numero": "OTM016", "fecha": "2024-07-01", "estado": "Archivado"},
    {"numero": "OTM017", "fecha": "2024-07-03", "estado": "Por Archivar"},
    {"numero": "OTM018", "fecha": "2024-07-05", "estado": "Archivado"},
    {"numero": "OTM019", "fecha": "2024-07-07", "estado": "Por Archivar"},
    {"numero": "OTM020", "fecha": "2024-07-09", "estado": "Archivado"},
]  
otm_data_completo= []   # Lista de OTMs completas

@app.route('/')
def inicio():
    return redirect(url_for('login'))
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Buscar en técnicos
        for user in tecnicosingenieros:
            if user['username'] == username and user['password'] == password:
                session['usuario'] = username
                return redirect(url_for('formulario'))  # Ruta para técnico

        # Buscar en licenciadas
        for user in licenciadas:
            if user['username'] == username and user['password'] == password:
                session['usuario'] = username
                return redirect(url_for('dashboardLicenciada'))  # Ruta para licenciada

        # Buscar en secretarias
        for user in secretarias:
            if user['username'] == username and user['password'] == password:
                session['usuario'] = username
                return redirect(url_for('dashboardSecretaria'))  # Ruta para secretaria

        error = 'Usuario o contraseña incorrectos'

    return render_template('login.html', error=error)



@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
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
    global otm_parcial, otm_data_completa

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


        # Limpiar datos parciales
        otm_parcial = {}

        return redirect(url_for('resumen'))

    return render_template('formulario2.html')

@app.route('/resumen')
def resumen():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('resumen.html', otms=otm_data_completo)







    


@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))





#para descargar el excel se instala en su temrinal -> pip install pandas openpyxl
from Download import generar_excel_otm
import pandas as pd
@app.route('/descargar_excel')
def descargar_excel():
    output, error, status = generar_excel_otm(otm_data_completo)
    if status != 200:
        return error, status
    return send_file(
        output,
        download_name=f'OTM-{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

# -> pip install reportlab 
@app.route('/descargar_pdf/<numero>')
def descargar_pdf(numero):
    otm = next((o for o in otm_detalle_data if o["numero"] == numero), None)
    if not otm:
        return "OTM no encontrada", 404

    buffer = generar_pdf_otm_completo_formato(otm)  # Usa la misma función que `ver_detalle`
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'OTM-{numero}.pdf',
        mimetype='application/pdf'
    )



@app.route("/dashboardSecretaria", methods=["GET", "POST"])
def dashboardSecretaria():
    session['rol'] = 'secretaria'  # ← Aquí guardas el rol

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

    return render_template("dashboardSecretaria.html", otms=filtradas)




@app.route('/archivar_otm/<numero>', methods=['POST'])
def archivar_otm(numero):
    for otm in otm_data:
        if otm["numero"] == numero:
            otm["estado"] = "Archivado"  # ✅ Aquí se cambia el estado
    return redirect(url_for('dashboardSecretaria'))

@app.route('/ver_detalle/<numero>')
def ver_detalle(numero):
    detalle_otm = next((otm for otm in otm_detalle_data if otm["numero"] == numero), None)

    if not detalle_otm:
        return "OTM no encontrada", 404

    return render_template('verDetalle.html', otm=detalle_otm)

@app.route("/dashboardLicenciada", methods=["GET", "POST"])
def dashboardLicenciada():
    session['rol'] = 'licenciada'  # ← Aquí también

    filtradas = otm_data

    if request.method == "POST":
        estado = request.form.get("estado")
        numero = request.form.get("codigo")

        def cumple(otm):
            cumple_estado = True
            cumple_numero = True
            if estado:
                cumple_estado = otm["estado"].lower() == estado.lower()
            if numero:
                cumple_numero = numero.lower() in otm["numero"].lower()
            return cumple_estado and cumple_numero

        filtradas = [otm for otm in otm_data if cumple(otm)]

    return render_template("dashboardLicenciada.html", otms=otm_detalle_data)


@app.route('/firmar_otm/<numero>', methods=['POST'])
def firmar_otm(numero):
    for otm in otm_detalle_data:
        if otm["numero"] == numero:
            otm["firmado"] = True
            otm["firmado_por"] = "licenciada"
            break
    return redirect(url_for('ver_detalle', numero=numero))


@app.route('/reportes_adicionales')
def reportes_adicionales():
    # Aquí puedes cargar datos desde la base de datos o estructuras en memoria
    return render_template('reportesAdicionales.html')


# CRUD RESUMEN.HTML
@app.route('/eliminar_otm/<int:index>', methods=['POST'])
def eliminar_otm(index):
    if 0 <= index < len(otm_data_completo):
        otm_data_completo.pop(index)
    return redirect(url_for('resumen'))

@app.route('/editar_otm/<int:index>', methods=['GET', 'POST'])
def editar_otm(index):
    if 0 <= index < len(otm_data_completo):
        if request.method == 'POST':
            for key in otm_data_completo[index]:
                otm_data_completo[index][key] = request.form.get(key, otm_data_completo[index][key])
            return redirect(url_for('resumen'))
        return render_template('editar_otm.html', otm=otm_data_completo[index], index=index)
    return redirect(url_for('resumen'))


from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
from datetime import datetime
import os

def generar_pdf_otm_completo_formato(otm):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Encabezado
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, height - 50, "ORDEN DE TRABAJO DE MANTENIMIENTO (OTM)")

    # Línea divisoria
    pdf.setLineWidth(0.5)
    pdf.line(50, height - 60, width - 50, height - 60)

    pdf.setFont("Helvetica", 11)

    y = height - 90
    salto = 18

    campos = [
        ("Número", otm["numero"]),
        ("Fecha", otm["fecha"]),
        ("Servicio", otm["servicio"]),
        ("Equipo", otm["equipo"]),
        ("Marca", otm["marca"]),
        ("Modelo", otm["modelo"]),
        ("Serie", otm["serie"]),
        ("Código", otm["codigo"]),
        ("Falla Reportada", otm["falla"]),
        ("Solicita", otm["solicita"]),
        ("Cargo", otm["cargo"]),
        ("Fecha Solicitud", otm["fecha_solicitud"]),
        ("Estado", otm["estado"]),
        ("Acciones Realizadas", otm["acciones"]),
        ("Responsable", otm["responsable"]),
        ("Fecha Ejecución", otm["fecha_ejecucion"]),
        ("Observaciones", otm["observaciones"]),
        ("Materiales Utilizados", otm["materiales"]),
        ("Costo Mano de Obra", f"S/ {otm['mano_obra']}"),
        ("Costo Total", f"S/ {otm['costo_total']}"),
    ]

    for label, value in campos:
        pdf.drawString(50, y, f"{label}:")
        pdf.drawString(200, y, str(value))
        y -= salto
        if y < 120:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 11)

    # Agregar firma y sello si fue firmado por la licenciada
    if otm.get("firmado") and otm.get("firmado_por") == "licenciada":
        # Coordenadas fijas desde el borde inferior
        firma_y = 100  # posición vertical para la firma
        firma_width = 150
        firma_height = 50
        sello_width = 70
        sello_height = 70

        firma_x = (width - firma_width) / 2  # centrado horizontal


        # Firma
        firma_path = os.path.join("static", "firmas", "firma_licfernandez.png")
    # Agregar firma y sello si fue firmado por la licenciada
    if otm.get("firmado") and otm.get("firmado_por") == "licenciada":
        # Coordenadas base
        firma_y = 100  # altura desde el borde inferior
        firma_width = 150
        firma_height = 50
        sello_width = 70
        sello_height = 70

        # Firma centrada
        firma_x = (width - firma_width) / 2

        # Firma
        firma_path = os.path.join("static", "firmas", "firma_licfernandez.png")
        if os.path.exists(firma_path):
            pdf.drawImage(firma_path, firma_x, firma_y, width=firma_width, height=firma_height)

        # Sello (a la derecha de la firma)
        sello_path = os.path.join("static", "sellos", "sello_licfernandez.png")
        if os.path.exists(sello_path):
            sello_x = firma_x + firma_width + 20
            sello_y = firma_y - 5
            pdf.drawImage(sello_path, sello_x, sello_y, width=sello_width, height=sello_height)

        # Nombre y cargo debajo de la firma
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawCentredString(width / 2, firma_y - 20, "Licenciada Fernández")
        pdf.setFont("Helvetica", 11)
        pdf.drawCentredString(width / 2, firma_y - 35, "Responsable de Área")

        # Fecha de firma debajo del nombre
        pdf.setFont("Helvetica", 10)
        pdf.drawCentredString(width / 2, firma_y - 50, f"Fecha de Firma: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer


if __name__ == '__main__':
    app.run(debug=True)


