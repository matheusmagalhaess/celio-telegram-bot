from telegram import *
from telegram.ext import *

# Dicionários para organizar as opções de teclado e mensagens
keyboard_options = {
    'start-button': [
        [InlineKeyboardButton("Atendimento Comercial", callback_data='button_comercial_clicked')],
        [InlineKeyboardButton("Suporte Técnico", callback_data='button_suporte_clicked')]
    ],
    'suporte-button': [
        [InlineKeyboardButton("CFTV", callback_data='button_cftv_clicked')],
        [InlineKeyboardButton("Veicular", callback_data='button_veicular_clicked')]
    ],
    'cftv-button': [
        [InlineKeyboardButton("Reset de Senha", callback_data='button_reset_clicked')],
        [InlineKeyboardButton("Especialista", callback_data='button_especialista_clicked')]
    ],
    'dvr-button':[
        [InlineKeyboardButton("Reset por Data", callback_data='button_reset_data_clicked')],
        [InlineKeyboardButton("Reset por Código Key", callback_data='button_reset_key_clicked')]

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
    'especialista': "Olá! Infelizmente não temos especialistas disponíveis no momento...",
    'dvr': "Por qual método você deseja fazer seu reset de senha?"
}