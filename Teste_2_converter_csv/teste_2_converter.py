import requests
import os
import pandas as pd
import zipfile
from bs4 import BeautifulSoup as bs
import tabula

def baixar_arquivo(url, nome_arquivo):
    response = requests.get(url)
    with open(nome_arquivo, 'wb') as arquivo:
        arquivo.write(response.content)
    print(f"Arquivo '{nome_arquivo}' baixado com sucesso!")

def zipar_arquivo(nome_arquivo, nome_zip):
    with zipfile.ZipFile(nome_zip, 'w') as zip_file:
        zip_file.write(nome_arquivo, os.path.basename(nome_arquivo))
    print(f"Arquivo '{nome_arquivo}' compactado em '{nome_zip}'")

def filtrar_arquivos(links, nome_arquivo):
    return [link['href'] for link in links if nome_arquivo.lower() in link.text.lower()]

def extrair_tabelas(nome_arquivo):
    dfs = tabula.read_pdf(nome_arquivo, pages='all', lattice=True, multiple_tables=True)

    # Cria um novo dataframe com o primeiro cabeçalho
    primeira_tabela = dfs[0]
    tabelas_unificadas = pd.concat(dfs[1:], ignore_index=True)

    return primeira_tabela, tabelas_unificadas

def substituir_palavras(df):
    df = df.replace({"OD": "Seg. Odontológica", "AMB": "Seg. Ambulatorial"}, regex=True)
    return df

def remover_arquivo(arquivo):
    if os.path.exists(arquivo):
        os.remove(arquivo)


def main():
    url = 'https://www.gov.br/ans/pt-br/assuntos/consumidor/o-que-o-seu-plano-de-saude-deve-cobrir-1/o-que-e-o-rol-de-procedimentos-e-evento-em-saude'
    response = requests.get(url)
    soup = bs(response.text, 'html.parser')
    links = soup.find_all('a')
    links_filtrados = filtrar_arquivos(links, 'anexo i - lista completa de procedimentos (.pdf)')
    if links_filtrados:
        arquivo_url_completa = requests.compat.urljoin(url, links_filtrados[0])
        nome_arquivo = os.path.basename(arquivo_url_completa)
        baixar_arquivo(arquivo_url_completa, nome_arquivo)
        primeira_tabela, tabelas_unificadas = extrair_tabelas(nome_arquivo)
        if not tabelas_unificadas.empty:
            tabelas_unificadas = tabelas_unificadas.loc[:, ~tabelas_unificadas.columns.str.contains('^Unnamed')]
            tabelas_unificadas = substituir_palavras(tabelas_unificadas)
            nome_csv = 'tabelas_unificadas.csv'
            tabelas_unificadas.to_csv(nome_csv, index=False)
            print(f"Tabelas unificadas salvas em '{nome_csv}'")
            nome_zip = 'Teste_Gabriel_Vinicius_Borges_De_Almeida.zip'
            zipar_arquivo(nome_csv, nome_zip)
            remover_arquivo(nome_csv)
            remover_arquivo(nome_arquivo)

if __name__ == '__main__':
    main()
