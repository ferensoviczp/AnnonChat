"""
AnnonChat - Backend do sistema de chat temporário

Este módulo implementa:
- Criação e gerenciamento de salas de chat
- Comunicação em tempo real via WebSockets
- Limpeza automática de salas expiradas
"""

from flask import Flask, render_template, request
from flask_socketio import SocketIO
from core.rooms import RoomManager

# App configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'  # Em produção, usar variável de ambiente
socketio = SocketIO(app, cors_allowed_origins="*")

roomManager = RoomManager(app, socketio)

@app.route('/', methods=['GET', 'POST'])
def index() -> str:
    return render_template('index.html')

@app.route('/sala/<codigo>')
def sala(codigo: str) -> str:
    if codigo not in roomManager.salas:
        return render_template('sala_inexistente.html'), 404
    
    return render_template(
        'chat.html', 
        codigo = codigo, 
        canDetele = roomManager.salas[codigo]['criador_ip'] == request.remote_addr
    )

# Gerenciamento de Salas.
app.add_url_rule('/criar', 'criar_sala', roomManager.create_room, methods=['POST'])
app.add_url_rule('/entrar', 'entrar_sala', roomManager.join_room, methods=['POST'])
app.add_url_rule('/sala/<codigo>/mensagens', 'obter_mensagens', roomManager.get_messages)
app.add_url_rule('/sala/<codigo>/destruir', 'destruir_sala', roomManager.destroy_room, methods=['POST'])

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 9000))
    socketio.run(app, debug=True, host="0.0.0.0", port=port)
