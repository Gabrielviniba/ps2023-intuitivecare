import requests
import os
import zipfile
from bs4 import BeautifulSoup as bs

def baixar_arquivo(url, nome_arquivo):
    response = requests.get(url)
    with open(nome_arquivo, 'wb') as arquivo:
        arquivo.write(response.content)
    print(f"Arquivo '{nome_arquivo}' baixado com sucesso!")

def filtrar_arquivos(links):
    arquivos_filtrados = [link['href'] for link in links if 'anexo' in link.text.lower()]
    return arquivos_filtrados

def zipar_arquivos(pasta_origem, nome_zip):
    with zipfile.ZipFile(nome_zip, 'w') as zip_file:
        for pasta_raiz, _, arquivos in os.walk(pasta_origem):
            for arquivo in arquivos:
                caminho_completo = os.path.join(pasta_raiz, arquivo)
                nome_arquivo_zip = os.path.relpath(caminho_completo, pasta_origem)
                zip_file.write(caminho_completo, nome_arquivo_zip)
    print(f"Arquivos compactados em '{nome_zip}'")

def main():
    url = 'https://www.gov.br/ans/pt-br/assuntos/consumidor/o-que-o-seu-plano-de-saude-deve-cobrir-1/o-que-e-o-rol-de-procedimentos-e-evento-em-saude'
    response = requests.get(url)
    soup = bs(response.text, 'html.parser')
    links = soup.find_all('a')
    arquivos_filtrados = filtrar_arquivos(links)
    pasta_destino = 'arquivos_anexo'
    os.makedirs(pasta_destino, exist_ok=True)
    for arquivo_url in arquivos_filtrados:
        arquivo_url_completa = requests.compat.urljoin(url, arquivo_url)
        nome_arquivo = os.path.basename(arquivo_url_completa)
        caminho_arquivo = os.path.join(pasta_destino, nome_arquivo)
        baixar_arquivo(arquivo_url_completa, caminho_arquivo)
    nome_zip = 'arquivos_anexo.zip'
    zipar_arquivos(pasta_destino, nome_zip)

if __name__ == '__main__':
    main()
