import sqlite3

# =========================
# FUNÇÕES PARA LIDAR COM CONEXÃO NA DB
# =========================
def abrir_conexao(caminho_db):
    try:
        conexao = sqlite3.connect(caminho_db)
        # Permite aceder aos dados do select com o nome da coluna ao invés utilizar um índice numérico.
        conexao.row_factory = sqlite3.Row
        # Ativa o funcionamente das FK
        conexao.execute("PRAGMA foreign_keys = ON")
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

# =========================
# FUNÇÕES PARA INSERIR DADOS NAS TABELAS
# =========================
def inserir_binario(caminho, hash, assinatura_digital, status):
    query = f"""
            INSERT OR IGNORE INTO binarios (caminho, hash, assinatura_digital, status)
            VALUES (?, ?, ?, ?)
             """
    conexao = abrir_conexao("base_de_dados/holmes.db")
    if conexao:
        cursor = conexao.cursor()
        try:
            cursor.execute(query, (caminho, hash, assinatura_digital, status))
            conexao.commit()
        except(sqlite3.IntegrityError):
            pass
        fechar_conexao(conexao)

def inserir_processo(pid, ppid, nome, utilizador, pontuacao_risco, nivel_risco, motivo, id_binario):
    query = f""" 
            INSERT OR IGNORE INTO processos (pid, ppid, nome, utilizador, 
            pontuacao_risco, nivel_risco, motivo, id_binario) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?) 
            """
    conexao = abrir_conexao("base_de_dados/holmes.db")
    if conexao:
        cursor = conexao.cursor()
        try:
            cursor.execute(query ,(pid, ppid, nome, utilizador, pontuacao_risco, nivel_risco, motivo, id_binario))
            conexao.commit()
        except(sqlite3.IntegrityError):
            pass
        fechar_conexao(conexao)

def inserir_programas_chave_registo(nome, tipo, HK, pontuacao_risco, nivel_risco, motivo ,id_binario):
    query = f"""
            INSERT OR IGNORE INTO programas_chave_registo (nome, tipo, HK, pontuacao_risco, nivel_risco, motivo, id_binario)
            VALUES (?, ?, ?, ?, ?, ?, ?)
             """
    conexao = abrir_conexao("base_de_dados/holmes.db")
    if conexao:
        cursor = conexao.cursor()
        try:
            cursor.execute(query, (nome, tipo, HK, pontuacao_risco, nivel_risco, motivo, id_binario))
            conexao.commit()
        except(sqlite3.IntegrityError):
            pass
        fechar_conexao(conexao)

def inserir_tarefas_agendadas(nome, proxima_execucao, ultima_execucao, utilizador, pontuacao_risco, nivel_risco, motivo, id_binario):
    query = f"""
            INSERT OR IGNORE INTO tarefas_agendadas (nome, proxima_execucao, ultima_execucao, 
            utilizador, pontuacao_risco, nivel_risco, motivo, id_binario)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
             """
    conexao = abrir_conexao("base_de_dados/holmes.db")
    if conexao:
        cursor = conexao.cursor()
        try:
            cursor.execute(query, (nome, proxima_execucao, ultima_execucao, utilizador, pontuacao_risco, nivel_risco, motivo, id_binario))
            conexao.commit()
        except(sqlite3.IntegrityError):
            pass
        fechar_conexao(conexao)

def inserir_servicos(nome, exibido, estado, pontuacao_risco, nivel_risco, motivo, id_binario):
    query = f"""
            INSERT OR IGNORE INTO servicos (nome, nome_exibido, estado, pontuacao_risco, nivel_risco, motivo, id_binario)
            VALUES (?, ?, ?, ?, ?, ?, ?)
             """
    conexao = abrir_conexao("base_de_dados/holmes.db")
    if conexao:
        cursor = conexao.cursor()
        try:
            cursor.execute(query, (nome, exibido, estado, pontuacao_risco, nivel_risco, motivo, id_binario))
            conexao.commit()
        except(sqlite3.IntegrityError):
            pass
        fechar_conexao(conexao)

