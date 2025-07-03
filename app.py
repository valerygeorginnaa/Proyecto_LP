from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Variables globales para almacenar datos de OTM
otm_parcial = {}   # Guarda temporalmente los datos del Formulario 1
otm_data = []      # Lista de OTMs completas

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
            datos[campo] = request.form.get(campo, '').strip()

        datos['prioridad'] = request.form.get('prioridad', '')
        datos['modalidad'] = request.form.getlist('modalidad[]')

        otm_parcial = datos
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
            'impuestos', 'total_general'
        ]

        for campo in campos_form2:
            datos_form2[campo] = request.form.get(campo, '').strip()

        # Fusionar los datos del formulario 1 y 2
        otm_completa = {**otm_parcial, **datos_form2}
        otm_data.append(otm_completa)

        # Limpiar datos parciales
        otm_parcial = {}

        return redirect(url_for('resumen'))

    return render_template('formulario2.html')

@app.route('/resumen')
def resumen():
    return render_template('resumen.html', otms=otm_data)

if __name__ == '__main__':
    app.run(debug=True)
