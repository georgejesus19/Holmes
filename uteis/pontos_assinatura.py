def pontos_assinatura(estado_assinatura):
    if (estado_assinatura == 'NotSigned'):
        return 20, "Sem assinatura digital"
    elif (estado_assinatura == 'HashMismatch'):
        return 40, "Ficheiro alterado"
    elif (estado_assinatura == 'NotTrusted'):
        return 35, "Certificado não confiável"
    elif (estado_assinatura == 'UnknownError'):
        return 15, "Erro ao verificar assinatura digital"
    return -10, "Assinatura digital válida"