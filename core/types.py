from typing import Dict, List, Set, TypedDict, Optional

# Type definitions
class Mensagem(TypedDict):
    nome: str
    mensagem: str
    timestamp: float
    fotoPerfil: Optional[str]

class Anexo(TypedDict):
    nome: str
    url: str
    tipo: str
    timestamp: float
    fotoPerfil: Optional[str]

class AudioMessage(TypedDict):
    nome: str
    audioUrl: str
    timestamp: float
    fotoPerfil: Optional[str]

class Sala(TypedDict):
    mensagens: List[Dict]
    usuarios: Set[str]
    criada_em: float