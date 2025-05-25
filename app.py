from flask import Flask, render_template, request, redirect, url_for
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

registros = []
contador_id = 1

@app.route('/')
def index():
    total = 0
    for r in registros:
        if r['tipo'] == 'ingreso':
            total += r['monto']
        else:
            total -= r['monto']
    return render_template('index.html', registros=registros, total=total)

@app.route('/agregar', methods=['POST'])
def agregar():
    global contador_id
    descripcion = request.form['descripcion']
    monto = float(request.form['monto'])
    tipo = request.form['tipo']
    fecha = request.form['fecha']
    categoria = request.form['categoria']

    nuevo_registro = {
        'id': contador_id,
        'descripcion': descripcion,
        'monto': monto,
        'tipo': tipo,
        'fecha': fecha,
        'categoria': categoria
    }
    registros.append(nuevo_registro)
    contador_id += 1
    return redirect(url_for('index'))

@app.route('/eliminar/<int:id>')
def eliminar(id):
    global registros
    registros = [r for r in registros if r['id'] != id]
    return redirect(url_for('index'))

@app.route('/editar/<int:id>')
def editar(id):
    registro = next((r for r in registros if r['id'] == id), None)
    return render_template('editar.html', registro=registro)

@app.route('/actualizar/<int:id>', methods=['POST'])
def actualizar(id):
    for r in registros:
        if r['id'] == id:
            r['descripcion'] = request.form['descripcion']
            r['monto'] = float(request.form['monto'])
            r['tipo'] = request.form['tipo']
            r['fecha'] = request.form['fecha']
            r['categoria'] = request.form['categoria']
            break
    return redirect(url_for('index'))

@app.route('/filtrar', methods=['POST'])
def filtrar():
    tipo = request.form['tipo']
    categoria = request.form['categoria']
    fecha_inicio = request.form['fecha_inicio']
    fecha_fin = request.form['fecha_fin']

    registros_filtrados = []
    for r in registros:
        if (tipo == 'todos' or r['tipo'] == tipo) and            (categoria == 'todas' or r['categoria'] == categoria) and            (not fecha_inicio or r['fecha'] >= fecha_inicio) and            (not fecha_fin or r['fecha'] <= fecha_fin):
            registros_filtrados.append(r)

    total = sum(r['monto'] if r['tipo'] == 'ingreso' else -r['monto'] for r in registros_filtrados)
    return render_template('index.html', registros=registros_filtrados, total=total)

@app.route('/graficas')
def graficas():
    categorias = {}
    for r in registros:
        key = f"{r['categoria']} ({r['tipo']})"
        categorias[key] = categorias.get(key, 0) + r['monto']

    labels = list(categorias.keys())
    values = list(categorias.values())

    plt.figure(figsize=(8, 6))
    plt.barh(labels, values, color='skyblue')
    plt.title("Total por Categoría (Ingresos y Gastos)")
    plt.xlabel("Monto")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close()

    return f'''
    <html>
        <head>
            <title>Gráficas</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body class="bg-light">
            <div class="container mt-5 p-4 bg-white shadow rounded text-center">
                <h2 class="mb-4 text-primary">📊 Gráfica de Registros</h2>
                <img src="data:image/png;base64,{img_base64}" class="img-fluid"/>
                <br><br>
                <a href="/" class="btn btn-secondary">Volver</a>
            </div>
        </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True)
