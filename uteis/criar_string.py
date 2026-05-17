def criar_string_motivo(lista):
    if(len(lista) > 0):
        string = "; ".join(lista)
        return string
    return "Sem motivos de suspeita"