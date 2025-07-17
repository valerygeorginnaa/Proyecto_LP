
#primero se descarga el  flask , si no lo tienes usa esto en tu temrinal -> pip install flask
#leugo lo ejecutas 
#el temrinal eses http://127.0.0.1:5000/login


from flask import Flask, render_template, request, redirect, url_for, session,send_file
from reportlab.pdfgen import canvas
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'supersecreto'  # Necesario para sesiones



# Variables globales para almacenar datos de OTM
otm_parcial = {}   # Guarda temporalmente los datos del Formulario 1
otm_data = []      # Lista de OTMs completas

@app.route('/')
def inicio():
    return redirect(url_for('login'))
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Verificamos credenciales
        if username == 'admin' and password == '123456':
            session['usuario'] = username
            return redirect(url_for('formulario'))  # Ruta del ingeniero o tecnico biomedico
        elif username == 'secretaria' and password == '123456':
            session['usuario'] = username
            return redirect(url_for('dashboardSecretaria'))  # Ruta de secretaria (area de ingenieria clinica)
        else:
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
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('resumen.html', otms=otm_data)





    


@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))





#para descargar el excel se instala en su temrinal -> pip install pandas openpyxl
from Download import generar_excel_otm
import pandas as pd
@app.route('/descargar_excel')
def descargar_excel():
    output, error, status = generar_excel_otm(otm_data)
    if status != 200:
        return error, status
    return send_file(
        output,
        download_name=f'OTM-{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

# -> pip install reportlab 
@app.route('/descargar_pdf/<int:index>')
def descargar_pdf(index):
    if 0 <= index < len(otm_data):
        otm = otm_data[index]

        # Crear un PDF en memoria
        buffer = BytesIO()
        p = canvas.Canvas(buffer)
        p.setFont("Helvetica", 12)

        y = 800
        for key, value in otm.items():
            texto = f"{key.replace('_', ' ').capitalize()}: {value}"
            p.drawString(50, y, texto)
            y -= 20
            if y < 50:
                p.showPage()
                y = 800

        p.save()
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'OTM-{index+1}.pdf',
            mimetype='application/pdf'
        )

    return "OTM no encontrada", 404

@app.route('/dashboardSecretaria')
def dashboardSecretaria():
    if 'usuario' not in session or session['usuario'] != 'secretaria':
        return redirect(url_for('login'))
    return render_template('dashboardSecretaria.html', otms=otm_data)

if __name__ == '__main__':
    app.run(debug=True)


