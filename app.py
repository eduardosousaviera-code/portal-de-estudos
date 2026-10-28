from pathlib import Path

from flask import Flask, render_template, abort

app = Flask(__name__, template_folder='.', static_folder='.', static_url_path='')


@app.route('/')
def root():
    return render_template('html/paginas-usuario/index.html')


@app.route('/inicio')
@app.route('/inicio.html')
def inicio():
    return render_template('html/paginas-usuario/inicio.html')


@app.route('/login')
@app.route('/login.html')
def login():
    return render_template('html/paginas-usuario/login.html')


@app.route('/cadastro')
@app.route('/cadastro.html')
@app.route('/cadastro_usuario.html')
def cadastro():
    return render_template('html/paginas-usuario/cadastro_usuario.html')


@app.route('/html/<path:filepath>')
def serve_html(filepath: str):
    full_path = Path('html') / filepath

    if not full_path.exists() or full_path.suffix.lower() != '.html':
        abort(404)

    return render_template(str(full_path).replace('\\', '/'))


@app.route('/<path:filepath>')
def fallback(filepath: str):
    if filepath.lower().endswith('.html'):
        candidate = Path(filepath)
        if candidate.exists():
            return render_template(str(candidate).replace('\\', '/'))

    abort(404)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
