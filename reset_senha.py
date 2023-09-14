from bs4 import BeautifulSoup
import requests, time

def ResetXiongmaiDate(cod,tipo):
        cont = 0
        url = 'https://cctvwiki.com/en/xiongmai-tech-password-reset/'

        data = {'txtCode': cod}

        response = requests.post(url, data=data)

        if response.status_code == 200:
                html = response.text
                # Cria um objeto BeautifulSoup para analisar o HTML
                soup = BeautifulSoup(html, 'html.parser')

                # Encontra o elemento <span> com id="KQ"
                span_element = soup.findAll('span', {'id': 'KQ'})

                # Verifica se o elemento foi encontrado
                if span_element:
                    # Obtém o texto dentro do elemento <span>
                    if tipo == 'date':
                        senha = span_element[0].get_text()
                        parts = senha.split("Time:")
                        senha = parts[0]
                    elif tipo == 'key':
                        senha = span_element[1].get_text()
                        parts = senha.split("Time:")
                        senha = parts[0]
                    
                    if senha == 'Super Password: Wait 5s and try it again':
                         time.sleep(6)
                         ResetXiongmaiDate(cod,tipo)
                         cont+=1
                         if cont > 3:
                            senha = 'Erro! tente novamente em alguns minutos...'
                            return senha
                    else:
                        return senha
                else:
                    senha = "Erro! tente novamente em alguns minutos..."
                    return senha
        else:
            senha = 'Erro! tente novamente em alguns minutos...'
            return senha 