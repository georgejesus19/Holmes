from rich.panel import Panel
from rich import print

def painel_de_processo(pid, ppid, nome, caminho, utilizador, hash, estado_da_assinatura, pontuacao, nivel, motivos):
    painel = Panel(f"""
    Identificação: \n
    • PID: {pid}
    • PPID: {ppid}
    • Nome: {nome}
    • Utilizador do processo: {utilizador}\n
    Executável: \n
    • Caminho: {caminho}
    • Hash: {hash}
    • Estado da assinatura digital: {estado_da_assinatura}\n
    Avaliação: \n
    • Pontuação de risco: {pontuacao}
    • Nível de risco: {nivel}
    • Motivos: {motivos}
                            """,
                   title="Detalhes do processo", width=85)
    print(painel)

def painel_chaves_registo(nome, hk, caminho, hash, estado_da_assinatura, pontuacao, nivel, motivos):
    painel = Panel(f"""
    Identificação: \n
    • Nome: {nome}
    • HIVE_KEY: {hk}
    Executável: \n
    • Caminho: {caminho}
    • Hash: {hash}
    • Estado da assinatura digital: {estado_da_assinatura}\n
    Avaliação: \n
    • Pontuação de risco: {pontuacao}
    • Nível de risco: {nivel}
    • Motivos: {motivos}
    
                        """,
                   title="Detalhes do programa", width=85)
    print(painel)

def painel_tarefas_agendadas(nome, ultima_execucao, proxima_execucao, caminho, utilizador,
                             hash, estado_da_assinatura, pontuacao, risco, motivos):

    painel = Panel(f"""
    Identificação: \n
    • Nome: {nome}
    • Utilizador da tarefa: {utilizador} \n
    Executável: \n
    • Caminho: {caminho}
    • Hash: {hash}
    • Estado da assinatura digital: {estado_da_assinatura} 
    • Última execução: {ultima_execucao}
    • Próxima execução: {proxima_execucao}\n
    Avaliação: \n
    • Pontuação de risco: {pontuacao}
    • Nível de risco: {risco}
    • Motivos: {motivos}
                """,
                title="Detalhes da tarefa agendada", width=85)
    print(painel)

def painel_servicos(nome, nome_exibido, caminho, hash, estado_da_assinatura, pontuacao, risco, motivos):
    painel = Panel(f"""
    Indentificação: \n
    • Nome do serviço: {nome}
    • Nome exibido: {nome_exibido} \n
    Executável: \n
    • Caminho: {caminho}
    • Hash: {hash}
    • Estado da assinatura digital: {estado_da_assinatura} \n
    Avaliação: \n
    • Pontuação de risco: {pontuacao} 
    • Nível de risco: {risco}
    • Motivos: {motivos}
                        """,
                   title="Detalhes do serviço", width=85)
    print(painel)

def painel_conexoes_rede(ip_local, porta_local, endereco_remota, dominio, porta_remota,
                         estado, pid, ppid, nome, caminho, hash, estado_da_assinatura, pontuacao, risco, motivos):
    painel = Panel(f"""
    Indentificação: \n
    • PID: {pid}
    • PPID: {ppid}
    • Nome: {nome} \n
    Executável: \n
    • Caminho: {caminho}
    • Hash: {hash}
    • Estado da assinatura digital: {estado_da_assinatura} \n
    Conexão: \n
    • Ip local: {ip_local}
    • Porta local: {porta_local}
    • Endereço remoto: {endereco_remota}
    • Porta remota: {porta_remota}
    • Estado da ligação: {estado} \n
    Destino: \n
    •Domínio: {dominio} \n
    Avaliação: \n
    • Pontuação de risco: {pontuacao} 
    • Nível de risco: {risco}
    • Motivos: {motivos}
                    """,
                   title="Detalhes da conexão de rede", width=85)
    print(painel)