from pygments.styles.dracula import green
from rich.panel import Panel
from rich import print


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

def painel_chaves_registo(nome, hk, tipo, caminho, hash, estado_da_assinatura, pontuacao, nivel, motivos):
    painel = Panel(f"""
    [bold blue]Identificação:[/bold blue]\n
    • Nome: {nome}
    • Iniciado por (HIVE_KEY): {hk}
    • Tipo: {tipo}\n
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
    • Tarefa executada: {caminho}
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
    • Serviço: {nome}
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
                         estado, pid, nome, caminho, hash, estado_da_assinatura, pontuacao, risco, motivos):
    painel = Panel(f"""
    [bold blue]Indentificação:[/bold blue]\n
    • PID: {pid}
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

def painel_resultado_consulta_hash(hash, detecoes, suspeitas, seguros, desconhecidos):

    if detecoes > suspeitas and detecoes > seguros and detecoes > desconhecidos:
        conclusao = "[red]MALICIOSO[/red] - A maioria dos motores indicou o hash como malicioso."

    elif suspeitas > detecoes and suspeitas > seguros and suspeitas > desconhecidos:
        conclusao = "[yellow]SUSPEITO[/yellow] - A maioria dos motores reportou comportamentos suspeitos."

    elif seguros > detecoes and seguros > suspeitas and seguros > desconhecidos:
        conclusao = "[bold green]SEGURO[/bold green] - A maioria dos motores considera o hash legítimo."

    elif desconhecidos > detecoes and desconhecidos > suspeitas and desconhecidos > seguros:
        conclusao = "[bold blue]DESCONHECIDO[/bold blue] - O hash não tem informações suficientes nos motores consultados."

    else:
        conclusao = "[cyan]INCONCLUSIVO[/cyan] - Os resultados obtidos não permitem saber a reputação do hash."

    painel = Panel(f"""
    Hash analisado : {hash} \n  
    Deteções de malware      : {detecoes} motores
    Comportamento suspeito   : {suspeitas} motores
    Classificado como seguro : {seguros} motores
    Hash desconhecido        : {desconhecidos} motores \n
    Conclusão : {conclusao}
    
                    """,
    title="Resulta da consulta do hash", border_style="green" ,width=100)
    print(painel)

def mostrar_painel_startup(novos, removidos, data_analise, data_atual):

    conteudo = ""

    if novos or removidos:
        conteudo += "Mudanças efetuadas desde a última análise:\n"

        if novos:
            conteudo += f"Ficheiros adicionados: {', '.join(novos)}\n"

        if removidos:
            conteudo += f"Ficheiros removidos: {', '.join(removidos)}\n"
    else:
        conteudo += "Não houve mudanças efetuadas desde a última análise\n"

    conteudo += "\n"

    conteudo += (
        f"Data da última análise: {data_analise}" if data_analise else f"Data da última análise: {data_atual}")


    painel = Panel(conteudo.strip(),title="Monitoramento da pasta startup",border_style="cyan", width=85)
    print(painel)