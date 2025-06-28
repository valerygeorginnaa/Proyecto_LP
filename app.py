from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def inicio():
    return redirect(url_for('formulario'))

@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    if request.method == 'POST':
        return redirect(url_for('formulario2'))
    return render_template('formulario.html')

@app.route('/formulario2', methods=['GET', 'POST'])
def formulario2():
    if request.method == 'POST':
        return "Formulario enviado correctamente ✅"
    return render_template('formulario2.html')

if __name__ == '__main__':
    app.run(debug=True)
