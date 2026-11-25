import os
import re
import sqlite3
from html import escape as escape_html
from pathlib import Path

from flask import Flask, abort, jsonify, redirect, render_template, request, session, url_for
from werkzeug.exceptions import BadRequest
from werkzeug.security import check_password_hash, generate_password_hash

from banco import inicializar_banco, obter_conexao

RAIZ = Path(__file__).resolve().parent
app = Flask(__name__, template_folder=str(RAIZ), static_folder=None)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "chave-de-desenvolvimento-altere-em-producao")

# Cria banco.db e a tabela de usuários na primeira execução.
inicializar_banco()

RESPOSTAS_CORRETAS_MEIO_AMBIENTE = {
    "q1": "b",
    "q2": "c",
    "q3": "a",
}


@app.after_request
def exibir_usuario_logado(response):
    usuario = session.get("usuario")
    if (
        not usuario
        or request.endpoint in {"inicio", "login", "cadastro"}
        or response.mimetype != "text/html"
    ):
        return response

    conteudo = response.get_data(as_text=True)
    header_existe = re.search(r"<header\b", conteudo, flags=re.IGNORECASE) is not None
    if not header_existe and re.search(r"<body\b", conteudo, flags=re.IGNORECASE) is None:
        return response

    classe_selo = "usuario-sessao" if header_existe else "usuario-sessao usuario-sessao--flutuante"
    selo = f'<span class="{classe_selo}">{escape_html(usuario)}</span>'
    seletor = r"(<header\b[^>]*>)" if header_existe else r"(<body\b[^>]*>)"
    conteudo, inseridos = re.subn(
        seletor,
        lambda correspondencia: correspondencia.group(1) + selo,
        conteudo,
        count=1,
        flags=re.IGNORECASE,
    )
    if inseridos:
        response.set_data(conteudo)
    return response


@app.route("/css/<path:arquivo>")
def servir_css(arquivo):
    return app.send_static_file(arquivo) if False else __import__("flask").send_from_directory(RAIZ / "css", arquivo)


@app.route("/img/<path:arquivo>")
def servir_img(arquivo):
    return __import__("flask").send_from_directory(RAIZ / "img", arquivo)


@app.route("/script/<path:arquivo>")
def servir_script(arquivo):
    return __import__("flask").send_from_directory(RAIZ / "script", arquivo)


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
    if "usuario" not in session:
        return redirect(url_for("login"))
    return render_template("html/paginas-usuario/index.html")


@app.route("/login", methods=["GET", "POST"])
@app.route("/login.html", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        senha = request.form.get("senha", "")
        if not usuario or not senha:
            return render_template("html/paginas-usuario/login.html", erro="Preencha usuário e senha."), 400

        with obter_conexao() as conexao:
            conta = conexao.execute(
                "SELECT usuario, senha_hash FROM usuarios WHERE usuario = ?",
                (usuario,),
            ).fetchone()

        if conta is None or not check_password_hash(conta["senha_hash"], senha):
            return render_template("html/paginas-usuario/login.html", erro="Usuário ou senha incorretos."), 401

        session.clear()
        session["usuario"] = conta["usuario"]
        return redirect(url_for("portal"))

    return render_template("html/paginas-usuario/login.html")


@app.route("/cadastro", methods=["GET", "POST"])
@app.route("/cadastro.html", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        senha = request.form.get("senha", "")
        confirmar_senha = request.form.get("confirmar_senha", "")

        if not usuario or not senha:
            return render_template("html/paginas-usuario/cadastro_usuario.html", erro="Preencha usuário e senha."), 400
        if senha != confirmar_senha:
            return render_template("html/paginas-usuario/cadastro_usuario.html", erro="As senhas não conferem."), 400

        try:
            with obter_conexao() as conexao:
                conexao.execute(
                    "INSERT INTO usuarios (usuario, senha_hash) VALUES (?, ?)",
                    (usuario, generate_password_hash(senha)),
                )
        except sqlite3.IntegrityError:
            return render_template("html/paginas-usuario/cadastro_usuario.html", erro="Esse usuário já existe."), 409

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


@app.route("/api/progresso/meio-ambiente", methods=["GET", "POST"])
def progresso_meio_ambiente():
    usuario = session.get("usuario")
    if not usuario:
        return jsonify(erro="Faça login para salvar seu progresso."), 401

    with obter_conexao() as conexao:
        conta = conexao.execute(
            "SELECT id FROM usuarios WHERE usuario = ?",
            (usuario,),
        ).fetchone()
        if conta is None:
            session.clear()
            return jsonify(erro="Sua sessão expirou. Faça login novamente."), 401

        usuario_id = conta["id"]

        if request.method == "GET":
            linhas = conexao.execute(
                """
                SELECT pergunta_id, alternativa
                FROM respostas_meio_ambiente
                WHERE usuario_id = ?
                """,
                (usuario_id,),
            ).fetchall()
            respostas = {linha["pergunta_id"]: linha["alternativa"] for linha in linhas}
            resultado = {
                "answers": respostas,
                "results": {
                    pergunta_id: alternativa == RESPOSTAS_CORRETAS_MEIO_AMBIENTE[pergunta_id]
                    for pergunta_id, alternativa in respostas.items()
                } if len(respostas) == len(RESPOSTAS_CORRETAS_MEIO_AMBIENTE) else None,
                "correct_count": sum(
                    respostas.get(pergunta_id) == alternativa_correta
                    for pergunta_id, alternativa_correta in RESPOSTAS_CORRETAS_MEIO_AMBIENTE.items()
                ) if len(respostas) == len(RESPOSTAS_CORRETAS_MEIO_AMBIENTE) else None,
            }
            return jsonify(resultado)

        if not request.is_json:
            return jsonify(erro="Envie as respostas em formato JSON."), 400

        try:
            dados = request.get_json()
        except BadRequest:
            return jsonify(erro="As respostas enviadas não são um JSON válido."), 400
        respostas = dados.get("answers") if isinstance(dados, dict) else None
        if (
            not isinstance(respostas, dict)
            or set(respostas) != set(RESPOSTAS_CORRETAS_MEIO_AMBIENTE)
            or any(
                not isinstance(alternativa, str) or alternativa not in {"a", "b", "c", "d"}
                for alternativa in respostas.values()
            )
        ):
            return jsonify(erro="Selecione uma alternativa para cada pergunta."), 400

        conexao.executemany(
            """
            INSERT INTO respostas_meio_ambiente (usuario_id, pergunta_id, alternativa)
            VALUES (?, ?, ?)
            ON CONFLICT(usuario_id, pergunta_id)
            DO UPDATE SET alternativa = excluded.alternativa
            """,
            [
                (usuario_id, pergunta_id, alternativa)
                for pergunta_id, alternativa in respostas.items()
            ],
        )

    resultados = {
        pergunta_id: respostas[pergunta_id] == alternativa_correta
        for pergunta_id, alternativa_correta in RESPOSTAS_CORRETAS_MEIO_AMBIENTE.items()
    }
    return jsonify(
        answers=respostas,
        results=resultados,
        correct_count=sum(resultados.values()),
    )


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
