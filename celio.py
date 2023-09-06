from imports import *

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
   
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Olá! Eu sou o Célio! Como posso te ajudar?")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    def resetXiongmai(cod):

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
    
    senha = resetXiongmai(20230905)
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Atualmente, eu ainda só consigo fazer o reset de senha dos DVRs da linha Xmeye")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Aqui está 🫡!\n{senha}")



if __name__ == '__main__':
    application = ApplicationBuilder().token('6538656591:AAG5fMTY0teI_wEVi6t2LeHeXIqH4XR6yIw').build()
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    
    reset_handler = CommandHandler('reset', reset)
    application.add_handler(reset_handler)

    application.run_polling()

    

    