def inserir_conexoes_rede(ip_local, porta_local, endereco_remoto, dominio, porta_remota, estado_conexao, pontuacao_risco, nivel_risco, motivo,id_processo):
    query = f"""
            INSERT OR IGNORE INTO conexoes_rede (ip_local, porta_local, endereco_remoto, dominio, porta_remota, estado_conexao, pontuacao_risco,nivel_risco, motivo, id_processo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
    conexao = abrir_conexao("base_de_dados/holmes.db")
    if conexao:
        cursor = conexao.cursor()
        try:
            cursor.execute(query, (ip_local, porta_local, endereco_remoto, dominio, porta_remota, estado_conexao, pontuacao_risco, nivel_risco, motivo, id_processo))
            conexao.commit()
        except(sqlite3.IntegrityError):
            pass
        fechar_conexao(conexao)

# =========================
# FUNÇÕES PARA OBTER ID'S (ESPECÍFICOS)
# =========================
def consultar_binario(caminho, tabela="binarios"):
    query = f"SELECT * FROM {tabela} WHERE caminho = ?"
    conexao = abrir_conexao("base_de_dados/holmes.db")

    if conexao:
        cursor = conexao.cursor()
        cursor.execute(query, (caminho,))
        resultado = cursor.fetchone()
        return resultado

def consultar_processo(pid):
    query = f"SELECT * FROM processos WHERE pid = ?"
    conexao = abrir_conexao("base_de_dados/holmes.db")

    if conexao:
        cursor = conexao.cursor()
        cursor.execute(query, (pid,))
        resultado = cursor.fetchone()
        return resultado

# =========================
# FUNÇÕES PARA OBTER DADOS DAS TABELAS
# =========================
def consultar_processos():
    query = f"""
            SELECT 
            processos.pid,
            processos.ppid,
            processos.nome,
            processos.utilizador,
            processos.pontuacao_risco,
            processos.nivel_risco,
            processos.motivo,
            processos.id_binario,
            processos.data_analise,
        
            binarios.caminho,
            binarios.hash,
            binarios.assinatura_digital,
            binarios.status
        
            FROM processos
            
            INNER JOIN binarios 
            ON processos.id_binario = binarios.id
             """
    conexao = abrir_conexao("base_de_dados/holmes.db")

    if conexao:
        cursor = conexao.cursor()
        cursor.execute(query)
        resultado = cursor.fetchall()
        if (len(resultado) > 0):
            # Imprimir cada linha
            print(f"Dados registados na tabela de processos: ")
            for linha in resultado:
                print("------------------------------------------------------------")
                print(f"PID                    : {linha["pid"]}")
                print(f"PPID                   : {linha["ppid"]}")
                print(f"Nome                   : {linha["nome"]}")
                print(f"Caminho                : {linha["caminho"]}")
                print(f"Utilizador             : {linha["utilizador"]}")
                print(f"Hash                   : {linha["hash"]}")
                print(f"Estado da assinatura   : {linha["status"]}")
                print(f"Pontuação de risco     : {linha["pontuacao_risco"]}")
                print(f"Nível de risco         : {linha["nivel_risco"]}")
                print(f"Motivos                : {linha["motivo"]}")
                print(f"Data de análise        : {linha["data_analise"]} ")
                print("------------------------------------------------------------")
        else:
            print(f"Não existem dados registados na tabela processos")
        # Fechar a conexão
        conexao.close()

def consultar_programas(HK):
    query = f"""
            SELECT 
            programas_chave_registo.nome,
            programas_chave_registo.tipo,
            programas_chave_registo.HK,
            programas_chave_registo.data_analise,
            programas_chave_registo.pontuacao_risco,
            programas_chave_registo.nivel_risco,
            programas_chave_registo.motivo,
            programas_chave_registo.id_binario,
        
            binarios.caminho,
            binarios.hash,
            binarios.assinatura_digital,
            binarios.status

            FROM programas_chave_registo
            
            INNER JOIN binarios 
            ON programas_chave_registo.id_binario = binarios.id
            
            WHERE HK = ?
             """
    conexao = abrir_conexao("base_de_dados/holmes.db")

    if conexao:
        cursor = conexao.cursor()
        cursor.execute(query, (HK,))
        resultado = cursor.fetchall()

        if (len(resultado) > 0):
            print(f"Dados registados na tabela programas chave de registo: ")
            for linha in resultado:
                print("------------------------------------------------------------")
                print(f"Nome                   : {linha["nome"]}")
                print(f"Caminho                : {linha["caminho"]}")
                print(f"Tipo                   : {linha["tipo"]}")
                print(f"Iniciado por           : {linha["HK"]}")
                print(f"Estado da assinatura   : {linha["status"]}")
                print(f"Hash                   : {linha["hash"]}")
                print(f"Pontuação de risco     : {linha["pontuacao_risco"]}")
                print(f"Nível de risco         : {linha["nivel_risco"]}")
                print(f"Motivos                : {linha["motivo"]}")
                print(f"Data de análise        : {linha["data_analise"]} ")
                print("------------------------------------------------------------")
        else:
            print(f"Não existem dados registados na tabela programas chave de registo")
        conexao.close()

def consultar_tarefas_agendadas():
    query = f"""
             SELECT
             tarefas_agendadas.nome,
             tarefas_agendadas.proxima_execucao,
             tarefas_agendadas.ultima_execucao,
             tarefas_agendadas.utilizador,
             tarefas_agendadas.pontuacao_risco,
             tarefas_agendadas.nivel_risco,
             tarefas_agendadas.motivo,
             tarefas_agendadas.data_analise,
             tarefas_agendadas.id_binario,
        
             binarios.id AS binario_id,
             binarios.caminho,
             binarios.hash,
             binarios.assinatura_digital,
             binarios.status
        
             FROM tarefas_agendadas
             INNER JOIN binarios
             ON tarefas_agendadas.id_binario = binarios.id;
             """
    conexao = abrir_conexao("base_de_dados/holmes.db")

    if conexao:
        cursor = conexao.cursor()
        cursor.execute(query)
        resultado = cursor.fetchall()

        if (len(resultado) > 0):
            print(f"Dados registados na tabela de tarefas agendadas: ")
            for linha in resultado:
                print("------------------------------------------------------------")
                print(f"Nome                    : {linha["nome"]}")
                print(f"Próxima Execução        : {linha["proxima_execucao"]}")
                print(f"Última Execução         : {linha["ultima_execucao"]}")
                print(f"Tarefa Executada        : {linha["caminho"]}")
                print(f"Utilizador              : {linha["utilizador"]}")
                print(f"Estado da assinatura    : {linha["assinatura_digital"]}")
                print(f"Hash                    : {linha["hash"]}")
                print(f"Pontuação de risco      : {linha["pontuacao_risco"]}")
                print(f"Nível de risco          : {linha["nivel_risco"]}")
                print(f"Motivos                 : {linha["motivo"]}")
                print(f"Data de análise         : {linha["data_analise"]} ")
                print("------------------------------------------------------------")
        else:
            print(f"Não existem dados registados na tabela de tarefas agendadas")
        conexao.close()

def consultar_servicos():
    query = f"""
            SELECT
            servicos.nome,
            servicos.nome_exibido,
            servicos.estado,
            servicos.pontuacao_risco,
            servicos.nivel_risco,
            servicos.id_binario,
            servicos.motivo,
            servicos.data_analise,
        
            binarios.id AS binario_id,
            binarios.caminho,
            binarios.hash,
            binarios.assinatura_digital,
            binarios.status
        
            FROM servicos
            INNER JOIN binarios
            ON servicos.id_binario = binarios.id;
             """
    conexao = abrir_conexao("base_de_dados/holmes.db")

    if conexao:
        cursor = conexao.cursor()
        cursor.execute(query)
        resultado = cursor.fetchall()
        if (len(resultado) > 0):
            print(f"Dados registados na tabela de serviços: ")
            for linha in resultado:
                print("------------------------------------------------------------")
                print(f"Serviço                : {linha["nome"]}")
                print(f"Nome exibido           : {linha["nome_exibido"]}")
                print(f"Estado do serviço      : {linha["estado"]}")
                print(f"Caminho                : {linha["caminho"]}")
                print(f"Estado da assinatura   : {linha["status"]}")
                print(f"Hash                   : {linha["hash"]}")
                print(f"Pontuação de risco     : {linha["pontuacao_risco"]}")
                print(f"Nível de risco         : {linha["nivel_risco"]}")
                print(f"Motivos                : {linha["motivo"]}")
                print(f"Data de análise        : {linha["data_analise"]} ")
                print("------------------------------------------------------------")
        else:
            print(f"Não existem dados registados na tabela de serviços")
        conexao.close()

def consultar_conexoes_rede():
    query = f"""
            SELECT
            conexoes_rede.ip_local,
            conexoes_rede.porta_local,
            conexoes_rede.endereco_remoto,
            conexoes_rede.dominio,
            conexoes_rede.porta_remota,
            conexoes_rede.estado_conexao,
            conexoes_rede.data_analise,
            conexoes_rede.pontuacao_risco,
            conexoes_rede.nivel_risco,
            conexoes_rede.motivo,
            conexoes_rede.id_processo,
        
            processos.id AS processo_id,
            processos.pid,
            processos.nome,
            processos.id_binario,
        
            binarios.id AS binario_id,
            binarios.caminho,
            binarios.hash,
            binarios.status
        
            FROM conexoes_rede
            
            INNER JOIN processos
            ON conexoes_rede.id_processo = processos.id
            
            INNER JOIN binarios
            ON processos.id_binario = binarios.id;
             """
    conexao = abrir_conexao("base_de_dados/holmes.db")
    if conexao:
        cursor = conexao.cursor()
        cursor.execute(query)
        resultado = cursor.fetchall()

        if (len(resultado) > 0):
            print(f"Dados registados na tabela de conexões de rede: ")
            for linha in resultado:
                print("------------------------------------------------------------")
                print(f"IP Local                 : {linha["ip_local"]}")
                print(f"Porta Local              : {linha["porta_local"]}")
                print(f"Endereço Remoto          : {linha["endereco_remoto"]}")
                print(f"Dominio                  : {linha["dominio"]}")
                print(f"Porta Remota             : {linha["porta_remota"]}")
                print(f"Estado da Conexão        : {linha["estado_conexao"]}")
                print(f"PID do Processo          : {linha["pid"]}")
                print(f"Nome do Processo         : {linha["nome"]}")
                print(f"Caminho do Processo      : {linha["caminho"]}")
                print(f"Assinatura digital       : {linha['status']}")
                print(f"Hash eo executável       : {linha['hash']}")
                print(f"Pontuação de risco       : {linha['pontuacao_risco']}")
                print(f"Nível de risco           : {linha['nivel_risco']}")
                print(f"Motivos                  : {linha['motivo']}")
                print(f"Data e hora da conexão   : {linha["data_analise"]}")
                print("------------------------------------------------------------")
        else:
            print(f"Não existem dados registados na tabela de conexões de rede")
        fechar_conexao(conexao)

def update_processo(pid , utilizador, pontuacao_risco, nivel_risco, motivo):
    query = """
            UPDATE processos
            SET utilizador = ?,
                pontuacao_risco = ?,
                nivel_risco = ?,
                motivo = ?
            WHERE pid = ?
            """

    conexao = abrir_conexao("base_de_dados/holmes.db")

    if conexao:
        cursor = conexao.cursor()
        cursor.execute(query, (utilizador,pontuacao_risco,nivel_risco,motivo,pid))
        conexao.commit()
        fechar_conexao(conexao)

caminho_db = "C:\\Users\\georg\\Holmes\\base_de_dados\\holmes.db"
conexao = abrir_conexao(caminho_db)

if conexao:

    cursor = conexao.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS binarios (id integer PRIMARY KEY, caminho text, "
                   "hash text, assinatura_digital text, status text, UNIQUE(caminho, hash))")

    cursor.execute("CREATE TABLE IF NOT EXISTS programas_startup (id integer PRIMARY KEY, nome text, "
                   "caminho text, data_analise DATETIME DEFAULT CURRENT_TIMESTAMP)")

    cursor.execute("CREATE TABLE IF NOT EXISTS processos (id integer PRIMARY KEY ,id_binario integer, pid integer,"
                   "ppid integer, nome text,"
                   "utilizador text, pontuacao_risco integer, nivel_risco text, motivo text, data_analise DATETIME DEFAULT CURRENT_TIMESTAMP, "
                   "FOREIGN KEY(id_binario) REFERENCES binarios(id), UNIQUE(pid))")

    cursor.execute("CREATE TABLE IF NOT EXISTS programas_chave_registo (id integer PRIMARY KEY, id_binario integer,nome text, tipo integer,"
                   "HK text, pontuacao_risco integer, nivel_risco text, motivo,data_analise DATETIME DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(id_binario) REFERENCES binarios(id), UNIQUE(nome, HK))")

    cursor.execute("CREATE TABLE IF NOT EXISTS tarefas_agendadas (id integer PRIMARY KEY, id_binario integer , nome TEXT, proxima_execucao DATETIME,"
                   "ultima_execucao DATETIME, utilizador TEXT, pontuacao_risco integer, nivel_risco text, motivo text, data_analise DATETIME DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY (id_binario) REFERENCES binarios(id), UNIQUE(nome))")

    cursor.execute("CREATE TABLE IF NOT EXISTS servicos (id integer PRIMARY KEY, id_binario integer,"
                   "nome TEXT, nome_exibido TEXT, estado TEXT, pontuacao_risco integer, nivel_risco text, motivo text, data_analise DATETIME DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(id_binario) REFERENCES binarios(id), UNIQUE(nome))")

    cursor.execute("CREATE TABLE IF NOT EXISTS conexoes_rede (id integer PRIMARY KEY, id_processo integer, ip_local TEXT, porta_local integer, endereco_remoto TEXT,"
                    "dominio TEXT, porta_remota TEXT, estado_conexao TEXT, motivo text, data_analise DATETIME DEFAULT CURRENT_TIMESTAMP,"
                   "pontuacao_risco integer, nivel_risco text,"
                   "FOREIGN KEY(id_processo) REFERENCES processos(id), UNIQUE(id_processo,ip_local,porta_local,endereco_remoto,porta_remota))")

    conexao.commit()
    fechar_conexao(conexao)