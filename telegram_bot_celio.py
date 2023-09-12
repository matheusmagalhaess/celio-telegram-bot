import logging
from telegram import *
from telegram.ext import *
from reset_senha import ResetXiongmaiDate
from dics import messages, keyboard_options

# Configurações de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Carregar o token a partir de um arquivo de configuração externo
with open('config.txt', "r") as config_file:
    TOKEN = config_file.read().strip()


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
    await send_message(update, context, 'start', 'start-button')

# Funções de callback

async def suporte_button_callback(update: Update, context: CallbackContext):
    user = update.effective_user
    await send_message(update, context, 'suporte', 'suporte-button')

async def cftv_button_callback(update: Update, context: CallbackContext):
    user = update.effective_user
    await send_message(update, context, 'cftv', 'cftv-button')

async def reset_button_callback(update, context):
    user = update.effective_user
    await send_message(update, context, 'dvr', 'dvr-button')

async def reset_data_button_callback(update: Update, context: CallbackContext):
    user = update.effective_user
    data = 20230912
    senha = ResetXiongmaiDate(data,'date')
    await send_message(update, context, 'reset')
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Aqui está 🫡!\n{senha}")

async def reset_key_button_callback(update: Update, context: CallbackContext):
    user = update.effective_user
    codigo_key = 77605748
    senha = ResetXiongmaiDate(codigo_key,'key')
    await send_message(update, context, 'reset')
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

    reset_data_button_handler = CallbackQueryHandler(reset_data_button_callback, pattern='^button_reset_data_clicked$')
    application.add_handler(reset_data_button_handler)

    reset_key_button_handler = CallbackQueryHandler(reset_key_button_callback, pattern='^button_reset_key_clicked$')
    application.add_handler(reset_key_button_handler)

    application.run_polling()
