import fnmatch
from uteis import validar_resposta

TAREFAS_CRITICAS = [
    "\\Microsoft\\Windows\\WindowsUpdate\\*",
    "\\Microsoft\\Windows\\UpdateOrchestrator\\*",
    "\\Microsoft\\Windows\\TaskScheduler\\Maintenance Configurator",
    "\\Microsoft\\Windows\\TaskScheduler\\Regular Maintenance",
    "\\Microsoft\\Windows\\SystemRestore\\*",
    "\\Microsoft\\Windows\\Windows Defender\\*",
    "\\Microsoft\\Windows\\Defrag\\*",
    "\\Microsoft\\Windows\\DiskCleanup\\*",
    "\\Microsoft\\Windows\\Customer Experience Improvement Program\\*",
    "\\Microsoft\\Windows\\Application Experience\\*",
    "\\Microsoft\\Windows\\MemoryDiagnostic\\*",
    "\\Microsoft\\Windows\\Shell\\*",
    "\\Microsoft\\Windows\\Time Synchronization\\*",
    "\\Microsoft\\Windows\\Registry\\*"
]

CORES = {'vermelho':'\033[31m',
         'limpo':'\033[m'}

def desativar_tarefa():
    pass