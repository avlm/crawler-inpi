# -*- coding: utf-8 -*-
import csv

def format_nome_inventor(nome_inventor):
        nomes_inventores = []
        for nome in nome_inventor:
            nomes_inventores.append(nome.strip().replace('/','').strip())
        nome_final = ''
        for nome in nomes_inventores:
            if nome:
                if nome_final:
                    nome_final = nome_final + ' / ' + nome
                else:
                    nome_final = nome_final + nome
        return nome_final

def save_to_csv(patente):
    with open('patentes_consulta_sem_BR.csv', 'a') as csv_patentes:
        writer = csv.writer(csv_patentes, delimiter=';')
        writer.writerow([
            patente['n_pedido'],
            patente['data_deposito'],
            patente['classificacao_ipc'],
            patente['classificacao_cpc'],
            patente['titulo'],
            patente['nome_inventor'],
            patente['nome_depositante']
        ])
        # csv_patentes.close()