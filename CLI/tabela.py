from rich import print
from rich.table import Table

from rich.table import Table
from rich.console import Console

console = Console()

tabela = Table(show_header=True, header_style="bold cyan", expand=True)

tabela.add_column("PID", justify="center", no_wrap=True)
tabela.add_column("PPID", justify="center", no_wrap=True)
tabela.add_column("Nome", no_wrap=True)
tabela.add_column("Caminho", overflow="ellipsis", no_wrap=True)
tabela.add_column("Utilizador", overflow="ellipsis", no_wrap=True)
tabela.add_column("Hash", overflow="ellipsis", no_wrap=True)
tabela.add_column("Assinatura", no_wrap=True)
tabela.add_column("Risco", justify="center", no_wrap=True)
tabela.add_column("Nível", no_wrap=True)

tabela.add_row(
    "1284",
    "9100",
    "msedge.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "GEORGE\\georg",
    "b4ea52196967c69a61c114c9934950f511f26bded473107e1b6c37cd8a22bf9e",
    "Válida",
    "0",
    "Baixo"
)

console.print(tabela)
