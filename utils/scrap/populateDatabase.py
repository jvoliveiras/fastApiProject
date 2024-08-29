import requests
import asyncio
from prisma import Prisma
from prisma.engine.errors import AlreadyConnectedError
import os
from tenacity import retry, stop_after_attempt, wait_fixed
prisma = Prisma()

async def insert_data(data):
    await prisma.estabelecimento.create(
        data={
            'codigo_cnes': data['codigo_cnes'],
            'numero_cnpj_entidade': data.get('numero_cnpj_entidade'),
            'nome_razao_social': data['nome_razao_social'],
            'nome_fantasia': data['nome_fantasia'],
            'natureza_organizacao_entidade': data.get('natureza_organizacao_entidade'),
            'tipo_gestao': data['tipo_gestao'],
            'descricao_nivel_hierarquia': data.get('descricao_nivel_hierarquia'),
            'descricao_esfera_administrativa': data['descricao_esfera_administrativa'],
            'codigo_tipo_unidade': data['codigo_tipo_unidade'],
            'codigo_cep_estabelecimento': data['codigo_cep_estabelecimento'],
            'endereco_estabelecimento': data['endereco_estabelecimento'],
            'numero_estabelecimento': data['numero_estabelecimento'],
            'bairro_estabelecimento': data['bairro_estabelecimento'],
            'numero_telefone_estabelecimento': data.get('numero_telefone_estabelecimento', ''),
            'latitude_estabelecimento_decimo_grau': data['latitude_estabelecimento_decimo_grau'],
            'longitude_estabelecimento_decimo_grau': data['longitude_estabelecimento_decimo_grau'],
            'endereco_email_estabelecimento': data.get('endereco_email_estabelecimento', ''),
            'numero_cnpj': data.get('numero_cnpj', ''),
            'codigo_identificador_turno_atendimento': data['codigo_identificador_turno_atendimento'],
            'descricao_turno_atendimento': data['descricao_turno_atendimento'],
            'estabelecimento_faz_atendimento_ambulatorial_sus': data['estabelecimento_faz_atendimento_ambulatorial_sus'],
            'codigo_estabelecimento_saude': data['codigo_estabelecimento_saude'],
            'codigo_uf': data['codigo_uf'],
            'codigo_municipio': data['codigo_municipio'],
            'descricao_natureza_juridica_estabelecimento': data['descricao_natureza_juridica_estabelecimento'],
            'codigo_motivo_desabilitacao_estabelecimento': data.get('codigo_motivo_desabilitacao_estabelecimento'),
            'estabelecimento_possui_centro_cirurgico': data.get('estabelecimento_possui_centro_cirurgico', 0),
            'estabelecimento_possui_centro_obstetrico': data.get('estabelecimento_possui_centro_obstetrico', 0),
            'estabelecimento_possui_centro_neonatal': data.get('estabelecimento_possui_centro_neonatal', 0),
            'estabelecimento_possui_atendimento_hospitalar': data.get('estabelecimento_possui_atendimento_hospitalar', 0),
            'estabelecimento_possui_servico_apoio': data['estabelecimento_possui_servico_apoio'],
            'estabelecimento_possui_atendimento_ambulatorial': data['estabelecimento_possui_atendimento_ambulatorial'],
            'codigo_atividade_ensino_unidade': data['codigo_atividade_ensino_unidade'],
            'codigo_natureza_organizacao_unidade': data.get('codigo_natureza_organizacao_unidade'),
            'codigo_nivel_hierarquia_unidade': data.get('codigo_nivel_hierarquia_unidade'),
            'codigo_esfera_administrativa_unidade': data.get('codigo_esfera_administrativa_unidade'),
        }
    )

def load_codes(file_path):
    codes = {}
    with open(file_path, 'r', encoding='latin-1') as file:
        for line in file:
            if ' - ' in line:
                name, code = line.strip().rsplit(' - ', 1)
                codes[name] = code
    return codes

base_dir = os.path.dirname(os.path.abspath(__file__))
state_codes = load_codes(os.path.join(base_dir, 'codigos_estados.txt'))
unit_types = load_codes(os.path.join(base_dir, 'TiposUnidades.txt'))

headers = {
    'accept': 'application/json',
}

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def fetch_establishments(params, headers):
    response = requests.get('https://apidadosabertos.saude.gov.br/cnes/estabelecimentos', params=params, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()

async def get_and_populate_establishments():
    try:
        await prisma.connect()
    except AlreadyConnectedError:
        await prisma.disconnect()
        await prisma.connect()

    for state, state_code in state_codes.items():
        print('Coletando e populando dados de: ', state)
        for unit, unit_code in unit_types.items():
            params = {
                'codigo_tipo_unidade': unit_code,
                'codigo_uf': state_code,
                'status': '1',
                'limit': '20',
                'offset': '50',
            }

            try:
                response_data = fetch_establishments(params, headers)
                if response_data.get('estabelecimentos'):
                    for estabelecimento in response_data['estabelecimentos']:
                        await insert_data(estabelecimento)
            except requests.exceptions.RequestException as e:
                print(f"Failed to fetch data for state {state} and unit {unit}: {e}")

    await prisma.disconnect()


