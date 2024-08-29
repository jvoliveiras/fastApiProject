from utils.cleardb import clear_database
from utils.scrap.populateDatabase import get_and_populate_establishments

update_in_progress = False
async def update_database():
    print('Limpando registros antigos...')
    await clear_database()
    print('Registros antigos removidos com sucesso!')
    print('Populando banco de dados...')
    await get_and_populate_establishments()
    print('Banco de dados populado com dados atualizados com sucesso!')
