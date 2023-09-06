import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, Updater
import requests
from msgs import *
from reset_senha import *


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


TOKEN = '6538656591:AAG5fMTY0teI_wEVi6t2LeHeXIqH4XR6yIw'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=saudacao)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=opcoes)

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    
    senha = ResetXiongmaiDate(20230905)
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Atualmente, eu ainda só consigo fazer o reset de senha dos DVRs da linha Xmeye")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Aqui está 🫡!\n{senha}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    
    reset_handler = CommandHandler('reset', reset)
    application.add_handler(reset_handler)

    application.run_polling()


    

    