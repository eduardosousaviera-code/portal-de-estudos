import os
import sqlite3
from pathlib import Path

from flask import (
    Flask,
    abort,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

RAIZ = Path(__file__).resolve().parent
app = Flask(__name__, template_folder=str(RAIZ), static_folder=None)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "alterar-em-producao")

CAMINHO_BANCO = RAIZ / "banco.db"


def conectar():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    return conexao


def criar_tabela():
    try:
        with conectar() as conexao:
            conexao.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario TEXT NOT NULL UNIQUE,
                    senha_hash TEXT NOT NULL
                )
            """)
    except sqlite3.DatabaseError:
        if CAMINHO_BANCO.exists():
            CAMINHO_BANCO.unlink()
        with conectar() as conexao:
            conexao.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario TEXT NOT NULL UNIQUE,
                    senha_hash TEXT NOT NULL
                )
            """)


criar_tabela()


@app.route("/css/<path:arquivo>")
def servir_css(arquivo):
    return send_from_directory(RAIZ / "css", arquivo)


@app.route("/img/<path:arquivo>")
def servir_img(arquivo):
    return send_from_directory(RAIZ / "img", arquivo)


@app.route("/script/<path:arquivo>")
def servir_script(arquivo):
    return send_from_directory(RAIZ / "script", arquivo)


@app.route("/")
@app.route("/inicio")
@app.route("/inicio.html")
def inicio():
    return render_template("html/paginas-usuario/inicio.html")


@app.route("/portal")
@app.route("/portal.html")
@app.route("/index")
@app.route("/index.html")
def portal():
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    return render_template("html/paginas-usuario/index.html")


@app.route("/login", methods=["GET", "POST"])
@app.route("/login.html", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        senha = request.form.get("senha", "")

        if not usuario or not senha:
            return render_template(
                "html/paginas-usuario/login.html",
                erro="Preencha o usuário e a senha.",
            )

        with conectar() as conexao:
            pessoa = conexao.execute(
                "SELECT id, usuario, senha_hash FROM usuarios WHERE usuario = ?",
                (usuario,),
            ).fetchone()

        if pessoa and check_password_hash(pessoa["senha_hash"], senha):
            session["usuario_id"] = pessoa["id"]
            session["usuario"] = pessoa["usuario"]
            return redirect(url_for("portal"))

        return render_template(
            "html/paginas-usuario/login.html",
            erro="Usuário ou senha incorretos.",
        )

    return render_template("html/paginas-usuario/login.html")


@app.route("/cadastro", methods=["GET", "POST"])
@app.route("/cadastro.html", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        senha = request.form.get("senha", "")
        confirmar_senha = request.form.get("confirmar_senha", "")

        if not usuario or not senha:
            return render_template(
                "html/paginas-usuario/cadastro_usuario.html",
                erro="Preencha o usuário e a senha.",
            )

        if senha != confirmar_senha:
            return render_template(
                "html/paginas-usuario/cadastro_usuario.html",
                erro="As senhas não conferem.",
            )

        senha_hash = generate_password_hash(senha)

        try:
            with conectar() as conexao:
                conexao.execute(
                    "INSERT INTO usuarios (usuario, senha_hash) VALUES (?, ?)",
                    (usuario, senha_hash),
                )
        except sqlite3.IntegrityError:
            return render_template(
                "html/paginas-usuario/cadastro_usuario.html",
                erro="Esse nome de usuário já existe.",
            )

        return redirect(url_for("login"))

    return render_template("html/paginas-usuario/cadastro_usuario.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("inicio"))


@app.route("/materias/portugues")
@app.route("/materias/portugues.html")
@app.route("/matérias/portugues")
@app.route("/matérias/portugues.html")
def portugues():
    return render_template("html/paginas-materias/português.html")


@app.route("/materias/matematica")
@app.route("/materias/matematica.html")
def matematica():
    return render_template("html/paginas-materias/matematica.html")


@app.route("/materias/historia")
@app.route("/materias/historia.html")
def historia():
    return render_template("html/paginas-materias/historia.html")


@app.route("/materias/geografia")
@app.route("/materias/geografia.html")
def geografia():
    return render_template("html/paginas-materias/geografia.html")


@app.route("/materias/geografia/mapas")
@app.route("/materias/geografia/mapas.html")
def geografia_mapas():
    return render_template("html/matérias/temas-geo/mapas.html")


@app.route("/materias/geografia/populacao")
@app.route("/materias/geografia/populacao.html")
@app.route("/materias/geografia/população")
@app.route("/materias/geografia/população.html")
def geografia_populacao():
    return render_template("html/matérias/temas-geo/população.html")


@app.route("/materias/geografia/economia")
@app.route("/materias/geografia/economia.html")
def geografia_economia():
    return render_template("html/matérias/temas-geo/economia.html")


@app.route("/materias/geografia/territorio")
@app.route("/materias/geografia/territorio.html")
def geografia_territorio():
    return render_template("html/matérias/temas-geo/territorio.html")


@app.route("/materias/geografia/meio-ambiente")
@app.route("/materias/geografia/meio-ambiente.html")
def geografia_meio_ambiente():
    return render_template("html/matérias/temas-geo/meio-ambiente.html")


@app.route("/html/<path:filepath>")
def serve_html(filepath):
    pagina = RAIZ / "html" / filepath
    if not pagina.exists() or pagina.suffix.lower() != ".html":
        abort(404)
    return render_template(str(pagina.relative_to(RAIZ)).replace("\\", "/"))


@app.route("/<path:filepath>")
def fallback(filepath):
    if filepath.lower().endswith(".html"):
        pagina = RAIZ / filepath
        if pagina.exists():
            return render_template(str(pagina.relative_to(RAIZ)).replace("\\", "/"))
    abort(404)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
