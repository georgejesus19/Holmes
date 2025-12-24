🕵️‍♂️ Holmes v1.0 — Detector de Backdoors Offline

O Holmes é um detector de backdoors leve, simples e totalmente offline,
desenvolvido para auditar sistemas Windows e identificar potenciais ameaças relacionadas a processos, persistência,
conexões de rede e alterações suspeitas no sistema. A ferramenta foi pensada para ser
eficiente, auto-contida e operável mesmo em máquinas modestas.

📌 Resumo das Funcionalidades:
    🔍 Análise de processos em execução
    🗂️ Detecção de mecanismos de persistência
    🌐 Mapeamento de conexões de rede -> (em desenvolvimento)
    📝 Sistema de logs integrado
    🖥️ Interface simples e prática
    🔐 Verificação de assinatura digital
    #️⃣ Cálculo de hash dos executáveis
    🧾 Expansão de variáveis de ambiente

A ferramenta está dividida nos seguintes módulos:

🔬 1. Módulo de Processos

Responsável por identificar processos ativos com comportamentos suspeitos.
Para cada processo, são recolhidas as seguintes informações:

- PID (Process ID);
- PPID (Parent Process ID);
- Nome do processo;
- Caminho do executável;
- Utilizador;
- Hash do binário;
- Estado da assinatura digital;

Este módulo compara nomes e caminhos dos processos com uma blacklist.
Se uma correspondência for encontrada, o processo é marcado como suspeito e enviado para o ficheiro de logs correspondente.

🧷 2. Módulo de Persistência de Arquivos

Responsável pela análise de mecanismos de permanência no sistema.
Abrange:

- Chaves de registro de inicialização (HKCU e HKLM);
- Serviços;
- Tarefas agendadas;
- Pastas de Startup
Assim como no módulo de processos, utiliza a blacklist e a verificação de assinatura digital.

✔️ Informações recolhidas:
Chaves de Registro:

Nome do programa
Caminho do binário
Tipo (quem iniciou)
Utilizador responsável
Assinatura digital
Hash do binário

Serviços:

Nome do serviço;
Nome de exibição;
Estado (ativo/inativo);
Caminho do executável;
Assinatura digital;
Hash.

Tarefas Agendadas:

Nome da tarefa;
Próxima execução;
Última execução;
Caminho executado;
Utilizador da tarefa;
Assinatura digital;
Hash do binário.

🌐 3. Módulo de Redes

Este módulo:

- Mapeia as conexões ativas
- Relaciona IPs externos aos processos responsáveis
- Compara endereços remotos com uma lista de IPs suspeitos
- Registra eventos relevantes em logs

📄 4. Módulo de Logs

Permite visualizar os conteúdos dos ficheiros de logs gerados pelos demais módulos:

- Logs de processos;
- Logs de persistência;
- Logs de rede.

🖥️ 5. Módulo de Interface

Interface simples e leve, responsável por:

- Mostrar as opções disponíveis
- Receber inputs do utilizador
- Exibir o nome da ferramenta no topo
- Não interfere na análise, apenas facilita a interação.

🔧 Estado Atual do Projeto

✔️ Hash, verificação de assinatura digital e expansão de variáveis de ambiente já implementados
✔️ Nenhum bug detetado até ao momento
✔️ Todas as funcionalidades dos módulos já se encontram disponíveis
✔️ Ferramenta operacional e estável