# AnnonChat - Chat Anônimo Temporário

AnnonChat é uma aplicação web de chat em tempo real onde todas as mensagens e arquivos são automaticamente apagados após 24 horas. Totalmente anônimo e sem armazenamento permanente de dados.

## ✨ Funcionalidades

- Criação de salas de chat temporárias
- Chat em tempo real com Socket.IO
- Compartilhamento de arquivos (imagens e outros)
- Totalmente anônimo - sem registro necessário
- Auto-destruição após 24 horas
- Interface moderna e responsiva

## 🛠️ Requisitos

- Python 3.8+
- pip
- Node.js (opcional, para desenvolvimento)

## 🚀 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/annonchat.git
cd annonchat
```

2. Crie e ative um ambiente virtual (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## ⚡ Como Usar

1. Inicie o servidor:
```bash
python main.py
```

2. Acesse no navegador:
```
http://localhost:5000
```

3. Na página inicial:
- Clique em "Criar Sala" para criar uma nova sala de chat
- Ou insira um código de sala existente para entrar

4. No chat:
- Digite seu nome (opcional)
- Comece a conversar!

## 🧰 Tecnologias Utilizadas

- **Backend**:
  - Python
  - Flask
  - Flask-SocketIO

- **Frontend**:
  - HTML5
  - Tailwind CSS
  - Socket.IO Client

- **Outras**:
  - JavaScript ES6+
  - Responsive Design

## 📝 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🤝 Contribuição

Contribuições são bem-vindas! Siga estes passos:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📬 Contato

Para dúvidas ou sugestões, entre em contato:

- Email: administracao@dspeed.com.br
- GitHub: [@ferensoviczp](https://github.com/ferensoviczp)
