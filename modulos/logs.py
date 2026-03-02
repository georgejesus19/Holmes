import os
import sqlite3
import traceback

from tabulate import tabulate

def abrir_conexao(caminho_db):
    try:
        conexao = sqlite3.connect(caminho_db)
        return conexao
    except sqlite3.Error as erro:
        print(f"Erro ao realizar conexão: {erro}")
        return None

def fechar_conexao(conexao):
    if conexao:
        try:
            conexao.close()
        except sqlite3.Error as erro:
            print(f"Erro ao fechar a conexão: {erro}")

def reduzir_caminho(caminho, limite=40):
    if caminho and len(caminho) > limite:
        return "..." + caminho[-limite:]
    return caminho


def inserir_processo(pid, ppid, nome, caminho, utilizador, hash, assinatura, tabela):
    query = f""" 
            INSERT INTO {tabela} (pid, ppid, nome, caminho, utilizador, hash, assinatura) 
            VALUES (?, ?, ?, ?, ?, ?, ?) 
            """
    conexao = abrir_conexao("base_de_dados/holmes.db")
    if conexao:
        cursor = conexao.cursor()
        cursor.execute(query ,(pid, ppid, nome, caminho, utilizador, hash, assinatura))
        conexao.commit()
        fechar_conexao(conexao)


def consultar_processos(tabela):
    query = f"SELECT * FROM {tabela}"
    conexao = abrir_conexao("base_de_dados/holmes.db")

    if conexao:
        cursor = conexao.cursor()
        cursor.execute(query)

        # Pegar todos os resultados
        resultados = cursor.fetchall()

        # Imprimir cada linha
        for linha in resultados:
            print("------------------------------------------------------------")
            print(f"PID                    : {linha[0]}")
            print(f"PPID                   : {linha[1]}")
            print(f"Nome                   : {linha[2]}")
            print(f"Caminho                : {linha[3]}")
            print(f"Utilizador             : {linha[4]}")
            print(f"Hahs                   : {linha[5]}")
            print(f"Estado da assinatura   : {linha[6]}")
            print("------------------------------------------------------------")
        # Fechar a conexão
        conexao.close()
caminho_db = "C:\\Users\\georg\\Holmes\\base_de_dados\\holmes.db"
conexao = abrir_conexao(caminho_db)

if conexao:
    cursor = conexao.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS processos (id integer PRIMARY KEY , pid integer,"
                   "ppid integer, nome text,"
                   "caminho text, utilizador text,"
                   "hash text, assinatura text)")

    cursor.execute("CREATE TABLE IF NOT EXISTS processos_suspeitos (id integer PRIMARY KEY , pid integer,"
                   "ppid integer, nome text,"
                   "caminho text, utilizador text,"
                   "hash text, assinatura text)")
    conexao.commit()
    fechar_conexao(conexao)