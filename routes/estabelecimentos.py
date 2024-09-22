from fastapi import APIRouter, Request, HTTPException
from prisma import Prisma
from prisma.errors import PrismaError
from typing import Dict, Any, List
from models.ceprequest import CepRequest
from utils.local import find_ceps_within_distance

router = APIRouter(prefix='/establishments')

prisma = Prisma()

@router.post('/get_establishments')
async def get_establishments(request: Request):
    search_params: Dict[str, Any] = await request.json()

    if 'codigo_tipo_unidade' not in search_params or 'codigo_uf' not in search_params:
        raise HTTPException(status_code=400, detail="Parametros 'codigo_tipo_unidade' e 'codigo_uf' são obrigatórios")

    try:
        codigo_tipo_unidade = int(search_params['codigo_tipo_unidade'])
        codigo_uf = int(search_params['codigo_uf'])

    except ValueError:
        raise HTTPException(status_code=400, detail="Parametros 'codigo_tipo_unidade' e 'codigo_uf' devem ser números inteiros")

    try:
        await prisma.connect()

        estabelecimentos = await prisma.estabelecimento.find_many(
            where={
                'codigo_tipo_unidade': codigo_tipo_unidade,
                'codigo_uf': codigo_uf
            }
        )

        if not estabelecimentos:
            raise HTTPException(status_code=404, detail="Nenhum estabelecimento encontrado")

        resultado: List[Dict[str, Any]] = []
        for estabelecimento in estabelecimentos:
            resultado.append({
                'nome_razao_social': estabelecimento.nome_razao_social,
                'nome_fantasia': estabelecimento.nome_fantasia,
                'codigo_cep_estabelecimento': estabelecimento.codigo_cep_estabelecimento,
                'endereco_estabelecimento': estabelecimento.endereco_estabelecimento,
                'numero_estabelecimento': estabelecimento.numero_estabelecimento,
                'bairro_estabelecimento': estabelecimento.bairro_estabelecimento,
                'numero_telefone_estabelecimento': estabelecimento.numero_telefone_estabelecimento,
                'descricao_turno_atendimento': estabelecimento.descricao_turno_atendimento,
                'estabelecimento_faz_atendimento_ambulatorial_sus': estabelecimento.estabelecimento_faz_atendimento_ambulatorial_sus,
            })

        return resultado

    except PrismaError as e:
        raise HTTPException(status_code=500, detail=f"Erro de banco de dados: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")

    finally:
        await prisma.disconnect()

@router.post("/new_get_establishments")
async def new_get_establishments(request:Request):
    search_params: Dict[str, Any] = await request.json();
    pass

@router.post('/search_by_cep')
async def search_by_cep(cep_request: CepRequest):
    try:
        api_key = "f3853bcd03d04d3cbd13ef68ef5f14ee"
        max_distance_km = cep_request.distance
        reference_cep = cep_request.cep

        ceps_proximos = find_ceps_within_distance(reference_cep, api_key, max_distance_km)

        if not ceps_proximos:
            raise HTTPException(status_code=404, detail="Nenhum CEP encontrado dentro da distância especificada.")

        await prisma.connect()

        estabelecimentos = await prisma.estabelecimento.find_many(
            where={
                'codigo_cep_estabelecimento': {
                    'in': ceps_proximos
                }
            }
        )

        if not estabelecimentos:
            raise HTTPException(status_code=404, detail="Nenhum estabelecimento encontrado para os CEPs próximos.")

        resultado: List[Dict[str, Any]] = []
        for estabelecimento in estabelecimentos:
            resultado.append({
                'nome_razao_social': estabelecimento.nome_razao_social,
                'nome_fantasia': estabelecimento.nome_fantasia,
                'codigo_cep_estabelecimento': estabelecimento.codigo_cep_estabelecimento,
                'endereco_estabelecimento': estabelecimento.endereco_estabelecimento,
                'numero_estabelecimento': estabelecimento.numero_estabelecimento,
                'bairro_estabelecimento': estabelecimento.bairro_estabelecimento,
                'numero_telefone_estabelecimento': estabelecimento.numero_telefone_estabelecimento,
                'descricao_turno_atendimento': estabelecimento.descricao_turno_atendimento,
                'estabelecimento_faz_atendimento_ambulatorial_sus': estabelecimento.estabelecimento_faz_atendimento_ambulatorial_sus,
            })

        return resultado

    except PrismaError as e:
        raise HTTPException(status_code=500, detail=f"Erro de banco de dados: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")

    finally:
        await prisma.disconnect()