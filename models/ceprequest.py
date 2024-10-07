from pydantic import BaseModel

class CepRequest(BaseModel):
    cep: str
    distance: int
    tipo_estabelecimento: str