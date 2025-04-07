from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import uuid
import time
import threading

app = Flask(__name__)
socketio = SocketIO(app)

salas = {}

# Limpeza automática após 24 horas
def limpeza_salas():
    while True:
        agora = time.time()
        expiradas = [codigo for codigo, sala in salas.items() if agora - sala['criada_em'] > 86400]
        for codigo in expiradas:
            del salas[codigo]
        time.sleep(3600)  # Verifica a cada hora

threading.Thread(target=limpeza_salas, daemon=True).start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/criar', methods=['POST'])
def criar():
    codigo = str(uuid.uuid4())[:6].upper()
    salas[codigo] = {'mensagens': [], 'usuarios': set(), 'criada_em': time.time()}
    return redirect(url_for('sala', codigo=codigo))

@app.route('/entrar', methods=['POST'])
def entrar():
    codigo = request.form['codigo'].strip().upper()
    if codigo in salas:
        return redirect(url_for('sala', codigo=codigo))
    return "Sala inexistente", 404

@app.route('/sala/<codigo>')
def sala(codigo):
    if codigo not in salas:
        return "Sala não encontrada", 404
    return render_template('chat.html', codigo=codigo)

@app.route('/sala/<codigo>/mensagens')
def mensagens(codigo):
    if codigo not in salas:
        return jsonify([])
    return jsonify(salas[codigo]['mensagens'])

@socketio.on('entrar')
def handle_entrar(data):
    join_room(data['codigo'])
    salas[data['codigo']]['usuarios'].add(data['nome'])
    emit('mensagem_sistema', f"{data['nome']} entrou na sala.", room=data['codigo'])
    emit('mensagens', salas[data['codigo']]['mensagens'], to=request.sid)

@socketio.on('sair')
def handle_sair(data):
    leave_room(data['codigo'])
    if data['nome'] in salas[data['codigo']]['usuarios']:
        salas[data['codigo']]['usuarios'].remove(data['nome'])
        emit('mensagem_sistema', f"{data['nome']} saiu da sala.", room=data['codigo'])

@socketio.on('mensagem')
def handle_mensagem(data):
    codigo = data['codigo']
    mensagem = {
        'nome': data['nome'],
        'mensagem': data['mensagem'],
        'timestamp': time.time(),
        'fotoPerfil': data.get('fotoPerfil', '')
    }
    salas[codigo]['mensagens'].append(mensagem)
    emit('nova_mensagem', mensagem, to=codigo)


@socketio.on('anexo')
def handle_anexo(data):
    codigo = data['codigo']
    anexo = {
        'nome': data['nome'],
        'url': data['url'],
        'tipo': data['tipo'],
        'timestamp': time.time(),
        'fotoPerfil': data.get('fotoPerfil', '')
    }
    salas[codigo]['mensagens'].append(anexo)
    emit('novo_anexo', anexo, to=codigo)


if __name__ == '__main__':
    socketio.run(app, debug=True)