from flask import Blueprint, request, jsonify, abort
from conectar.funcaoConectar import conectar

estudante_bp = Blueprint("estudante", __name__)

##############################################
#ROTAS PARA A TABELA estudante

##ROTA GET
##############################################
@estudante_bp.route("/estudante", methods=["GET"])
def listar_estudante():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT idEstudante, nome, turma, matricula, contato FROM estudante")
    dados = [
        {"idEstudante": row[0], "nome": row[1], "turma": row[2], "matricula": row[3], "contato": row[4]}
        for row in cursor.fetchall()
    ]
    conn.close()
    return jsonify(dados)

##ROTA DELETE
#############################################
from flask import jsonify, abort

@estudante_bp.route("/estudante/<int:idEstudante>", methods=["DELETE"])
def deletar_estudante(idEstudante):
    conn = conectar()
    cursor = conn.cursor()

    # tenta apagar o registro informado
    cursor.execute("DELETE FROM estudante WHERE idEstudante = %s", (idEstudante,))
    conn.commit()

    # cursor.rowcount informa quantas linhas foram afetadas
    if cursor.rowcount == 0:
        conn.close()
        # nenhum registro com esse ID → devolve 404
        abort(404, description="Não encontrado")

    conn.close()
    # 204 = No Content (padrão para deleções bem‑sucedidas)
    return ("", 204)


##ROTA INSERT
#############################################

from flask import request, jsonify, abort
@estudante_bp.route("/estudante", methods=["POST"])
def criar_estudante():
    dados = request.get_json(silent=True)
    if not dados:
        abort(400, description="JSON inválido ou ausente")

    # Validação de campos obrigatórios
    campos_obrigatorios = {"nome", "turma", "matricula", "contato"}
    if not campos_obrigatorios.issubset(dados.keys()):
        abort(400, description=f"Campos obrigatórios: {', '.join(campos_obrigatorios)}")

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO estudante (nome, turma, matricula, contato)"
        "VALUES (%s, %s, %s, %s)",
        (dados["nome"], dados["turma"], dados["matricula"], dados["contato"])
    )
    conn.commit()
    novo_idEstudante = cursor.lastrowid
    conn.close()

    # 201 Created + Location do recurso recém‑criado
    resposta = jsonify({"idEmprestimo": novo_idEstudante, **dados})
    resposta.status_code = 201
    resposta.headers["Location"] = f"/estudante/{novo_idEstudante}"
    return resposta

##ROTA UPDATE
#############################################
@estudante_bp.route("/estudante/<int:idEstudante>", methods=["PUT", "PATCH"])
def atualizar_emprestimo(idEstudante):
    dados = request.get_json(silent=True)
    if not dados:
        abort(400, description="JSON inválido ou ausente")

    # Para PUT, garanta que todos os campos estejam presentes
    if request.method == "PUT":
        campos_esperados = {"nome", "turma", "matricula", "contato"}
        if not campos_esperados.issubset(dados.keys()):
            abort(400, description=f"PUT requer todos os campos: {', '.join(campos_esperados)}")

    # Monta dinamicamente o SQL somente com os campos enviados
    campos_validos = {"nome", "turma", "matricula", "contato"}
    set_clauses = []
    valores = []
    for campo in campos_validos & dados.keys():
        set_clauses.append(f"{campo} = %s")
        valores.append(dados[campo])

    if not set_clauses:
        abort(400, description="Nenhum campo válido para atualizar")

    valores.append(idEstudante)  # último parâmetro é o WHERE

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        f"UPDATE estudante SET {', '.join(set_clauses)} WHERE idEstudante = %s",
        tuple(valores)
    )
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        abort(404, description="Não encontrado")

    conn.close()
    # 204 = No Content, mas você pode devolver 200 com o JSON atualizado se preferir
    return ("", 204)