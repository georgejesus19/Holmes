import os
import sqlite3
from CLI import cores

# =========================
# FUNÇÕES PARA LIDAR COM CONEXÃO NA DB
# =========================
def abrir_conexao(caminho_db):
    try:
        conexao = sqlite3.connect(caminho_db)
        conexao.row_factory = sqlite3.Row
        conexao.execute("PRAGMA foreign_keys = ON")
        return conexao
    except Exception:
        return None

def fechar_conexao(conexao):
    if conexao:
        try:
            conexao.close()
        except Exception:
            pass

# =========================
# FUNÇÕES PARA INSERIR DADOS NAS TABELAS
# =========================
def inserir_binario(caminho, hash, assinatura_digital, status):
    query = f"""
            INSERT OR IGNORE INTO binarios (caminho, hash, assinatura_digital, status)
            VALUES (?, ?, ?, ?)
             """
    conexao = abrir_conexao("base_de_dados/holmes.db")
    if not conexao:
        return
    try:
        cursor = conexao.cursor()
        cursor.execute(query, (caminho, hash, assinatura_digital, status))
        conexao.commit()
    except(sqlite3.Error):
        print(f"{cores.CORES['vermelho']}[AVISO] Falha ao inserir registo na base de dados.{cores.CORES['limpo']}")
        pass
    finally:
        fechar_conexao(conexao)

def inserir_log(tipo, modulo, alvo_nome, alvo_caminho, data):
    query = f"""
            INSERT OR IGNORE INTO logs (tipo, modulo, alvo_nome, alvo_caminho, data_acao) VALUES ( ?, ?, ?, ?, ?)
             """
    conexao = abrir_conexao("base_de_dados/holmes.db")

    if not conexao:
        print(f"{cores.CORES['vermelho']}[AVISO] Falha ao registar log (Base de dados indisponível).{cores.CORES['limpo']}")
        return
    try:
        cursor = conexao.cursor()
        cursor.execute(query, (tipo, modulo, alvo_nome, alvo_caminho, data))
        conexao.commit()
    except (sqlite3.Error) :
        print(f"{cores.CORES['vermelho']}[AVISO] Falha ao inserir registo na base de dados.{cores.CORES['limpo']}")
        pass
    finally:
        fechar_conexao(conexao)


def inserir_log_erro(tipo, modulo, data, mensagem):
    query = f"""
            INSERT OR IGNORE INTO logs (tipo, modulo, data_acao, mensagem) VALUES (?, ?, ?, ?)
             """
    conexao = abrir_conexao("base_de_dados/holmes.db")

    if not conexao:
        return
    try:
        cursor = conexao.cursor()
        cursor.execute(query, (tipo, modulo, data, mensagem))
        conexao.commit()
    except Exception:
        print(f"{cores.CORES['vermelho']}[AVISO] Falha ao inserir registo na base de dados.{cores.CORES['limpo']}")
        pass
    finally:
        fechar_conexao(conexao)

def inserir_processo(pid, ppid, nome, utilizador, pontuacao_risco, nivel_risco, motivo, id_binario):
    query = f""" 
            INSERT OR IGNORE INTO processos (pid, ppid, nome, utilizador, 
            pontuacao_risco, nivel_risco, motivo, id_binario) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?) 
            """
    conexao = abrir_conexao("base_de_dados/holmes.db")

    if not conexao:
        return
    try:
        cursor = conexao.cursor()
        cursor.execute(query, (pid, ppid, nome, utilizador, pontuacao_risco, nivel_risco, motivo, id_binario))
        conexao.commit()
    except(sqlite3.Error):
        print(f"{cores.CORES['vermelho']}[AVISO] Falha ao inserir registo na base de dados.{cores.CORES['limpo']}")
        pass
    finally:
        fechar_conexao(conexao)

def inserir_programas_chave_registo(nome, tipo, HK, pontuacao_risco, nivel_risco, motivo, id_binario):
    query = f"""
            INSERT OR IGNORE INTO programas_chave_registo (nome, tipo, HK, pontuacao_risco, nivel_risco, motivo, id_binario)
            VALUES (?, ?, ?, ?, ?, ?, ?)
             """
    conexao = abrir_conexao("base_de_dados/holmes.db")

    if not conexao:
        return
    try:
        cursor = conexao.cursor()
        cursor.execute(query, (nome, tipo, HK, pontuacao_risco, nivel_risco, motivo, id_binario))
        conexao.commit()
    except(sqlite3.Error):
        print(f"{cores.CORES['vermelho']}[AVISO] Falha ao inserir registo na base de dados.{cores.CORES['limpo']}")
        pass
    finally:
        fechar_conexao(conexao)

