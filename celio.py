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
    custom_keyboard = [[InlineKeyboardButton("Reset de Senha", callback_data='button_reset_clicked')]]
    reply_markup = InlineKeyboardMarkup(custom_keyboard)
    saudacao = f'Olá, {user.first_name}👋!\nMeu nome é Célio, sou o chatbot da Clear CFTV!\nPosso te ajudar em algumas coisas.'
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=saudacao, reply_markup=reply_markup)

async def reset_button_callback(update, context):
    query = update.callback_query
    query.answer()
    
    senha = ResetXiongmaiDate(20230905)  # Certifique-se de que ResetXiongmaiDate esteja definida corretamente
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Atualmente, eu ainda só consigo fazer o reset de senha dos DVRs da linha Xmeye")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Aqui está 🫡!\n{senha}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    reset_button_handler = CallbackQueryHandler(reset_button_callback, pattern='^button_reset_clicked$')
    application.add_handler(reset_button_handler)

    application.run_polling()
