from flask import Flask, render_template, abort
from pathlib import Path

app = Flask(__name__, template_folder='.', static_folder='.', static_url_path='')


# Página inicial / landing page
@app.route('/')
@app.route('/inicio')
@app.route('/inicio.html')
def inicio():
    return render_template('html/paginas-usuario/inicio.html')


# Portal principal / seleção de matérias
@app.route('/portal')
@app.route('/portal.html')
@app.route('/index')
@app.route('/index.html')
def portal():
    return render_template('html/paginas-usuario/index.html')


# Autenticação
@app.route('/login')
@app.route('/login.html')
def login():
    return render_template('html/paginas-usuario/login.html')


@app.route('/cadastro')
@app.route('/cadastro.html')
def cadastro():
    return render_template('html/paginas-usuario/cadastro_usuario.html')


# Matérias principais
@app.route('/materias/portugues')
@app.route('/materias/portugues.html')
@app.route('/matérias/portugues')
@app.route('/matérias/portugues.html')
def portugues():
    return render_template('html/paginas-materias/português.html')


@app.route('/materias/matematica')
@app.route('/materias/matematica.html')
def matematica():
    return render_template('html/paginas-materias/matematica.html')


@app.route('/materias/historia')
@app.route('/materias/historia.html')
def historia():
    return render_template('html/paginas-materias/historia.html')


@app.route('/materias/geografia')
@app.route('/materias/geografia.html')
def geografia():
    return render_template('html/paginas-materias/geografia.html')


# Temas de Geografia
@app.route('/materias/geografia/mapas')
@app.route('/materias/geografia/mapas.html')
def geografia_mapas():
    return render_template('html/matérias/temas-geo/mapas.html')


@app.route('/materias/geografia/populacao')
@app.route('/materias/geografia/populacao.html')
@app.route('/materias/geografia/população')
@app.route('/materias/geografia/população.html')
def geografia_populacao():
    return render_template('html/matérias/temas-geo/população.html')


@app.route('/materias/geografia/economia')
@app.route('/materias/geografia/economia.html')
def geografia_economia():
    return render_template('html/matérias/temas-geo/economia.html')


@app.route('/materias/geografia/territorio')
@app.route('/materias/geografia/territorio.html')
def geografia_territorio():
    return render_template('html/matérias/temas-geo/territorio.html')


@app.route('/materias/geografia/meio-ambiente')
@app.route('/materias/geografia/meio-ambiente.html')
def geografia_meio_ambiente():
    return render_template('html/matérias/temas-geo/meio-ambiente.html')


# Rotas antigas / compatibilidade com HTML puro
@app.route('/html/<path:filepath>')
def serve_html(filepath):
    p = Path('html') / filepath
    if not p.exists() or p.suffix.lower() != '.html':
        abort(404)
    return render_template(str(p).replace('\\', '/'))


@app.route('/<path:filepath>')
def fallback(filepath):
    if filepath.lower().endswith('.html'):
        p = Path(filepath)
        if p.exists():
            return render_template(str(p).replace('\\', '/'))
    abort(404)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
