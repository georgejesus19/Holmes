from rich.panel import Panel
from rich import print
from CLI.cores import CORES

def painel_de_processo(pid, ppid, nome, caminho, utilizador, hash, estado_da_assinatura, pontuacao, nivel, motivos):
    painel = Panel(f"""
    [bold blue]Identificação:[/bold blue]\n
    • PID: {pid}
    • PPID: {ppid}
    • Nome: {nome}
    • Utilizador do processo: {utilizador}\n
    [yellow]Executável:[/yellow] \n
    • Caminho: {caminho}
    • Hash: {hash}
    • Estado da assinatura digital: {estado_da_assinatura}\n
    [bold green]Avaliação:[/bold green] \n
    • Pontuação de risco: {pontuacao}
    • Nível de risco: {nivel}
    • Motivos: {motivos}
    """,

    title="Detalhes do processo", width=85)
    print(painel)

def painel_chaves_registo(nome, hk, caminho, hash, estado_da_assinatura, pontuacao, nivel, motivos):
    painel = Panel(f"""
    [bold blue]Identificação:[/bold blue]\n
    • Nome: {nome}
    • HIVE_KEY: {hk}\n
    [yellow]Executável:[/yellow]\n
    • Caminho: {caminho}
    • Hash: {hash}
    • Estado da assinatura digital: {estado_da_assinatura}\n
    [bold green]Avaliação:[/bold green]\n
    • Pontuação de risco: {pontuacao}
    • Nível de risco: {nivel}
    • Motivos: {motivos}
    """,

    title="Detalhes do programa", width=85)
    print(painel)

def painel_tarefas_agendadas(nome, ultima_execucao, proxima_execucao, caminho, utilizador,
                             hash, estado_da_assinatura, pontuacao, risco, motivos):

    painel = Panel(f"""
    [bold blue]Identificação:[/bold blue]\n
    • Nome: {nome}
    • Utilizador da tarefa: {utilizador} \n
    [yellow]Executável:[/yellow]\n
    • Caminho: {caminho}
    • Hash: {hash}
    • Estado da assinatura digital: {estado_da_assinatura} 
    • Última execução: {ultima_execucao}
    • Próxima execução: {proxima_execucao}\n
    [bold green]Avaliação:[/bold green]\n
    • Pontuação de risco: {pontuacao}
    • Nível de risco: {risco}
    • Motivos: {motivos}
    """,

    title="Detalhes da tarefa agendada", width=85)
    print(painel)

def painel_servicos(nome, nome_exibido, caminho, hash, estado_da_assinatura, pontuacao, risco, motivos):
    painel = Panel(f"""
    [bold blue]Indentificação:[/bold blue]\n
    • Nome do serviço: {nome}
    • Nome exibido: {nome_exibido} \n
    [yellow]Executável:[/yellow]\n
    • Caminho: {caminho}
    • Hash: {hash}
    • Estado da assinatura digital: {estado_da_assinatura} \n
    [bold green]Avaliação:[/bold green]\n
    • Pontuação de risco: {pontuacao} 
    • Nível de risco: {risco}
    • Motivos: {motivos}
    """,

    title="Detalhes do serviço", width=85)
    print(painel)

def painel_conexoes_rede(ip_local, porta_local, endereco_remota, dominio, porta_remota,
                         estado, pid, ppid, nome, caminho, hash, estado_da_assinatura, pontuacao, risco, motivos):
    painel = Panel(f"""
    [bold blue]Indentificação:[/bold blue]\n
    • PID: {pid}
    • PPID: {ppid}
    • Nome: {nome} \n
    [yellow]Executável:[/yellow]\n
    • Caminho: {caminho}
    • Hash: {hash}
    • Estado da assinatura digital: {estado_da_assinatura} \n
    [bold magenta]Conexão:[/bold magenta]\n
    • Ip local: {ip_local}
    • Porta local: {porta_local}
    • Endereço remoto: {endereco_remota}
    • Porta remota: {porta_remota}
    • Estado da ligação: {estado} \n
    [cyan]Destino:[/cyan]\n
    • Domínio: {dominio} \n
    [bold green]Avaliação:[/bold green]\n
    • Pontuação de risco: {pontuacao} 
    • Nível de risco: {risco}
    • Motivos: {motivos}
    """,

    title="Detalhes da conexão de rede", width=85)
    print(painel)

def painel_consulta_hash():
    painel = Panel(f"""
    Formato suportado : SHA256                
    Limite por minuto : 4 consultas           
    Limite diário     : 500 consultas         
    Internet          : Necessária 
    """,
    title="Consulta de Hash (Regras)", border_style="red", width=60)
    print(painel)