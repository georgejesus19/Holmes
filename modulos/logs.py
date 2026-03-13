import sqlite3

def abrir_conexao(caminho_db):
    try:
        conexao = sqlite3.connect(caminho_db)
        return conexao
    except sqlite3.Error as erro:
        print(f"Erro ao realizar conexão: {erro}")
        return None

def fechar_conexao(conexao):
    if conexao:
        try:
            conexao.close()
        except sqlite3.Error as erro:
            print(f"Erro ao fechar a conexão: {erro}")


def inserir_processo(pid, ppid, nome, caminho, utilizador, hash, assinatura, tabela):
    query = f""" 
            INSERT OR IGNORE INTO {tabela} (pid, ppid, nome, caminho, utilizador, hash, assinatura) 
            VALUES (?, ?, ?, ?, ?, ?, ?) 
            """
    conexao = abrir_conexao("base_de_dados/holmes.db")
    if conexao:
        cursor = conexao.cursor()
        cursor.execute(query ,(pid, ppid, nome, caminho, utilizador, hash, assinatura))
        conexao.commit()
        fechar_conexao(conexao)

def inserir_programas_chave_registo(nome, caminho, tipo, HK, assinatura, hash, tabela):
    query = f"""
            INSERT OR IGNORE INTO {tabela} (nome, caminho, tipo, HK, assinatura, hash)
            VALUES (?, ?, ?, ?, ?, ?)
             """
    conexao = abrir_conexao("base_de_dados/holmes.db")
    if conexao:
        cursor = conexao.cursor()
        cursor.execute(query, (nome, caminho, tipo, HK, assinatura, hash))
        conexao.commit()
        fechar_conexao(conexao)

def inserir_tarefas_agendadas(nome, proxima_execucao, ultima_execucao, tarefa_executada, utilizador, assinatura, hash, tabela):
    query = f"""
            INSERT OR IGNORE INTO {tabela} (nome, proxima_execucao, ultima_execucao, tarefa_executada, utilizador, assinatura, hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
             """
    conexao = abrir_conexao("base_de_dados/holmes.db")
    if conexao:
        cursor = conexao.cursor()
        cursor.execute(query, (nome, proxima_execucao, ultima_execucao, tarefa_executada, utilizador, assinatura, hash))
        conexao.commit()
        fechar_conexao(conexao)

def inserir_servicos(nome, exibido, estado, caminho, assinatura, hash, tabela):
    query = f"""
            INSERT OR IGNORE INTO {tabela} (nome, exibido, estado, caminho, assinatura, hash)
            VALUES (?, ?, ?, ?, ?, ?)
             """
    conexao = abrir_conexao("base_de_dados/holmes.db")
    if conexao:
        cursor = conexao.cursor()
        cursor.execute(query, (nome, exibido, estado, caminho, assinatura, hash))
        conexao.commit()
        fechar_conexao(conexao)

