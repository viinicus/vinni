from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
import os
app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Necessário para usar flash messages


DB_PATH = os.path.join(os.path.dirname(__file__), 'Sistema.db')
def criar_conexao():
    conexao = sqlite3.connect(DB_PATH)
    conexao.row_factory = sqlite3.Row  # Permite acesso a colunas pelo nome
    return conexao

def criar_tabela(conexao):
    cursor = conexao.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cadastro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            saldo REAL DEFAULT 0.0 
        )
    ''')

    conexao.commit()
def recuperar_saldo(conexao, nome_usuario):
    cursor = conexao.cursor()
    cursor.execute('SELECT saldo FROM cadastro WHERE nome = ?', (nome_usuario,))
    row = cursor.fetchone()
    return row[0] if row else 0.0

def atualizar_saldo(conexao, nome_usuario, novo_saldo):
    cursor = conexao.cursor()
    cursor.execute('UPDATE cadastro SET saldo = ? WHERE nome = ?', (novo_saldo, nome_usuario))
    conexao.commit()

def cadastrar_usuario(conexao, nome, senha):
    cursor = conexao.cursor()
    try:
        cursor.execute('INSERT INTO cadastro (nome, senha, saldo) VALUES (?, ?, ?)', (nome, senha, 0.0))
        conexao.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def logar_usuario(conexao, nome, senha):
    cursor = conexao.cursor()
    cursor.execute('''SELECT * FROM cadastro WHERE nome = ? AND senha = ?''', (nome, senha))
    return cursor.fetchone()

def deletar_usuario(conexao, nome):
    cursor = conexao.cursor()
    cursor.execute('''
        DELETE FROM cadastro WHERE nome = ?''', (nome,)) # deleta usuario
    conexao.commit()  # Confirma a transação
    return cursor.rowcount > 0


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/Teladinheiro', methods=['GET', 'POST'])
def tela2():
    nome_usuario = session.get('usuario_logado')

    if 'usuario_logado' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))

    conexao = criar_conexao()
    saldo = recuperar_saldo(conexao, nome_usuario)
    
    return render_template('Teladinheiro.html', saldo=saldo, nome=nome_usuario)

#TRANSAÇÃO
@app.route('/transacao', methods=['POST'])
def transacao():
    if 'usuario_logado' not in session:
        return jsonify({"mensagem": "Usuário não logado"}), 403

    nome_usuario = session['usuario_logado']
    conexao = criar_conexao()
    saldo = recuperar_saldo(conexao, nome_usuario)
    mensagem = ""

    if 'sacar' in request.form:
        valor_saque = float(request.form['valor'])
        if valor_saque <= saldo:
            saldo -= valor_saque
            mensagem = "Saque realizado com sucesso!"
        else:
            mensagem = "Saldo insuficiente!"
    elif 'depositar' in request.form:
        valor_deposito = float(request.form['valor'])
        saldo += valor_deposito
        mensagem = "Depósito realizado com sucesso!"
    
    atualizar_saldo(conexao, nome_usuario, saldo) 

    return jsonify({"saldo": saldo, "mensagem": mensagem})

# CADASTRO
@app.route('/cadastro', methods=['GET','POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha']
        conexao = criar_conexao()
        criar_tabela(conexao)
        if cadastrar_usuario(conexao, nome, senha):
            flash('Usuário cadastrado com sucesso!', 'success')
            return redirect(url_for('login'))
        else:
            flash('Usuário já cadastrado.', 'Aviso')
    return render_template('cadastro.html')

#LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha']
        conexao = criar_conexao()
        resultado = logar_usuario(conexao, nome, senha)
        if resultado:
            session['usuario_logado'] = nome
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('tela2'))
        else:
            flash('Nome ou senha incorretos.', 'Aviso')
    return render_template('login.html')

@app.route('/logout',methods=['POST'])
def logout():
    session.pop('usuario_logado', None)
    flash('Você foi deslogado com sucesso!', 'Sucesso')
    return redirect(url_for('index'))


@app.route('/deletar', methods=['POST'])
def deletar():
    if 'usuario_logado' not in session:
        flash('Você precisa estar logado para deletar sua conta.', 'warning')
        return redirect(url_for('login'))
    
    nome = session['usuario_logado']
    with criar_conexao() as conexao:
        if deletar_usuario(conexao, nome):
            session.pop('usuario_logado', None)  # Remove o usuário da sessão
            flash('Sua conta foi deletada com sucesso!', 'success')
        else:
            flash('Erro ao deletar conta.', 'danger')
    
    return redirect(url_for('index'))

if __name__ == '_main_':
    conexao = criar_conexao()
    criar_tabela(conexao)
    app.run(debug=True)