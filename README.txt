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

Futuro / Extras:

Integração de IA leve para análise inteligente de processos e arquivos

Interface Rich para visualização avançada;
Monitoramento da pasta Startup em tempo real;
Análise manual com a base de dados;
Integração com API externa (VirusTotal).