def inserir_tarefas_agendadas(nome, proxima_execucao, ultima_execucao, utilizador, pontuacao_risco, nivel_risco, motivo,
                              id_binario):
    query = f"""
            INSERT OR IGNORE INTO tarefas_agendadas (nome, proxima_execucao, ultima_execucao, 
            utilizador, pontuacao_risco, nivel_risco, motivo, id_binario)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
             """
    conexao = abrir_conexao("base_de_dados/holmes.db")

    if not conexao:
        return
    try:
        cursor = conexao.cursor()
        cursor.execute(query,(nome, proxima_execucao, ultima_execucao, utilizador, pontuacao_risco, nivel_risco, motivo,id_binario))
        conexao.commit()
    except(sqlite3.Error):
        print(f"{cores.CORES['vermelho']}[AVISO] Falha ao inserir registo na base de dados.{cores.CORES['limpo']}")
        pass
    finally:
        fechar_conexao(conexao)

def inserir_servicos(nome, exibido, estado, pontuacao_risco, nivel_risco, motivo, id_binario):
    query = f"""
            INSERT OR IGNORE INTO servicos (nome, nome_exibido, estado, pontuacao_risco, nivel_risco, motivo, id_binario)
            VALUES (?, ?, ?, ?, ?, ?, ?)
             """
    conexao = abrir_conexao("base_de_dados/holmes.db")

    if not conexao:
        return
    try:
        cursor = conexao.cursor()
        cursor.execute(query, (nome, exibido, estado, pontuacao_risco, nivel_risco, motivo, id_binario))
        conexao.commit()
    except(sqlite3.Error):
        print(f"{cores.CORES['vermelho']}[AVISO] Falha ao inserir registo na base de dados.{cores.CORES['limpo']}")
        pass
    finally:
        fechar_conexao(conexao)


