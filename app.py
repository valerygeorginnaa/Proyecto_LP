from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

# Carpeta para guardar firmas y sellos
UPLOAD_FOLDER = 'static/firmas'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Variables globales para almacenar OTM sin base de datos
otm_parcial = {}   # Guarda temporalmente formulario 1
otm_data = []      # Lista completa de OTMs ingresadas

@app.route('/')
def inicio():
    return redirect(url_for('formulario'))

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
            valor = request.form.get(campo, '').strip()
            datos[campo] = valor

        # Prioridad
        datos['prioridad'] = request.form.get('prioridad', '')

        # Modalidades (checkbox múltiple)
        datos['modalidad'] = request.form.getlist('modalidad[]')

        # Guardar archivo firma del solicitante
        firma_archivo = request.files.get('firma_archivo')
        if firma_archivo and firma_archivo.filename:
            ruta = os.path.join(app.config['UPLOAD_FOLDER'], firma_archivo.filename)
            firma_archivo.save(ruta)
            datos['firma_solicitante'] = ruta

        # Guardar archivo sello de recepción
        sello_archivo = request.files.get('sello_archivo')
        if sello_archivo and sello_archivo.filename:
            ruta = os.path.join(app.config['UPLOAD_FOLDER'], sello_archivo.filename)
            sello_archivo.save(ruta)
            datos['firma_recepcion'] = ruta

        otm_parcial = datos  # Guardar temporalmente

        return redirect(url_for('formulario2'))

    return render_template('formulario.html')

@app.route('/formulario2', methods=['GET', 'POST'])
def formulario2():
    global otm_parcial, otm_data

    if request.method == 'POST':
        datos_form2 = {}
        campos_form2 = [
            'nombre_tecnico', 'especialidad', 'horas', 'valor_hora', 'costo_mo',
            'origen', 'descripcion_material', 'um', 'cantidad', 'costo_unitario',
            'costo_parcial', 'total_mo', 'total_materiales', 'otros_gastos',
            'impuestos', 'total_general', 'firma_ejecutor', 'firma_jefe'
        ]

        for campo in campos_form2:
            valor = request.form.get(campo, '').strip()
            datos_form2[campo] = valor

        # Subida de firmas en formulario 2 (si las usas como archivos)
        firma_ejecutor_file = request.files.get('firma_ejecutor_file')
        if firma_ejecutor_file and firma_ejecutor_file.filename:
            ruta = os.path.join(app.config['UPLOAD_FOLDER'], firma_ejecutor_file.filename)
            firma_ejecutor_file.save(ruta)
            datos_form2['firma_ejecutor'] = ruta

        firma_jefe_file = request.files.get('firma_jefe_file')
        if firma_jefe_file and firma_jefe_file.filename:
            ruta = os.path.join(app.config['UPLOAD_FOLDER'], firma_jefe_file.filename)
            firma_jefe_file.save(ruta)
            datos_form2['firma_jefe'] = ruta

        # Fusionar los datos del form1 y form2
        otm_completa = {**otm_parcial, **datos_form2}
        otm_data.append(otm_completa)

        print("\n✅ OTM guardada correctamente:")
        for k, v in otm_completa.items():
            print(f"{k}: {v}")

        # Limpia el parcial
        otm_parcial = {}

        return redirect(url_for('resumen'))

    return render_template('formulario2.html')

@app.route('/resumen')
def resumen():
    return render_template('resumen.html', otms=otm_data)

if __name__ == '__main__':
    app.run(debug=True)