def inserir_conexoes_rede(ip_local, porta_local, endereco_remoto, dominio, porta_remota, estado_conexao, pid, nome, assinatura, tabela):
    query = f"""
            INSERT OR IGNORE INTO {tabela} (ip_local, porta_local, endereco_remoto, dominio, porta_remota, estado, pid, nome, assinatura)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
    conexao = abrir_conexao("base_de_dados/holmes.db")
    if conexao:
        cursor = conexao.cursor()
        cursor.execute(query, (ip_local, porta_local, endereco_remoto, dominio, porta_remota, estado_conexao, pid, nome, assinatura))
        conexao.commit()
        fechar_conexao(conexao)

def consultar_processos(tabela):
    query = f"SELECT * FROM {tabela}"
    conexao = abrir_conexao("base_de_dados/holmes.db")

    if conexao:
        cursor = conexao.cursor()
        cursor.execute(query)
        resultados = cursor.fetchall()

        # Imprimir cada linha
        for linha in resultados:
            print("------------------------------------------------------------")
            print(f"PID                    : {linha[0]}")
            print(f"PPID                   : {linha[1]}")
            print(f"Nome                   : {linha[2]}")
            print(f"Caminho                : {linha[3]}")
            print(f"Utilizador             : {linha[4]}")
            print(f"Hahs                   : {linha[5]}")
            print(f"Estado da assinatura   : {linha[6]}")
            print("------------------------------------------------------------")
        # Fechar a conexão
        conexao.close()

def consultar_programas(tabela):
    query = f"SELECT * FROM {tabela}"
    conexao = abrir_conexao("base_de_dados/holmes.db")

    if conexao:
        cursor = conexao.cursor()
        print(query)
        cursor.execute(query)
        resultado = cursor.fetchall()

        for linha in resultado:
            print("------------------------------------------------------------")
            print(f"Nome                   : {linha[0]}")
            print(f"Caminho                : {linha[1]}")
            print(f"Tipo                   : {linha[2]}")
            print(f"Iniciado por           : {linha[3]}")
            print(f"Estado da assinatura   : {linha[4]}")
            print(f"Hash                   : {linha[5]}")
            print("------------------------------------------------------------")
        conexao.close()

def consultar_tarefas_agendadas(tabela):
    query = f"SELECT * FROM {tabela}"
    conexao = abrir_conexao("base_de_dados/holmes.db")

    if conexao:
        cursor = conexao.cursor()
        cursor.execute(query)
        resultado = cursor.fetchall()

        for linha in resultado:
            print("------------------------------------------------------------")
            print(f"Nome                    : {linha[1]}")
            print(f"Próxima Execução        : {linha[2]}")
            print(f"Última Execução         : {linha[3]}")
            print(f"Tarefa Executada        : {linha[4]}")
            print(f"Utilizador              : {linha[5]}")
            print(f"Estado da assinatura    : {linha[7]}")
            print(f"Hash                    : {linha[6]}")
            print("------------------------------------------------------------")
        conexao.close()

def consultar_servicos(tabela):
    query = f"SELECT * FROM {tabela}"
    conexao = abrir_conexao("base_de_dados/holmes.db")

    if conexao:
        cursor = conexao.cursor()
        cursor.execute(query)
        resultado = cursor.fetchall()

        for linha in resultado:
            print("------------------------------------------------------------")
            print(f"Serviço                : {linha[1]}")
            print(f"Nome exibido           : {linha[2]}")
            print(f"Estado do serviço      : {linha[3]}")
            print(f"Caminho                : {linha[4]}")
            print(f"Estado da assinatura   : {linha[5]}")
            print(f"Hash                   : {linha[6]}")
            print("------------------------------------------------------------")
        conexao.close()

def consultar_conexoes_rede(tabela):
    query = f"SELECT * FROM {tabela}"
    conexao = abrir_conexao("base_de_dados/holmes.db")
    if conexao:
        cursor = conexao.cursor()
        cursor.execute(query)
        resultado = cursor.fetchall()

        for linha in resultado:
            print("------------------------------------------------------------")
            print(f"IP Local                 : {linha[1]}")
            print(f"Porta Local              : {linha[2]}")
            print(f"Endereço Remoto          : {linha[3]}")
            print(f"Dominio                  : {linha[4]}")
            print(f"Porta Remota             : {linha[5]}")
            print(f"Estado da Conexão        : {linha[6]}")
            print(f"PID do Processo          : {linha[7]}")
            print(f"Nome do Processo         : {linha[8]}")
            print(f"Data e hora da conexão   : {linha[9]}")
            print("------------------------------------------------------------")
        fechar_conexao(conexao)

caminho_db = "C:\\Users\\georg\\Holmes\\base_de_dados\\holmes.db"
conexao = abrir_conexao(caminho_db)

if conexao:
    cursor = conexao.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS processos (id integer PRIMARY KEY , pid integer,"
                   "ppid integer, nome text,"
                   "caminho text, utilizador text,"
                   "hash text, assinatura text, UNIQUE(caminho, hash))")

    cursor.execute("CREATE TABLE IF NOT EXISTS processos_suspeitos (id integer PRIMARY KEY , pid integer,"
                   "ppid integer, nome text,"
                   "caminho text, utilizador text,"
                   "hash text, assinatura text, UNIQUE(caminho, hash))")

    cursor.execute("CREATE TABLE IF NOT EXISTS programas_HKCU (id integer PRIMARY KEY, nome text, caminho text, tipo integer,"
                   "HK text, assinatura text, hash text, UNIQUE(caminho, hash))")

    cursor.execute("CREATE TABLE IF NOT EXISTS programas_HKLM (id integer PRIMARY KEY, nome text, caminho text, tipo integer,"
                   "HK text, assinatura text, hash text, UNIQUE(caminho, hash))")

    cursor.execute("CREATE TABLE IF NOT EXISTS programas_HKCU_suspeitos (id integer PRIMARY KEY, nome text, caminho text, tipo integer,"
                   "HK text, assinatura text, hash text, UNIQUE(caminho, hash))")

    cursor.execute("CREATE TABLE IF NOT EXISTS programas_HKLM_suspeitos (id integer PRIMARY KEY, nome text, caminho text, tipo integer,"
                   "HK text, assinatura text, hash text, UNIQUE(caminho, hash))")

    cursor.execute("CREATE TABLE IF NOT EXISTS tarefas_agendadas (id integer PRIMARY KEY, nome TEXT, proxima_execucao DATETIME,"
                   "ultima_execucao DATETIME, tarefa_executada TEXT, utilizador TEXT,assinatura TEXT, hash TEXT, UNIQUE(nome, utilizador, tarefa_executada, hash))")

    cursor.execute("CREATE TABLE IF NOT EXISTS tarefas_agendadas_suspeitas (id integer PRIMARY KEY, nome TEXT, proxima_execucao DATETIME,"
                   "ultima_execucao DATETIME, tarefa_executada TEXT, utilizador TEXT,assinatura TEXT, hash TEXT, UNIQUE(nome, utilizador, tarefa_executada, hash))")

    cursor.execute("CREATE TABLE IF NOT EXISTS servicos (id integer PRIMARY KEY, nome TEXT, exibido TEXT, estado TEXT, "
                   "caminho TEXT, assinatura TEXT, hash TEXT, UNIQUE(nome, caminho, exibido, hash))")

    cursor.execute("CREATE TABLE IF NOT EXISTS servicos_suspeitos (id integer PRIMARY KEY, nome TEXT, exibido TEXT, estado TEXT, "
                   "caminho TEXT, assinatura TEXT, hash TEXT, UNIQUE(nome, caminho, exibido, hash))")

    cursor.execute("CREATE TABLE IF NOT EXISTS conexoes_rede (id integer PRIMARY KEY, ip_local TEXT, porta_local integer ,endereco_remoto TEXT,"
                    "dominio TEXT, porta_remota TEXT, estado TEXT, pid integer, nome TEXT, assinatura TEXT, data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,UNIQUE(nome, pid, porta_remota))")

    cursor.execute("CREATE TABLE IF NOT EXISTS conexoes_rede_suspeitas (id integer PRIMARY KEY, ip_local TEXT, porta_local integer ,endereco_remoto TEXT,"
                   "dominio TEXT, porta_remota TEXT, estado TEXT, pid integer, nome TEXT, assinatura TEXT, data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,UNIQUE(nome, pid, porta_remota))")

    conexao.commit()
    fechar_conexao(conexao)