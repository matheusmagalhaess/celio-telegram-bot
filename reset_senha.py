from bs4 import BeautifulSoup
import requests, time

def ResetXiongmaiDate(cod,tipo):
    senha = 'Super Password: Wait 5s and try it again'
    while senha == 'Super Password: Wait 5s and try it again': # Loop para caso o servidor não responda com a senha, ele tente por até 3 vezes... 
        cont = 0 # Tentativas de conseguir a senha
        url = 'https://cctvwiki.com/en/xiongmai-tech-password-reset/' # URL da API
        data = {'txtCode': cod} # Parâmetro que eu vou passar para fazer o "POST"
        response = requests.post(url, data=data) # Faço o POST na URL
        
        if response.status_code == 200: # Se o servidor responder
            html = response.text # Crio um html de resposta

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
                    if senha != 'Super Password: Wait 5s and try it again':
                        break
                elif tipo == 'key':
                    senha = span_element[1].get_text()
                    parts = senha.split("Time:")
                    senha = parts[0]
                    if senha != 'Super Password: Wait 5s and try it again':
                        break
            cont += 1
            time.sleep(5)
            if cont > 2:
                senha = 'Lamento, mas o servidor de reset de senha está indisponível no momento... Aguarde alguns minutos e tente novamente...'
                break
        else:
            senha = "Lamento, mas o servidor de reset de senha está indisponível no momento... Aguarde alguns minutos e tente novamente...",
            break
            
    return senha