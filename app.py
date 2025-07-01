import datetime

from flask import Flask, render_template, request, redirect, url_for,send_file, session
import os
import pandas as pd
from io import BytesIO
from openpyxl.utils import get_column_letter
app = Flask(__name__)

# Carpeta para guardar las firmas
UPLOAD_FOLDER = 'static/firmas'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.secret_key = '1234'
@app.route('/')
def inicio():
    return redirect(url_for('formulario'))

@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    if request.method == 'POST':
        datos = {}
        campos = [
            'dependencia', 'numero', 'fecha', 'area', 'ubicacion',
            'denominacion', 'marca', 'modelo', 'serie', 'codigo_patrimonial',
            'problema', 'firma_solicitante', 'fecha_solicitud',
            'firma_recepcion', 'fecha_recepcion', 'diagnostico',
            'encargado', 'fecha_mantenimiento', 'trabajo', 'fecha_inicio',
            'fecha_termino', 'garantia', 'costo', 'recomendaciones'
        ]
        
        for campo in campos:
            valor = request.form.get(campo, '').strip()
            if valor:
                datos[campo] = valor

        prioridad = request.form.get('prioridad')
        if prioridad:
            datos['prioridad'] = prioridad

        modalidades = request.form.getlist('modalidad[]')
        if modalidades:
            datos['modalidad'] = modalidades

        print("\n📝 Datos del Formulario 1:")
        for k, v in datos.items():
            print(f"{k}: {v}")
        session['datos_formulario'] = datos

        return redirect(url_for('formulario2'))

    return render_template('formulario.html')

@app.route('/formulario2', methods=['GET', 'POST'])
def formulario2():
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
            if valor:
                datos_form2[campo] = valor

        # Subida de archivos de firma/sello
        firmas = {}
        archivos = {
            'firma_ejecutor_archivo': 'firma_ejecutor_file',
            'firma_jefe_archivo': 'firma_jefe_file'
        }

        for clave, input_file in archivos.items():
            archivo = request.files.get(input_file)
            if archivo and archivo.filename:
                ext = archivo.filename.rsplit('.', 1)[-1].lower()
                if ext in ['jpg', 'jpeg', 'png', 'pdf']:
                    ruta = os.path.join(app.config['UPLOAD_FOLDER'], archivo.filename)
                    archivo.save(ruta)
                    firmas[clave] = ruta

        print("\n📄 Datos del Formulario 2:")
        for k, v in datos_form2.items():
            print(f"{k}: {v}")
        print("\n📎 Archivos de firma:")
        for k, v in firmas.items():
            print(f"{k}: {v}")

        return "Formulario completo enviado correctamente ✅"

    return render_template('formulario2.html')
@app.route('/descargar_excel')
def descargar_excel():
    datos = session.get('datos_formulario', {})
    if not datos:
        return "No hay datos para exportar", 400

    df = pd.DataFrame([datos])
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
        worksheet = writer.sheets['Sheet1']
        for i, col in enumerate(df.columns, 1):
            max_length = max(
                [len(str(s)) for s in df[col].values] + [len(str(col))]
            )
            worksheet.column_dimensions[get_column_letter(i)].width = max_length + 2

    output.seek(0)
    return send_file(
        output,
        download_name=f'formulario_{datetime.datetime.now().strftime("%Y-%m-%d")}.xlsx',
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
if __name__ == '__main__':
    app.run(debug=True)
