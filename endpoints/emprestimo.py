from flask import Blueprint, request, jsonify, abort
from conectar.funcaoConectar import conectar

emprestimo_bp = Blueprint("emprestimo", __name__)

##############################################
#ROTAS PARA A TABELA emprestimo

##ROTA GET
##############################################
@emprestimo_bp.route("/emprestimo", methods=["GET"])
def listar_emprestimo():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT idEmprestimo, dataEmprestimo, dataDevolucaoPrevista, dataDevolucaoReal, status FROM emprestimo")
    dados = [
        {"idEmprestimo": row[0], "dataEmprestimo": row[1], "dataDevolucaoPrevista": row[2], "dataDevolucaoReal": row[3], "status": row[4]}
        for row in cursor.fetchall()
    ]
    conn.close()
    return jsonify(dados)

##ROTA DELETE
#############################################
from flask import jsonify, abort

@emprestimo_bp.route("/emprestimo/<int:idEmprestimo>", methods=["DELETE"])
def deletar_emprestimo(idEmprestimo):
    conn = conectar()
    cursor = conn.cursor()

    # tenta apagar o registro informado
    cursor.execute("DELETE FROM emprestimo WHERE idEmprestimo = %s", (idEmprestimo,))
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
@emprestimo_bp.route("/emprestimo", methods=["POST"])
def criar_emprestimo():
    dados = request.get_json(silent=True)
    if not dados:
        abort(400, description="JSON inválido ou ausente")

    # Validação de campos obrigatórios
    campos_obrigatorios = {"dataEmprestimo", "dataDevolucaoPrevista", "dataDevolucaoReal", "status"}
    if not campos_obrigatorios.issubset(dados.keys()):
        abort(400, description=f"Campos obrigatórios: {', '.join(campos_obrigatorios)}")

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO emprestimo (dataEmprestimo, dataDevolucaoPrevista, dataDevolucaoReal, status)"
        "VALUES (%s, %s, %s, %s)",
        (dados["dataEmprestimo"], dados["dataDevolucaoPrevista"], dados["dataDevolucaoReal"], dados["status"])
    )
    conn.commit()
    novo_idEmprestimo = cursor.lastrowid
    conn.close()

    # 201 Created + Location do recurso recém‑criado
    resposta = jsonify({"idEmprestimo": novo_idEmprestimo, **dados})
    resposta.status_code = 201
    resposta.headers["Location"] = f"/emprestimo/{novo_idEmprestimo}"
    return resposta

##ROTA UPDATE
#############################################
@emprestimo_bp.route("/emprestimo/<int:idEmprestimo>", methods=["PUT", "PATCH"])
def atualizar_emprestimo(idEmprestimo):
    dados = request.get_json(silent=True)
    if not dados:
        abort(400, description="JSON inválido ou ausente")

    # Para PUT, garanta que todos os campos estejam presentes
    if request.method == "PUT":
        campos_esperados = {"dataEmprestimo", "dataDevolucaoPrevista", "dataDevolucaoReal", "status"}
        if not campos_esperados.issubset(dados.keys()):
            abort(400, description=f"PUT requer todos os campos: {', '.join(campos_esperados)}")

    # Monta dinamicamente o SQL somente com os campos enviados
    campos_validos = {"dataEmprestimo", "dataDevolucaoPrevista", "dataDevolucaoReal", "status"}
    set_clauses = []
    valores = []
    for campo in campos_validos & dados.keys():
        set_clauses.append(f"{campo} = %s")
        valores.append(dados[campo])

    if not set_clauses:
        abort(400, description="Nenhum campo válido para atualizar")

    valores.append(idEmprestimo)  # último parâmetro é o WHERE

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        f"UPDATE emprestimo SET {', '.join(set_clauses)} WHERE idEmprestimo = %s",
        tuple(valores)
    )
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        abort(404, description="Não encontrado")

    conn.close()
    # 204 = No Content, mas você pode devolver 200 com o JSON atualizado se preferir
    return ("", 204)