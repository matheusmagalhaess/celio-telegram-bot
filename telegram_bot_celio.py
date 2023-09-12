import logging
from telegram import *
from telegram.ext import *
from reset_senha import ResetXiongmaiDate

# Configurações de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Carregar o token a partir de um arquivo de configuração externo
with open("config.txt", "r") as config_file:
    TOKEN = config_file.read().strip()


# Dicionários para organizar as opções de teclado e mensagens
keyboard_options = {
    'start': [
        [InlineKeyboardButton("Atendimento Comercial", callback_data='button_comercial_clicked')],
        [InlineKeyboardButton("Suporte Técnico", callback_data='button_suporte_clicked')]
    ],
    'suporte': [
        [InlineKeyboardButton("CFTV", callback_data='button_cftv_clicked')],
        [InlineKeyboardButton("Veicular", callback_data='button_veicular_clicked')]
    ],
    'cftv': [
        [InlineKeyboardButton("Reset de Senha", callback_data='button_reset_clicked')],
        [InlineKeyboardButton("Especialista", callback_data='button_especialista_clicked')]
    ],
    'dvr':[
        [InlineKeyboardButton("Reset por Data", callback_data='button_dvr_data_clicked')],
        [InlineKeyboardButton("Reset por Código Key", callback_data='button_dvr_key_clicked')]

    ]
}

# Dicionários para organizar as mensagens 
messages = {
    'start': "Olá, {user} 👋!\nMeu nome é Célio, sou o chatbot da Clear CFTV!\nPosso te ajudar em algumas coisas.",
    'suporte': "Perfeito, {user}! Qual vertical você precisa de suporte?",
    'cftv': "{user}, aqui vai algumas opções disponíveis:",
    'reset': "Atualmente, eu ainda só consigo fazer o reset de senha dos DVRs da linha Xmeye para a data de hoje...",
    'senha': "Aqui está 🫡! {senha}",
    'comercial': "Vejo que precisa de atendimento comercial, ligue: 35 3473-4000",
    'especialista': "Olá! Infelizmente não temos especialistas disponíveis no momento..."
}


# Função para enviar uma mensagem, seja com um dicionário ou não
async def send_message(update: Update, context: CallbackContext, msg_key, keyboard_options_key=None):
    user = update.effective_user
    msg = messages[msg_key].format(user=user.first_name)

    
    if keyboard_options_key: # Da um "get" na key que é passada e cria o teclado caso haja uma key
        custom_keyboard = keyboard_options[keyboard_options_key]
        reply_markup = InlineKeyboardMarkup(custom_keyboard)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg, reply_markup=reply_markup)
    else: # Se a key do dicionário de teclado for None, então ele envia somente uma mensagem
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)

# Função de start
async def start(update: Update, context: CallbackContext):
    # Veja, os parâmetros são somente as keys de mensagem e teclado
    await send_message(update, context, 'start', 'start')

# Funções de callback

async def suporte_button_callback(update: Update, context: CallbackContext):
    user = update.effective_user
    await send_message(update, context, 'suporte', 'suporte')

async def cftv_button_callback(update: Update, context: CallbackContext):
    user = update.effective_user
    await send_message(update, context, 'cftv', 'cftv')

async def reset_button_callback(update, context):
    query = update.callback_query
    query.answer()

    senha = ResetXiongmaiDate(20230906)  # Certifique-se de que ResetXiongmaiDate esteja definida corretamente
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Atualmente, eu ainda só consigo fazer o reset de senha dos DVRs da linha Xmeye para a data de hoje... ")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Aqui está 🫡!\n{senha}")


async def comercial_button_callback(update, context):
    await send_message(update, context, 'comercial')

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    comercial_button_handler = CallbackQueryHandler(comercial_button_callback, pattern='^button_comercial_clicked$')
    application.add_handler(comercial_button_handler)

    suporte_button_handler = CallbackQueryHandler(suporte_button_callback, pattern='^button_suporte_clicked$')
    application.add_handler(suporte_button_handler)
    
    cftv_button_handler = CallbackQueryHandler(cftv_button_callback, pattern='^button_cftv_clicked$')
    application.add_handler(cftv_button_handler)
    
    reset_button_handler = CallbackQueryHandler(reset_button_callback, pattern='^button_reset_clicked$')
    application.add_handler(reset_button_handler)

    application.run_polling()
