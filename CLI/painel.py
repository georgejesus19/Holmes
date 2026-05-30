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

def painel_chaves_registo():
    pass

def painel_tarefas_agendadas():
    pass

def painel_servicos():
    pass

def painel_conexoes_rede():
    pass
