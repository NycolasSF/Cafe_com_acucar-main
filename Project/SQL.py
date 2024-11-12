from mysql.connector import connect, Error

# Função para executar uma consulta e garantir que o cursor seja fechado após cada operação
def run_query(host, user, password, db_name, query, fetch_all=True):
    try:
        with connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                if fetch_all:
                    result = cursor.fetchall()  # Obtém todos os resultados, se solicitado
                else:
                    result = None  # Caso a consulta não precise retornar resultados
                connection.commit()  # Confirma as alterações no banco de dados
                return result
    except Error as e:
        print(f"Erro ao executar a consulta: {e}")

# Função para carregar o último jogador e pontos
def load_player_data():
    host = 'localhost'
    user = 'root'
    password = ''
    db_name = 'gamepygame'
    
    query = "SELECT name, points FROM players ORDER BY _id DESC LIMIT 1;"
    result = run_query(host, user, password, db_name, query)
    
    if result:
        return result[0][0], result[0][1]  # Retorna o último jogador e seus pontos
    return "", 0  

# Função para atualizar ou adicionar um jogador no banco de dados
def save_player_data(name, points):
    host = 'localhost'
    user = 'root'
    password = ''
    db_name = 'gamepygame'
    
  
    check_query = f"SELECT _id FROM players WHERE name = '{name}'"
    result = run_query(host, user, password, db_name, check_query)
    
    if result:
        
        update_query = f"UPDATE players SET points = {points} WHERE name = '{name}'"
        run_query(host, user, password, db_name, update_query, fetch_all=False)
        print(f"Atualizado {name} com {points} pontos.")
    else:
        
        insert_query = f"INSERT INTO players (name, points) VALUES ('{name}', {points})"
        run_query(host, user, password, db_name, insert_query, fetch_all=False)
        print(f"Inserido novo jogador: {name} com {points} pontos.")
        
def save_player_score(name, points):
    query = f"UPDATE Players SET points = {points} WHERE name = '{name}';"
    run_query('localhost', 'root', '', 'gamepygame', query)


def load_player_score(player_name):
    """Carrega a pontuação do jogador a partir do banco de dados."""
    try:
        # Conecte-se ao banco de dados
        with connect(
            host='localhost',
            user='root',        # Altere para seu usuário
            password='',         # Altere para sua senha
            database='gamepygame'
        ) as connection:
            # Crie o cursor e execute a consulta
            with connection.cursor() as cursor:
                query = "SELECT points FROM players WHERE name = %s"
                cursor.execute(query, (player_name,))
                result = cursor.fetchone()  # Retorna apenas o primeiro resultado
                
                if result:
                    return result[0]  # Retorna a pontuação do jogador
                else:
                    print(f"Jogador '{player_name}' não encontrado.")
                    return 0  # Retorna 0 se o jogador não foi encontrado
    except Error as e:
        print(f"Erro ao carregar pontuação: {e}")
        return 0

def load_last_player():
    """Carrega o último jogador salvo e sua pontuação."""
    try:
        # Conecta-se ao banco de dados
        with connect(
            host='localhost',
            user='root',        # Substitua pelo seu usuário
            password='',         # Substitua pela sua senha
            database='gamepygame'
        ) as connection:
            # Cria o cursor e executa a consulta para pegar o último jogador
            with connection.cursor() as cursor:
                query = "SELECT name, points FROM players ORDER BY _id DESC LIMIT 1"
                cursor.execute(query)
                result = cursor.fetchone()  # Retorna o último jogador inserido
                
                if result:
                    return result[0], result[1]  # Retorna o nome e os pontos do jogador
                else:
                    print("Nenhum jogador encontrado.")
                    return "", 0  # Retorna valores padrão se não há jogadores
    except Error as e:
        print(f"Erro ao carregar último jogador: {e}")
        return "", 0

# if __name__ == "__main__":
#     print("Resultado de load_player_data():")
#     resultado = load_player_data()
#     print(resultado)  

#     novo_score = 10
#     nome_jogador = "Player One"
#     save_player_data(novo_score, nome_jogador)
    
#     print("\nApós atualização de pontos:")
#     resultado_atualizado = save_player_data()
#     print(resultado_atualizado)  