def inserir_conexoes_rede(ip_local, porta_local, endereco_remoto, dominio, porta_remota, estado_conexao,
                          pontuacao_risco, nivel_risco, motivo, id_processo):
    query = f"""
            INSERT OR IGNORE INTO conexoes_rede (ip_local, porta_local, endereco_remoto, dominio, porta_remota, estado_conexao, pontuacao_risco,nivel_risco, motivo, id_processo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
    conexao = abrir_conexao("base_de_dados/holmes.db")
    if not conexao:
        return
    try:
        cursor = conexao.cursor()
        cursor.execute(query, (ip_local, porta_local, endereco_remoto, dominio, porta_remota, estado_conexao,pontuacao_risco, nivel_risco, motivo, id_processo))
        conexao.commit()
    except(sqlite3.Error):
        print(f"{cores.CORES['vermelho']}[AVISO] Falha ao inserir registo na base de dados.{cores.CORES['limpo']}")
        pass
    finally:
        fechar_conexao(conexao)

def inserir_programas_startup(nome, caminho):
    query = f"""
            INSERT OR IGNORE INTO programas_startup (nome, caminho) VALUES (?, ?)
             """
    conexao = abrir_conexao("base_de_dados/holmes.db")

    if not conexao:
        return
    try:
        cursor = conexao.cursor()
        cursor.execute(query, (nome, caminho))
        conexao.commit()
    except(sqlite3.Error):
        print(f"{cores.CORES['vermelho']}[AVISO] Falha ao inserir registo na base de dados.{cores.CORES['limpo']}")
        pass
    finally:
        fechar_conexao(conexao)

# =========================
# FUNÇÕES PARA OBTER ID'S (ESPECÍFICOS)
# =========================
def consultar_binario(caminho, tabela="binarios"):
    query = f"SELECT * FROM {tabela} WHERE caminho = ?"
    conexao = abrir_conexao("base_de_dados/holmes.db")

    if not conexao:
        return None

    try:
        cursor = conexao.cursor()
        cursor.execute(query, (caminho,))
        resultado = cursor.fetchone()
        return resultado
    except sqlite3.Error:
        print(f"{cores.CORES['vermelho']}[AVISO] Falha ao consultar registo na base de dados.{cores.CORES['limpo']}")
        return None


def consultar_processo(pid):
    query = f"SELECT * FROM processos WHERE pid = ?"
    conexao = abrir_conexao("base_de_dados/holmes.db")

    if not conexao:
        return None
    try:
        cursor = conexao.cursor()
        cursor.execute(query, (pid,))
        resultado = cursor.fetchone()
        return resultado
    except sqlite3.Error:
        print(f"{cores.CORES['vermelho']}[AVISO] Falha ao consultar registo na base de dados.{cores.CORES['limpo']}")
        return None
    finally:
        fechar_conexao(conexao)

# =========================
# FUNÇÕES PARA OBTER DADOS DAS TABELAS
# =========================
def consultar_logs_acoes():
    query = """
    SELECT * FROM logs
    WHERE tipo = ?
    """

    conexao = abrir_conexao("base_de_dados/holmes.db")

    if not conexao:
        return
    try:
        cursor = conexao.cursor()
        cursor.execute(query, ("ação",))

        resultado = cursor.fetchall()

        if len(resultado) > 0:
            print("Logs registados:")
            for linha in resultado:
                print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print(f"{cores.CORES['azul']}Módulo responsável     :{cores.CORES['limpo']} {linha['modulo']}")
                print(f"{cores.CORES['azul']}Nome do alvo           :{cores.CORES['limpo']} {linha['alvo_nome']}")
                print(f"{cores.CORES['azul']}Caminho                :{cores.CORES['limpo']} {linha['alvo_caminho']}")
                print(f"{cores.CORES['azul']}Data de execução       :{cores.CORES['limpo']} {linha['data_acao']}")
                print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print("\n")
        else:
            print("Não existem logs registados na tabela")
    except sqlite3.Error:
        print(f"{cores.CORES['vermelho']}[AVISO] Falha ao consultar registos na base de dados.{cores.CORES['limpo']}")
    finally:
        fechar_conexao(conexao)

def consultar_logs_erro():
    query = """
            SELECT * FROM logs
            WHERE tipo = ?
            """

    conexao = abrir_conexao("base_de_dados/holmes.db")

    if not conexao:
        return
    try:
        cursor = conexao.cursor()
        cursor.execute(query, ("erro",))

        resultado = cursor.fetchall()

        if (len(resultado) > 0):
            print("Logs registados (erro) :")
            for linha in resultado:
                print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print(f"{cores.CORES['azul']}Módulo responsável     :{cores.CORES['limpo']} {linha['modulo']}")
                print(f"{cores.CORES['azul']}Data de execução       :{cores.CORES['limpo']} {linha['data_acao']}")
                print(f"{cores.CORES['vermelho']}Erro                   :{cores.CORES['limpo']} {linha['mensagem']}")
                print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print("\n")
        else:
            print("Não existem logs de erros registados")
    except sqlite3.Error:
        print(f"{cores.CORES['vermelho']}[AVISO] Falha ao consultar registos na base de dados.{cores.CORES['limpo']}")
    finally:
        fechar_conexao(conexao)

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

    if not conexao:
        return
    try:
        cursor = conexao.cursor()
        cursor.execute(query)
        resultado = cursor.fetchall()
        if (len(resultado) > 0):
            # Imprimir cada linha
            print(f"Dados registados na tabela de processos: \n")
            for linha in resultado:
                print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print(f"{cores.CORES['azul']}Identificação:{cores.CORES['limpo']}\n")
                print(f"PID                  : {linha['pid']}")
                print(f"PPID                 : {linha['ppid']}")
                print(f"Nome                 : {linha['nome']}")
                print(f"Utilizador           : {linha['utilizador']}\n")
                print(f"{cores.CORES['amarelo']}Executável:{cores.CORES['limpo']}\n")
                print(f"Caminho              : {linha['caminho']}")
                print(f"Hash                 : {linha['hash']}")
                print(f"Estado da assinatura : {linha['status']}\n")
                print(f"{cores.CORES['verde']}Avaliação:{cores.CORES['limpo']}\n")
                print(f"Pontuação de risco   : {linha['pontuacao_risco']}")
                print(f"Nível de risco       : {linha['nivel_risco']}")
                print(f"Motivos              : {linha["motivo"]}")
                print(f"Data de análise      : {linha["data_analise"]} ")
                print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print("\n")
        else:
            print(f"Não existem dados registados na tabela processos")
    except sqlite3.Error:
        print(f"{cores.CORES['vermelho']}[AVISO] Falha ao consultar registos na base de dados.{cores.CORES['limpo']}")
    finally:
        fechar_conexao(conexao)

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

    if not conexao:
        return
    try:
        cursor = conexao.cursor()
        cursor.execute(query, (HK,))
        resultado = cursor.fetchall()

        if (len(resultado) > 0):
            print(f"Dados registados na tabela programas chave de registo: \n")
            for linha in resultado:
                print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print(f"{cores.CORES['azul']}Identificação:{cores.CORES['limpo']}\n")
                print(f"Nome                     : {linha['nome']}")
                print(f"Tipo                     : {linha['tipo']}")
                print(f"Iniciado por (HIKE_KEY)  : {linha['HK']}\n")
                print(f"{cores.CORES['amarelo']}Executável:{cores.CORES['limpo']}\n")
                print(f"Caminho                  : {linha['caminho']}")
                print(f"Estado da assinatura     : {linha['status']}")
                print(f"Hash                     : {linha['hash']}\n")
                print(f"{cores.CORES['verde']}Avaliação:{cores.CORES['limpo']}\n")
                print(f"Pontuação de risco       : {linha['pontuacao_risco']}")
                print(f"Nível de risco           : {linha['nivel_risco']}")
                print(f"Motivos                  : {linha["motivo"]}")
                print(f"Data de análise          : {linha["data_analise"]} ")
                print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print("\n")
        else:
            print(f"Não existem dados registados na tabela programas chave de registo")
    except sqlite3.Error:
        print(f"{cores.CORES['vermelho']}[AVISO] Falha ao consultar registos na base de dados.{cores.CORES['limpo']}")
    finally:
        fechar_conexao(conexao)

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

    if not conexao:
        return
    try:
        cursor = conexao.cursor()
        cursor.execute(query)
        resultado = cursor.fetchall()

        if (len(resultado) > 0):
            print(f"Dados registados na tabela de tarefas agendadas: \n")
            for linha in resultado:
                print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print(f"{cores.CORES['azul']}Identificação:{cores.CORES['limpo']}\n")
                print(f"Nome                    : {linha['nome']}")
                print(f"Utilizador              : {linha['utilizador']}\n")
                print(f"{cores.CORES['amarelo']}Executável:{cores.CORES['limpo']}\n")
                print(f"Tarefa Executada        : {linha['caminho']}")
                print(f"Próxima Execução        : {linha['proxima_execucao']}")
                print(f"Última Execução         : {linha['ultima_execucao']}")
                print(f"Estado da assinatura    : {linha['assinatura_digital']}")
                print(f"Hash                    : {linha['hash']}\n")
                print(f"{cores.CORES['verde']}Avaliação:{cores.CORES['limpo']}\n")
                print(f"Pontuação de risco      : {linha['pontuacao_risco']}")
                print(f"Nível de risco:         : {linha['nivel_risco']}")
                print(f"Motivos                 : {linha["motivo"]}")
                print(f"Data de análise         : {linha["data_analise"]} ")
                print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        else:
            print(f"Não existem dados registados na tabela de tarefas agendadas")
    except sqlite3.Error:
        print(f"{cores.CORES['vermelho']}[AVISO] Falha ao consultar registos na base de dados.{cores.CORES['limpo']}")
    finally:
        fechar_conexao(conexao)

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

    if not conexao:
        return
    try:
        cursor = conexao.cursor()
        cursor.execute(query)
        resultado = cursor.fetchall()
        if (len(resultado) > 0):
            print(f"Dados registados na tabela de serviços: \n")
            for linha in resultado:
                print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print(f"{cores.CORES['azul']}Identificação:{cores.CORES['limpo']}\n")
                print(f"Serviço                : {linha['nome']}")
                print(f"Nome exibido           : {linha['nome_exibido']}")
                print(f"Estado do serviço      : {linha['estado']}\n")
                print(f"{cores.CORES['amarelo']}Executável:{cores.CORES['limpo']}\n")
                print(f"Caminho                : {linha['caminho']}")
                print(f"Estado da assinatura   : {linha['status']}")
                print(f"Hash                   : {linha['hash']}\n")
                print(f"{cores.CORES['verde']}Avaliação:{cores.CORES['limpo']}\n")
                print(f"Pontuação de risco     : {linha['pontuacao_risco']}")
                print(f"Nível de risco         : {linha['nivel_risco']}")
                print(f"Motivos                : {linha["motivo"]}")
                print(f"Data de análise        : {linha["data_analise"]} ")
                print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print("\n")
        else:
            print(f"Não existem dados registados na tabela de serviços")
    except sqlite3.Error:
        print(f"{cores.CORES['vermelho']}[AVISO] Falha ao consultar registos na base de dados.{cores.CORES['limpo']}")
    finally:
        fechar_conexao(conexao)

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
    if not conexao:
        return
    try:
        cursor = conexao.cursor()
        cursor.execute(query)
        resultado = cursor.fetchall()

        if (len(resultado) > 0):
            print(f"Dados registados na tabela de conexões de rede: \n")
            for linha in resultado:
                print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print(f"{cores.CORES['azul']}Identificação:{cores.CORES['limpo']}\n")
                print(f"PID do Processo         : {linha['pid']}")
                print(f"Nome do Processo        : {linha['nome']}\n")
                print(f"{cores.CORES['amarelo']}Executável:{cores.CORES['limpo']}\n")
                print(f"Caminho processo        : {linha['caminho']}")
                print(f"Assinatura digital      : {linha['status']}")
                print(f"Hash do executável      : {linha['hash']}\n")
                print(f"{cores.CORES['roxo']}Conexão:{cores.CORES['limpo']}\n")
                print(f"IP Local                : {linha['ip_local']}")
                print(f"Porta Local             : {linha['porta_local']}")
                print(f"Endereço Remoto         : {linha['endereco_remoto']}\n")
                print(f"Porta Remota            : {linha['porta_remota']}")
                print(f"Estado da Conexão       : {linha['estado_conexao']}\n")
                print(f"{cores.CORES['cyan']}Destino:{cores.CORES['limpo']}\n")
                print(f"Dominio                 : {linha['dominio']}\n")
                print(f"{cores.CORES['verde']}Avaliação:{cores.CORES['limpo']}\n")
                print(f"Pontuação de risco      : {linha['pontuacao_risco']}")
                print(f"Nível de risco          : {linha['nivel_risco']}")
                print(f"Motivos                 : {linha['motivo']}")
                print(f"Data e hora da conexão  : {linha["data_analise"]}")
                print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print("\n")
        else:
            print(f"Não existem dados registados na tabela de conexões de rede")
    except sqlite3.Error:
        print(f"{cores.CORES['vermelho']}[AVISO] Falha ao consultar registos na base de dados.{cores.CORES['limpo']}")
    finally:
        fechar_conexao(conexao)

def consultar_pasta_startup():
    query = "SELECT * FROM programas_startup"

    conexao = abrir_conexao("base_de_dados/holmes.db")
    if not conexao:
        return None
    try:
        cursor = conexao.cursor()
        cursor.execute(query)
        resultado = cursor.fetchall()
        return resultado
    except sqlite3.Error:
        return None
    finally:
        fechar_conexao(conexao)

# =========================
# FUNÇÕES PARA ATUALIZAR DADOS DAS TABELAS
# =========================
def update_processo(pid, utilizador, pontuacao_risco, nivel_risco, motivo):
    query = """
            UPDATE processos
            SET utilizador = ?,
                pontuacao_risco = ?,
                nivel_risco = ?,
                motivo = ?
            WHERE pid = ?
            """

    conexao = abrir_conexao("base_de_dados/holmes.db")

    if not conexao:
        return
    try:
        cursor = conexao.cursor()
        cursor.execute(query, (utilizador, pontuacao_risco, nivel_risco, motivo, pid))
        conexao.commit()
    except sqlite3.Error:
        print(f"{cores.CORES['vermelho']}[AVISO] Falha ao atualizar registos na base de dados.{cores.CORES['limpo']}")
        pass
    finally:
        fechar_conexao(conexao)


def update_startup(data_analise):
    query = """
            UPDATE programas_startup set data_analise = ?
            """
    conexao = abrir_conexao("base_de_dados/holmes.db")
    if not conexao:
        return
    try:
        cursor = conexao.cursor()
        cursor.execute(query, (data_analise,))
        conexao.commit()
    except sqlite3.Error:
        print(f"{cores.CORES['vermelho']}[AVISO] Falha ao atualizar registos na base de dados.{cores.CORES['limpo']}")
    finally:
        fechar_conexao(conexao)

def criar_tabelas():
    DIRETORIO_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    caminho_db = os.path.join(DIRETORIO_BASE, "base_de_dados", "holmes.db")

    conexao = abrir_conexao(caminho_db)

    if not conexao:
        print(f"{cores.CORES['vermelho']}[AVISO] Houve uma falha na criação da conexão (Base de dados indisponível).{cores.CORES['limpo']}")
        return

    try:
        cursor = conexao.cursor()
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS binarios (
                    id INTEGER PRIMARY KEY,
                    caminho TEXT NOT NULL,
                    hash TEXT NOT NULL,
                    assinatura_digital TEXT NOT NULL,
                    status TEXT NOT NULL,
                    UNIQUE(caminho, hash)
                )
                """)

        cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY,
                    data_acao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    tipo TEXT CHECK(tipo IN ('ação', 'erro')) NOT NULL,
                    modulo TEXT CHECK(modulo IN ('processos', 'persistência', 'redes', 'uteis')) NOT NULL,
                    alvo_nome TEXT,
                    alvo_caminho TEXT,
                    mensagem TEXT
                )
                """)

        cursor.execute("""
                CREATE TABLE IF NOT EXISTS programas_startup (
                    id INTEGER PRIMARY KEY,
                    nome TEXT NOT NULL,
                    caminho TEXT NOT NULL,
                    data_analise DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(nome, caminho)
                )
                """)

        cursor.execute("""
                CREATE TABLE IF NOT EXISTS processos (
                    id INTEGER PRIMARY KEY,
                    id_binario INTEGER NOT NULL,
                    pid INTEGER NOT NULL,
                    ppid INTEGER NOT NULL,
                    nome TEXT NOT NULL,
                    utilizador TEXT,
                    pontuacao_risco INTEGER NOT NULL,
                    nivel_risco TEXT NOT NULL,
                    motivo TEXT ,
                    data_analise DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(id_binario) REFERENCES binarios(id),
                    UNIQUE(pid)
                )
                """)

        cursor.execute("""
                CREATE TABLE IF NOT EXISTS programas_chave_registo (
                    id INTEGER PRIMARY KEY,
                    id_binario INTEGER NOT NULL,
                    nome TEXT NOT NULL,
                    tipo INTEGER NOT NULL,
                    HK TEXT NOT NULL,
                    pontuacao_risco INTEGER NOT NULL,
                    nivel_risco TEXT NOT NULL,
                    motivo TEXT NOT NULL,
                    data_analise DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(id_binario) REFERENCES binarios(id),
                    UNIQUE(nome, HK)
                )
                """)

        cursor.execute("""
                CREATE TABLE IF NOT EXISTS tarefas_agendadas (
                    id INTEGER PRIMARY KEY,
                    id_binario INTEGER NOT NULL,
                    nome TEXT NOT NULL,
                    proxima_execucao DATETIME,
                    ultima_execucao DATETIME,
                    utilizador TEXT,
                    pontuacao_risco INTEGER NOT NULL,
                    nivel_risco TEXT NOT NULL,
                    motivo TEXT,
                    data_analise DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(id_binario) REFERENCES binarios(id),
                    UNIQUE(nome)
                )
                """)

        cursor.execute("""
                CREATE TABLE IF NOT EXISTS servicos (
                    id INTEGER PRIMARY KEY,
                    id_binario INTEGER NOT NULL,
                    nome TEXT NOT NULL,
                    nome_exibido TEXT NOT NULL,
                    estado TEXT NOT NULL,
                    pontuacao_risco INTEGER NOT NULL,
                    nivel_risco TEXT NOT NULL,
                    motivo TEXT,
                    data_analise DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(id_binario) REFERENCES binarios(id),
                    UNIQUE(nome)
                )
                """)

        cursor.execute("""
                CREATE TABLE IF NOT EXISTS conexoes_rede (
                    id INTEGER PRIMARY KEY,
                    id_processo INTEGER NOT NULL,
                    ip_local TEXT NOT NULL,
                    porta_local INTEGER NOT NULL,
                    endereco_remoto TEXT NOT NULL,
                    dominio TEXT NOT NULL,
                    porta_remota TEXT NOT NULL,
                    estado_conexao TEXT NOT NULL,
                    motivo TEXT,
                    data_analise DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    pontuacao_risco INTEGER NOT NULL,
                    nivel_risco TEXT NOT NULL,
                    FOREIGN KEY(id_processo) REFERENCES processos(id),
                    UNIQUE(id_processo, ip_local, porta_local, endereco_remoto, porta_remota, estado_conexao)
                )
                """)
        conexao.commit()
    except Exception:
        print(f"{cores.CORES['vermelho']}[AVISO] Falha ao criar tabelas (Base de dados indisponível).{cores.CORES['limpo']}")
    finally:
        fechar_conexao(conexao)