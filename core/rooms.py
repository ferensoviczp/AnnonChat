from typing import Dict
from .types import Sala, Mensagem, Anexo, AudioMessage
from flask import Flask, url_for, redirect, request, jsonify, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
import time, threading, uuid

class RoomManager:
    
    def __init__(self, app: Flask, socketio: SocketIO):
        
        # State management
        self.app = app
        self.socketio = socketio
        self.salas: Dict[str, Sala] = {}
        
        # Inicia os Sockets.
        self.socketEvents()
        
        # Inicia thread de limpeza
        threading.Thread(target=self.clear_rooms, daemon=True).start()
        
    def socketEvents(self) -> None:
        
        @self.socketio.on('entrar')
        def handle_entrar(data: Dict) -> None:
            """Handler para quando um usuário entra no chat via WebSocket.
            
            Args:
                data: Dados contendo código da sala e nome do usuário
            """
            codigo = data['codigo']
            nome = data['nome'].strip()
            
            join_room(codigo)
            self.salas[codigo]['usuarios'].add(nome)
            
            emit('mensagem_sistema', f"{nome} entrou na sala.", room=codigo)
            emit('mensagens', self.salas[codigo]['mensagens'], to=request.sid)

        @self.socketio.on('sair')
        def handle_sair(data: Dict) -> None:
            """Handler para quando um usuário sai do chat via WebSocket.
            
            Args:
                data: Dados contendo código da sala e nome do usuário
            """
            codigo = data['codigo']
            nome = data['nome'].strip()
            
            leave_room(codigo)
            if nome in self.salas[codigo]['usuarios']:
                self.salas[codigo]['usuarios'].remove(nome)
                emit('mensagem_sistema', f"{nome} saiu da sala.", room=codigo)

        @self.socketio.on('mensagem')
        def handle_mensagem(data: Dict) -> None:
            """Handler para recebimento de mensagens via WebSocket.
            
            Args:
                data: Dados contendo código da sala, mensagem e informações do usuário
            """
            codigo = data['codigo']
            mensagem = data['mensagem'].strip()
            
            print(data.get('fotoPerfil', "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png"))
            
            if mensagem:  # Ignora mensagens vazias
                nova_mensagem: Mensagem = {
                    'nome': data['nome'],
                    'mensagem': mensagem,
                    'timestamp': time.time(),
                    'fotoPerfil': data.get('fotoPerfil', "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png")
                }
                self.salas[codigo]['mensagens'].append(nova_mensagem)
                emit('nova_mensagem', nova_mensagem, room=codigo)

        @self.socketio.on('anexo')
        def handle_anexo(data: Dict) -> None:
            """Handler para recebimento de arquivos anexados via WebSocket.
            
            Args:
                data: Dados contendo código da sala e informações do arquivo
            """
            codigo = data['codigo']
            novo_anexo: Anexo = {
                'nome': data['nome'],
                'url': data['url'],
                'tipo': data['tipo'],
                'timestamp': time.time(),
                'fotoPerfil': data.get('fotoPerfil', '')
            }
            self.salas[codigo]['mensagens'].append(novo_anexo)
            emit('novo_anexo', novo_anexo, room=codigo)

        @self.socketio.on('audio')
        def handle_audio(data: Dict) -> None:
            """Handler para recebimento de mensagens de áudio via WebSocket.
            
            Args:
                data: Dados contendo código da sala e informações do áudio
            """
            codigo = data['codigo']
            novo_audio: AudioMessage = {
                'nome': data['nome'],
                'audioUrl': data['audioUrl'],
                'timestamp': time.time(),
                'fotoPerfil': data.get('fotoPerfil', '')
            }
            self.salas[codigo]['mensagens'].append(novo_audio)
            emit('novo_audio', novo_audio, room=codigo)

        @self.socketio.on('destruir_sala')
        def handle_destruir_sala(data: Dict) -> None:
            """Handler para destruição de sala via WebSocket.
            
            Args:
                data: Dados contendo código da sala
            """
            codigo = data['codigo']
            ip = request.remote_addr
            
            resultado = self.destroy_room(codigo, ip)
            
            print(f"Resultado da destruição da sala {codigo}: {resultado}")

            if resultado[1] == 200:
                # Desconectar todos os usuários da sala
                namespace = '/'  # ou o namespace que você está usando, se for diferente
                sala = codigo

                # Obtem todos os sids conectados à sala
                participantes = list(self.socketio.server.manager.get_participants(namespace, sala))
                print(f"Participantes desconectados: {participantes}")

                for rid, sid in participantes:  # Ignora o nome da sala, usa apenas o sid
                    self.socketio.server.disconnect(sid, namespace=namespace)
                    self.socketio.server.disconnect(rid, namespace=namespace)
                    emit('sala_destruida', {'sucesso': True}, to=sid)

                # Opcional: emitir confirmação ao solicitante (caso ele ainda esteja conectado)
                emit('sala_destruida', {'sucesso': True}, to=request.sid)
            else:
                emit('erro_destruicao', {'erro': resultado[0]}, to=request.sid)


    def create_room(self) -> str:
        """Cria uma nova sala de chat com código único.
        
        Returns:
            str: Redirecionamento para a sala criada
        """
        codigo = str(uuid.uuid4())[:6].upper()
        self.salas[codigo] = {
            'mensagens': [],
            'usuarios': set(),
            'criada_em': time.time(),
            'criador_ip': request.remote_addr
        }
        return redirect(url_for('sala', codigo=codigo))
       
    def join_room(self) -> str:
        """Entra em uma sala existente.
        
        Returns:
            str: Redirecionamento para a sala ou mensagem de erro
        """
        codigo = request.form['codigo'].strip().upper()
        if codigo in self.salas:
            return redirect(url_for('sala', codigo=codigo))
        return render_template('sala_inexistente.html'), 404
        
    def get_messages(self, codigo: str) -> str:
        """Retorna as mensagens de uma sala em formato JSON.
        
        Args:
            codigo: Código da sala
            
        Returns:
            str: Mensagens em formato JSON ou lista vazia
        """
        if codigo not in self.salas:
            return jsonify([])
        
        # Format messages for response
        formatted_messages = []
        for msg in self.salas[codigo]['mensagens']:
            if 'audioUrl' in msg:
                formatted_messages.append({
                    'nome': msg['nome'],
                    'audioUrl': msg['audioUrl'],
                    'timestamp': msg['timestamp'],
                    'fotoPerfil': msg.get('fotoPerfil', '')
                })
            elif 'url' in msg:
                formatted_messages.append({
                    'nome': msg['nome'],
                    'url': msg['url'],
                    'tipo': msg['tipo'],
                    'timestamp': msg['timestamp'],
                    'fotoPerfil': msg.get('fotoPerfil', '')
                })
            else:
                formatted_messages.append({
                    'nome': msg['nome'],
                    'mensagem': msg['mensagem'],
                    'timestamp': msg['timestamp'],
                    'fotoPerfil': msg.get('fotoPerfil', '')
                })
        
        return jsonify(formatted_messages)
        
    def clear_rooms(self) -> None:
        """Remove salas que passaram do tempo de expiração (24 horas)."""
        while True:
            agora = time.time()
            expiradas = [
                codigo for codigo, sala in self.salas.items() 
                if agora - sala['criada_em'] > 86400  # 24 horas
            ]
            for codigo in expiradas:
                del self.salas[codigo]
            time.sleep(3600)  # Verifica a cada hora
            
    def destroy_room(self, codigo: str, ip: str) -> str:
        if codigo not in self.salas:
            return "Sala não encontrada", 404

        if ip != self.salas[codigo]['criador_ip']:
            return "Apenas o criador pode destruir a sala", 403

        emit('mensagem_sistema', "A sala foi destruída pelo criador.", room=codigo)
        emit('sala_destruida', room=codigo)
        
        del self.salas[codigo]
        return "Sala destruída com sucesso", 200
            
    