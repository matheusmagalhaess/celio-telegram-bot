import logging
from telegram import *
from telegram.ext import *
from reset_senha import ResetXiongmaiDate

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = '6538656591:AAG5fMTY0teI_wEVi6t2LeHeXIqH4XR6yIw'  # Substitua pelo seu token

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user 
    custom_keyboard = [[InlineKeyboardButton("Atendimento Comercial", callback_data='button_comercial_clicked')],
                       [InlineKeyboardButton("Suporte Técnico", callback_data='button_suporte_clicked')]]
    reply_markup = InlineKeyboardMarkup(custom_keyboard)
    saudacao = f'Olá, {user.first_name}👋!\nMeu nome é Célio, sou o chatbot da Clear CFTV!\nPosso te ajudar em algumas coisas.'
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=saudacao, reply_markup=reply_markup)

async def suporte_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    custom_keyboard = [[InlineKeyboardButton("CFTV", callback_data='button_cftv_clicked')],
                       [InlineKeyboardButton("Veicular", callback_data='button_veicular_clicked')]]
    reply_markup = InlineKeyboardMarkup(custom_keyboard)
    msg = f"Perfeito, {user.first_name}! Qual vertical você precisa de suporte?"
    await context.bot.send_message(chat_id=update.effective_chat.id, text = msg, reply_markup=reply_markup)

async def cftv_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    custom_keyboard = [[InlineKeyboardButton("Reset de Senha", callback_data='button_reset_clicked')],
                       [InlineKeyboardButton("Especialista", callback_data='button_especialista_clicked')]]
    reply_markup = InlineKeyboardMarkup(custom_keyboard)
    msg = f"{user.first_name}, aqui vai algumas opções disponíveis:"
    await context.bot.send_message(chat_id=update.effective_chat.id, text = msg, reply_markup=reply_markup)

async def reset_button_callback(update, context):
    query = update.callback_query
    query.answer()
    
    senha = ResetXiongmaiDate(20230906)  # Certifique-se de que ResetXiongmaiDate esteja definida corretamente
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Atualmente, eu ainda só consigo fazer o reset de senha dos DVRs da linha Xmeye para a data de hoje... ")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Aqui está 🫡!\n{senha}")

async def especialista_button_callback(update, context):
    query = update.callback_query
    query.answer()

async def comercial_button_callback(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Vejo que precisa de atendimento comercial, ligue: 35 3473-4000')

    await context.bot.send_message(chat_id=update.effective_chat.id, text='Olá! Infelizmente não temos especialistas disponíveis no momento...')

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

    especialista_handler = CallbackQueryHandler(especialista_button_callback, pattern='^button_especialista_clicked$')
    application.add_handler(especialista_handler)

    application.run_polling()
