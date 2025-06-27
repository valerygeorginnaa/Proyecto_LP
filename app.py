from flask import Flask, render_template, request
app = Flask(__name__)
app.secret_key = 'clave-secreta'

@app.route('/', methods=['GET', 'POST'])
def formulario():
    if request.method == 'POST':
        nombre = request.form['nombre']
        edad = request.form['edad']
        return f"Hola {nombre}, tienes {edad} años."
    return render_template('formulario.html')

if __name__ == '__main__':
    app.run(debug=True)
