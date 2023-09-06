from bs4 import BeautifulSoup
import requests

def ResetXiongmaiDate(cod):

        url = 'https://cctvwiki.com/en/xiongmai-tech-password-reset/'

        data = {'txtCode': cod}

        response = requests.post(url, data=data)

        if response.status_code == 200:
                html = response.text
                # Cria um objeto BeautifulSoup para analisar o HTML
                soup = BeautifulSoup(html, 'html.parser')

                # Encontra o elemento <span> com id="KQ"
                span_element = soup.find('span', {'id': 'KQ'})

                # Verifica se o elemento foi encontrado
                if span_element:
                    # Obtém o texto dentro do elemento <span>
                    senha = span_element.get_text()
                    parts = senha.split("Time:")
                    senha = parts[0]
                    return senha
                else:
                    senha = "Erro! tente novamente em alguns minutos..."
                    return senha
        else:
            senha = 'Erro! tente novamente em alguns minutos...'
            return senha 