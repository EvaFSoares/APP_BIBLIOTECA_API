from flask import Flask
from endpoints.emprestimo import emprestimo_bp
from endpoints.estudante import estudante_bp
#from endpoints.funcionario import funcionario_bp
#from endpoints.livro import livro_bp

app = Flask(__name__)

# Registrar os blueprints
app.register_blueprint(emprestimo_bp)
app.register_blueprint(estudante_bp)
#app.register_blueprint(funcionario_bp)
#app.register_blueprint(livro_bp)

if __name__ == "__main__":
    app.run(debug=True)