🕵️‍♂️ Holmes v1.0 — Detector de Backdoors Offline

O Holmes é um detector de backdoors leve, simples e totalmente offline,
desenvolvido para auditar sistemas Windows e identificar potenciais ameaças relacionadas a processos, persistência, conexões de rede e alterações suspeitas no sistema. A ferramenta foi pensada para ser eficiente, auto-contida e operável mesmo em máquinas modestas.

📌 Resumo das Funcionalidades Atuais:
🔍 Análise de processos em execução, com detecção de comportamentos suspeitos
🗂️ Detecção de mecanismos de persistência (registro, serviços, tarefas agendadas, pastas de Startup)
🌐 Mapeamento de conexões de rede (em desenvolvimento)
📝 Sistema de logs básico (futuro: integração com SQLite)
🖥️ Interface simples e prática
🔐 Verificação de assinatura digital de binários
#️⃣ Cálculo de hash de executáveis
🧾 Expansão de variáveis de ambiente para paths dinâmicos
⚡ Normalização e padronização de caminhos
✅ Comparação com listas de nomes, caminhos e domínios suspeitos

Módulos do Holmes
🔬 1. Módulo de Processos
Identifica processos ativos suspeitos. Para cada processo, são recolhidas informações detalhadas:

PID (Process ID);
PPID (Parent Process ID);
Nome do processo;
Caminho do executável (normalizado e expandido);
Utilizador;
Hash do binário;
Estado da assinatura digital;

O módulo compara nomes e caminhos com uma blacklist. Processos suspeitos são registrados em logs específicos.

🧷 2. Módulo de Persistência de Arquivos

Analisa mecanismos de permanência no sistema, incluindo:

Chaves de registro de inicialização (HKCU e HKLM);
Serviços do Windows;
Tarefas agendadas;
Pastas de Startup;

Informações recolhidas:

Chaves de Registro:
Nome do programa;
Caminho do binário;
Tipo (quem iniciou);
Utilizador responsável;
Assinatura digital;
Hash do binário.

Serviços:

Nome do serviço;
Nome de exibição;
Estado;
Caminho do executável;
Assinatura digital;
Hash.

Tarefas Agendadas:

Nome da tarefa;
Próxima execução;
Última execução;
Caminho executado;
Utilizador;
Assinatura digital;
Hash do binário.

🌐 3. Módulo de Redes

Responsável pelo mapeamento de conexões de rede:

Identifica conexões ativas e processos responsáveis;
Compara IPs remotos com lista de endereços suspeitos.


📄 4. Módulo de Logs

Permite visualizar e registar informações geradas pelos módulos, numa base de dados local:

Logs de processos
Logs de persistência
Logs de rede

Integração com SQLite para armazenamento persistente.

🖥️ 5. Módulo de Interface

Interface leve para facilitar interação com o utilizador:

Mostra opções disponíveis;
Recebe inputs do utilizador;
Exibe nome da ferramenta no topo;
Não interfere nas análises.

🔧 Estado Atual do Projeto

Implementado:
Hash e assinatura digital coletados em todos os módulos
Expansão de variáveis de ambiente funcionando
Normalização e padronização de caminhos
Comparação com blacklist de nomes, caminhos e domínios
Interface básica pronta e funcional
Ferramenta operacional e estável

🆕 🔎 6. Módulo de Análise Manual

Permite ao utilizador analisar um ficheiro ou processo específico sob demanda,
fora das análizações automáticas.

📌 Funcionalidades:
Introdução manual de um caminho de ficheiro ou executável;
Expansão de variáveis de ambiente (ex: %APPDATA%, %TEMP%);
Normalização do caminho para evitar inconsistências;
Cálculo do hash do ficheiro;
Verificação da assinatura digital;
Comparação com:
    Blacklist de ficheiros;
    Caminhos suspeitos;
Exibição detalhada dos resultados da análise.

🎯 Objetivo:

Este modo dá mais controlo ao utilizador, permitindo investigar ficheiros suspeitos de forma isolada — útil quando:

Um antivírus levanta suspeitas;
Um ficheiro desconhecido aparece no sistema;
O utilizador quer validar manualmente um binário.

▶️ Como Utilizar o Holmes

1️⃣ Pré-requisitos

Antes de executar a ferramenta, garante que tens:

Python instalado (versão 3.10 ou superior recomendada);
Python adicionado às variáveis de ambiente (PATH);

👉 Isto permite executar o comando python a partir de qualquer diretório no sistema.

2️⃣ Executar o Prompt de Comando como Administrador

Abre o CMD como administrador.

📌 Isto é necessário porque o Holmes precisa de permissões elevadas para:

Ler processos do sistema;
Aceder a serviços do Windows;
Consultar tarefas agendadas;
Ler certas chaves do registo (HKLM);
Analisar caminhos protegidos do sistema.

3️⃣ Navegar até à pasta do Holmes

No CMD, utiliza o comando cd para navegar até à pasta onde o projeto está localizado.

Exemplo: cd C:\Users\TeuNome\Desktop\Holmes

4️⃣ Executar a ferramenta

Dentro da pasta do projeto, executa:

python main.py

5️⃣ Utilizar o menu

Após iniciar, será apresentado um menu com as funcionalidades disponíveis, como:

Análise de processos;
Análise de persistência;
Análise de rede;
Análise manual;

Futuro / Extras:

Integração de IA leve para análise inteligente de processos e arquivos

Interface Rich para visualização avançada;
Monitoramento da pasta Startup em tempo real;
Análise manual com a base de dados;
Integração com API externa (VirusTotal).