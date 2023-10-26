import telebot
import logging
import time
import threading
from reset_senha import ResetXiongmaiDate
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from cpf import cpf_check

### ---------------------- SETUP -------------------------------------------### 


# Carregar o token a partir de um arquivo de configuração externo
with open('config.txt', "r") as config_file:
    TOKEN = config_file.read().strip()

# Configuração do formato de log
log_format = '%(asctime)s [%(levelname)s] - %(message)s'
log_formatter = logging.Formatter(log_format)

# Configuração do codificador
log_handler = logging.StreamHandler()
log_handler.setFormatter(log_formatter)

# Configuração do nível de log
log_level = logging.DEBUG

# Configuração do logger
logger = logging.getLogger()
logger.setLevel(log_level)
logger.addHandler(log_handler)


bot = telebot.TeleBot(TOKEN)


# Dicionário para armazenar o estado do usuário
user_state = {} # Rastreia se o usuário já enviou a data ou código key no processo de reset de senha
conversation_state = {} # Utilizado para rastrear se o usuário já inciou um atendimento ou não, se não iniciou, o message handler com message:True entra em ação
last_state = {} # Dicionário para rastrear a última interação de cada usuário

# Função para verificar a inatividade de um usuário
def verificar_inatividade():
    limite_inatividade1 = 300  # Tempo em segundos após o qual um usuário é considerado inativo
    limite_inatividade2 = 600 
    while True:
        for chat_id, timestamp in list(last_state.items()):# Primeira leitura
            if time.time() - timestamp > limite_inatividade1: # Usuário inativo level 1
                msg1 = 'Você ainda está aí?'
                bot.send_message(chat_id, msg1)
                time.sleep(30)
        for chat_id, timestamp in list(last_state.items()):# Segunda leitura
            if time.time() - timestamp > limite_inatividade2: # Usuário inativo level 2
                msg2 ='Como não houve mais interação, estou encerrando nossa conversa. Você pode me chamar a qualquer momento se precisar! 😁👋'
                bot.send_message(chat_id, msg2)
                if chat_id in conversation_state:
                    del conversation_state[chat_id]
                if chat_id in user_state:
                    del user_state[chat_id]
                del last_state[chat_id]

        time.sleep(60) # Verifica a cada 300 segundos se o usuário está inativo... 


### ---------------------- MESSAGE HANDLER START POINT -------------------------------------------### 
@bot.message_handler(commands=['start', 'inicio'])
def start_message(message):
    chat_id = message.chat.id
    user_firstname = message.from_user.first_name     
    last_state[chat_id] = time.time()   
    if conversation_state.get(chat_id) is None or conversation_state.get(chat_id) == 'menu_start': # Aqui eu testo pra ver se ele já não passou por aqui quando ele usa o /inicio
        conversation_state[chat_id]='menu_start'
        msg = 'Olá! 👋 Eu sou o Tom, o chatbot da Clear CFTV. Posso te ajudar em algumas coisas, mas antes preciso que você aceite nossa política de privacidade que\
 pode ser encontrada [aqui](https://www.clearcftv.com.br/pol%C3%ADtica-de-privacidade).'

        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        custom_keyboard = [InlineKeyboardButton('Aceito', callback_data='callback_start'),
                        InlineKeyboardButton('Não aceito', callback_data='callback_privacidade_negada')]
        
        markup.add(custom_keyboard[0], custom_keyboard[1])

        bot.send_message(chat_id, msg, parse_mode='Markdown', reply_markup=markup, disable_web_page_preview= True)
    else:
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        custom_keyboard = [InlineKeyboardButton('Reiniciar atendimento', callback_data='callback_start')]
        
        markup.add(custom_keyboard[0])
        msg = 'Clique no botão para recomeçar ou envie /sair para encerrar o atendimento'
        bot.send_message(chat_id, msg, parse_mode='Markdown', reply_markup=markup, disable_web_page_preview= True)

### ---------------------- MESSAGE HANDLER COMERCIAL VEICULAR -------------------------------------------### 
@bot.message_handler(commands=['veicular'])
def veicular(message):  
    chat_id = message.chat.id
    conversation_state[chat_id]='comercial_veicular'
    last_state[chat_id] = time.time()
    bot.send_message(message.chat.id, 'Aqui vai um [vídeo](https://www.youtube.com/watch?v=SqESxWL17bQ) para você conhecer mais sobre nossa linha veicular: ', parse_mode='Markdown')
    bot.send_message(message.chat.id, 'Para receber nosso Catálogo, me envie\n/catalogoveicular, ou clique no comando que eu envio para você... ')
    bot.send_message(message.chat.id, 'Se desejar encerrar seu atendimento, digite /sair ou se quiser retornar ao início, digite /incio')

@bot.message_handler(commands=['catalogoveicular'])
def catalogoveicular(message):  
    chat_id = message.chat.id  
    last_state[chat_id] = time.time()
    bot.send_message(message.chat.id, 'Ok! Um momento... ')
    with open('media/veicular/docs/CatalogoVeicular.pdf', 'rb') as catalogo_veicular:
        bot.send_document(message.chat.id,catalogo_veicular, caption='Aqui está!')
    bot.send_message(message.chat.id, 'Se desejar encerrar seu atendimento, digite /sair ou se quiser retornar ao início, digite /inicio')
    
### ---------------------- MESSAGE HANDLER COMERCIAL CFTV -------------------------------------------### 

@bot.message_handler(commands=['cftv','CFTV'])
def cftv(message):
    chat_id = message.chat.id
    conversation_state[chat_id] = 'comercial_cftv'
    last_state[chat_id] = time.time()
    bot.send_message(chat_id, 'Vou te encaminhar nosso catálogo de produtos para você conhecer nossas novidades...')
    with open('media/cftv/docs/catalogo_cftv.pdf','rb') as catalogo_cftv:
        bot.send_document(chat_id, catalogo_cftv, caption='Aqui está! Se tiver dúvidas, entre em contato com nossos consultores, será um prazer te ajudar...')
    bot.send_message(chat_id, 'Se desejar encerrar seu atendimento, digite /sair ou se quiser retornar ao início, digite /inicio')

### ---------------------- MESSAGE HANDLER RESET DE SENHA -------------------------------------------### 

@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == 'esperando_cpf')
def esperando_cpf(message):
    chat_id = message.chat.id
    user_input = message.text
    user_firstname = message.from_user.first_name
    last_state[chat_id] = time.time()
    cpf = user_input
    cpf = cpf_check(cpf)
    if cpf is False:
        markup = InlineKeyboardMarkup()
        button = InlineKeyboardButton('Tentar novamente', callback_data='callback_cpf')
        markup.add(button)
        bot.send_message(chat_id, 'CPF inválido!', reply_markup= markup)
    else:
        markup = InlineKeyboardMarkup()
        button = InlineKeyboardButton('Continuar', callback_data='callback_reset_de_senha')
        markup.add(button)
        bot.send_message(chat_id,f'Ótimo, {user_firstname}! Clique no botão abaixo para continuar: ', reply_markup=markup)

@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == 'esperando_key')
def handle_key(message):
    chat_id = message.chat.id
    conversation_state[chat_id]='resetando_senha'
    last_state[chat_id] = time.time()
    chat_id = message.chat.id
    user_input = message.text
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    custom_keyboard = [InlineKeyboardButton('Reiniciar atendimento', callback_data='callback_cftv'), InlineKeyboardButton('Novo reset', callback_data='callback_reset_de_senha')]
    markup.add(custom_keyboard[0], custom_keyboard[1])
    try:
        key = int(user_input)
        senha = ResetXiongmaiDate(key, 'key')
        if senha != 'Lamento, mas o servidor de reset de senha está indisponível no momento... Aguarde alguns minutos e tente novamente...':
            bot.send_message(chat_id, f'Aqui está: {senha}')
            bot.send_message(chat_id, 'Insira a senha acima no seu DVR. Em seguida, aguarde. Após o procedimento, a senha será nula (em branco)', reply_markup=markup)
            bot.send_message(chat_id, 'Se desejar encerrar seu atendimento clique aqui 👉 /sair')
        else:
            bot.send_message(chat_id, f'{senha}')
            bot.send_message(chat_id, 'Se desejar encerrar seu atendimento clique aqui 👉 /sair')

    except ValueError:
        bot.send_message(chat_id, 'Não foi possível entender o que você escreveu. Tente novamente clicando no botão "Reset de Senha" e verifique se digitou corretamente.')
        bot.send_message(chat_id, 'Se desejar encerrar seu atendimento clique aqui 👉 /sair')
    user_state.pop(chat_id)  # Remova o estado do usuário após a conclusão

@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == 'esperando_data')
def handle_data(message):
    chat_id = message.chat.id
    user_input = message.text
    last_state[chat_id] = time.time()
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    custom_keyboard = [InlineKeyboardButton('Reiniciar atendimento', callback_data='callback_cftv'), InlineKeyboardButton('Novo reset', callback_data='callback_reset_de_senha')]
    markup.add(custom_keyboard[0], custom_keyboard[1])
    try:
        data = int(user_input)
        senha = ResetXiongmaiDate(data, 'date')
        if senha != 'Lamento, mas o servidor de reset de senha está indisponível no momento... Aguarde alguns minutos e tente novamente...':
            bot.send_message(chat_id, f'Aqui está: {senha}')
            bot.send_message(chat_id, 'Insira a senha acima no seu DVR e lembre-se de respeitar letras maísuculas e minúsculas. Em seguida, aguarde. Após o procedimento, a senha será nula (em branco)', reply_markup=markup)
            bot.send_message(chat_id, 'Se desejar encerrar seu atendimento clique aqui 👉 /sair')
        else:
            bot.send_message(chat_id, f'{senha}')
            bot.send_message(chat_id, 'Se desejar encerrar seu atendimento clique aqui 👉 /sair')
    except ValueError:
        bot.send_message(chat_id, 'Não foi possível entender o que você escreveu. Tente novamente clicando no botão "Reset de Senha" e verifique se digitou corretamente.')
        bot.send_message(chat_id, 'Se desejar encerrar seu atendimento clique aqui 👉 /sair')
    del user_state[chat_id]  # Remova o estado do usuário após a conclusão

### ---------------------- MESSAGE HANDLER COMANDOS GERAIS -------------------------------------------### 

@bot.message_handler(commands =['especialista'])
def especialista(message):
    chat_id = message.chat.id
    conversation_state[chat_id] = 'especialista'
    last_state[chat_id] = time.time()
    msg = 'No momento, você pode falar com um de nossos especialistas através do nosso WhatsApp oficial do Suporte Técnico clicando [aqui](wa.me/+553534734043).\nLembre-se que nossos especialistas estão disponíveis\
 de *segunda à sexta das 08:00 às 18:00*.'
    bot.send_message(chat_id, msg, parse_mode='Markdown', disable_web_page_preview= True)

@bot.message_handler(commands=['ajuda'])
def ajuda(message):
    chat_id = message.chat.id
    conversation_state[chat_id] = 'ajuda'
    last_state[chat_id] = time.time()
    reply = InlineKeyboardMarkup()
    custom_keyboard = [InlineKeyboardButton('Reset por data', callback_data='callback_reset_data'),
                      InlineKeyboardButton('Reset por código key', callback_data='callback_reset_key')]
    reply.add(custom_keyboard[0], custom_keyboard[1])
    with open('media/cftv/imgs/key.png', 'rb') as photo:
        bot.send_photo(chat_id, photo,'Se seu DVR tiver este símbolo -> ❓  então selecione a opção [Código Key]. Caso não tenha, selecione a opção [Reset por Data]', reply_markup=reply)

@bot.message_handler(commands=['sair'])
def sair(message):
    chat_id = message.chat.id
    last_state[chat_id] = time.time()
    user_firstname = message.from_user.first_name  # Usar user_firstname em vez de user_first_name
    if chat_id in conversation_state:
        del conversation_state[chat_id]
    if chat_id in user_state:
        del user_state[chat_id]
    bot.send_message(chat_id, f'Espero ter te ajudado! Até breve, {user_firstname} 👋')

### ---------------------- CALLBACKS POLÍTICA DE PRIVACIDADE -------------------------------------------### 

@bot.callback_query_handler(func=lambda call: call.data == 'callback_start')
def callback_start(call):
    chat_id = call.message.chat.id
    conversation_state[chat_id] = 'privacidade_aceita'
    last_state[chat_id] = time.time()
    msg = 'Obrigado! Agora, escolha que tipo de atendimento você deseja:'
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    custom_keyboard = [InlineKeyboardButton('Atendimento Comercial', callback_data='callback_comercial'),
                       InlineKeyboardButton('Suporte Técnico', callback_data='callback_suporte')]
    
    markup.add(custom_keyboard[0], custom_keyboard[1])

    bot.send_message(chat_id, msg, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'callback_privacidade_negada')
def callback_privacidade_negada(call):
    chat_id = call.message.chat.id
    last_state[chat_id] = time.time()
    msg = 'Lamento mas não posso dar sequência no seu atendimento sem que aceite nossos termos.'
    msg2 = 'Espero poder te ajudar em breve 👋'
    if chat_id in conversation_state:
        del conversation_state[chat_id]
    if chat_id in user_state:
        del user_state[chat_id]
    bot.send_message(chat_id, msg)
    bot.send_message(chat_id, msg2)

### ---------------------- CALLBACK COMERCIAL ------------------------------------------------### 
@bot.callback_query_handler(func=lambda call: call.data == 'callback_comercial')
def callback_comercial(call):
    chat_id = call.message.chat.id
    conversation_state[chat_id] = 'callback_comercial'
    last_state[chat_id] = time.time()
    user_firstname = call.from_user.first_name
    msg = f'{user_firstname}, aqui vai algumas opções que posso fazer por você:\n\n\
☎️ - Fale conosco: 3534734000\n\
🚛 - Conheça nossa linha /veicular\n\
🎥 - Conheça nossa linha /CFTV\n\
💻 - Acesse nosso [site](www.clearcftv.com.br)👇\n\n\
                             '
   
    bot.send_message(chat_id, msg, parse_mode='Markdown')
    msg2 = 'Se precisar retornar, digite /inicio para voltar.'
    bot.send_message(chat_id, msg2, disable_web_page_preview= True)
### ---------------------- CALLBACK SUPORTE TÉCNICO -------------------------------------------### 
@bot.callback_query_handler(func=lambda call: call.data == 'callback_suporte')
def callback_suporte(call):
    chat_id = call.message.chat.id
    conversation_state[chat_id]='callback_suporte'
    last_state[chat_id] = time.time()
    msg = "Vejo que você precisa de ajuda com nossos produtos.\nSelecione a vertical de produtos que precisa de suporte. 👇"
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    custom_keyboard = [InlineKeyboardButton('Veicular', callback_data='callback_veicular'),
                       InlineKeyboardButton('CFTV', callback_data='callback_cftv'),
                       InlineKeyboardButton('Voltar ↩️', callback_data='callback_start')]
    
    markup.add(custom_keyboard[0], custom_keyboard[1],custom_keyboard[2])

    bot.send_message(chat_id, msg, reply_markup=markup)

### ----------------------------------- SUPORTE VEICULAR -----------------------------------------### 

@bot.callback_query_handler(func=lambda call: call.data == 'callback_veicular')
def callback_veicular(call):
    chat_id = call.message.chat.id
    conversation_state[chat_id] = 'callback_veicular'
    last_state[chat_id] = time.time()
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    custom_keyboard = [InlineKeyboardButton('MDVR', callback_data='callback_mdvr'), InlineKeyboardButton('Software IVMS', callback_data='callback_ivms'),
                       InlineKeyboardButton('Contador de Passageiros', callback_data='callback_contador_pessoas'), InlineKeyboardButton('Câmeras AHD', callback_data='callback_cam_ahd'),
                       InlineKeyboardButton('Câmeras IP', callback_data='callback_cam_ipc_veicular'), InlineKeyboardButton('Voltar ↩️  ', callback_data='callback_suporte')]
    markup.add(custom_keyboard[0],custom_keyboard[1],custom_keyboard[2],custom_keyboard[3],custom_keyboard[4],custom_keyboard[5])
    msg = 'Sobre qual produto você precisa de ajuda?'
    bot.send_message(chat_id, msg, reply_markup=markup)
    
### ---------------------------------------- CALLBACK SUPORTE MDVR ----------------------------------###

@bot.callback_query_handler(func=lambda call: call.data == 'callback_mdvr')
def callback_mdvr(call):
    chat_id = call.message.chat.id
    conversation_state[chat_id] = 'callback_mdvr'
    last_state[chat_id] = time.time()
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    custom_keyboard = [InlineKeyboardButton('CL14GS', callback_data='callback_cl14'), InlineKeyboardButton('Plus', callback_data='callback_plus'), 
                       InlineKeyboardButton('Max (Sensor de Fadiga)', callback_data='callback_max'),InlineKeyboardButton('Voltar ↩️', callback_data='callback_veicular')]
    markup.add(custom_keyboard[0],custom_keyboard[1],custom_keyboard[2], custom_keyboard[3])
    msg = 'Entendido! Qual modelo de MDVR você precisa de suporte?'
    bot.send_message(chat_id, msg, reply_markup=markup)

### CL14
@bot.callback_query_handler(func=lambda call: call.data == 'callback_cl14')
def callback_cl14(call):
    chat_id = call.message.chat.id
    conversation_state[chat_id] = 'callback_cl14'
    last_state[chat_id] = time.time()
    msg = 'Aqui está algumas coisas que posso te ajudar:\n\
🎥[Vídeo 1](https://www.youtube.com/channel/UC3gHVQQ-SFIkprT1wxC_50w)\n\
🎥[Vídeo 2](https://www.youtube.com/channel/UC3gHVQQ-SFIkprT1wxC_50w)\n\
🎥[Vídeo 3](https://www.youtube.com/channel/UC3gHVQQ-SFIkprT1wxC_50w)\n\
📄[Clique aqui](https://futurae.notion.site/DVR-Veicular-CL14GSD-f8bb461f91294d2f9816d99240f669af) para acessar a página de documentação completa do produto \n\
Se não encontrou o que procura, fale com nosso /especialista'
    markup = InlineKeyboardMarkup()
    custom_keyboard = [InlineKeyboardButton('Voltar ↩️', callback_data='callback_mdvr')]
    markup.add(custom_keyboard[0])
    bot.send_message(chat_id, msg, reply_markup=markup, parse_mode='Markdown')

### PLUS
@bot.callback_query_handler(func=lambda call: call.data == 'callback_plus')
def callback_plus(call):
    chat_id = call.message.chat.id
    conversation_state[chat_id] = 'callback_plus'
    last_state[chat_id] = time.time()
    msg = 'Aqui está algumas coisas que posso te ajudar:\n\
🎥[Vídeo 1](https://www.youtube.com/channel/UC3gHVQQ-SFIkprT1wxC_50w)\n\
🎥[Vídeo 2](https://www.youtube.com/channel/UC3gHVQQ-SFIkprT1wxC_50w)\n\
🎥[Vídeo 3](https://www.youtube.com/channel/UC3gHVQQ-SFIkprT1wxC_50w)\n\
📄[Clique aqui](https://futurae.notion.site/DVR-Veicular-PLUS-799387300af944d98a10dcbfea082c29) para acessar a página de documentação completa do produto \n\
Se não encontrou o que procura, fale com nosso /especialista'
    markup = InlineKeyboardMarkup()
    custom_keyboard = [InlineKeyboardButton('Voltar ↩️', callback_data='callback_mdvr')]
    markup.add(custom_keyboard[0])
    bot.send_message(chat_id, msg, reply_markup=markup, parse_mode='Markdown', disable_web_page_preview= True)

### MAX - SENSOR DE FADIGA
@bot.callback_query_handler(func=lambda call: call.data == 'callback_max')
def callback_max(call):
    chat_id = call.message.chat.id
    conversation_state[chat_id] = 'callback_max'
    last_state[chat_id] = time.time()
    msg = 'Aqui está algumas coisas que posso te ajudar:\n\
🎥[Vídeo 1](https://www.youtube.com/channel/UC3gHVQQ-SFIkprT1wxC_50w)\n\
🎥[Vídeo 2](https://www.youtube.com/channel/UC3gHVQQ-SFIkprT1wxC_50w)\n\
🎥[Vídeo 3](https://www.youtube.com/channel/UC3gHVQQ-SFIkprT1wxC_50w)\n\n\
📄[Clique aqui](https://futurae.notion.site/DVR-Veicular-MAX-efa46e82a7d94a78acde07dca82eaf77?pvs=4) para acessar a página de documentação completa do produto!\n\n\
Se não encontrou o que procura, fale com nosso /especialista'
    markup = InlineKeyboardMarkup()
    custom_keyboard = [InlineKeyboardButton('Download do app de calibração', callback_data='callback_icalibration'),InlineKeyboardButton('Voltar ↩️', callback_data='callback_mdvr')]
    markup.max_row_keys=1
    markup.add(custom_keyboard[0], custom_keyboard[1])
    bot.send_message(chat_id, msg, reply_markup=markup, parse_mode='Markdown', disable_web_page_preview= True)

@bot.callback_query_handler(func=lambda call: call.data == 'callback_icalibration')
def callback_icalibration(call):
    chat_id = call.message.chat.id
    conversation_state[chat_id] = 'callback_icalibration'
    last_state[chat_id] = time.time()
    msg=' [Clique aqui para fazer o download](https://drive.google.com/file/d/15HvPpvi7X-oQv4fXMHBm-eNPRypK1FVW/view?usp=sharing)\n\n\
Caso não saiba como instalar um aplicativo com a extensão .apk [clique aqui](https://www.youtube.com/watch?v=b5D6zwkQKd4)'
    markup = InlineKeyboardMarkup()
    custom_keyboard = [InlineKeyboardButton('Voltar ↩️', callback_data='callback_max')]
    markup.add(custom_keyboard[0])
    bot.send_message(chat_id, msg, reply_markup=markup, parse_mode='Markdown', disable_web_page_preview= True)

### ---------------------------------------- CALLBACK SUPORTE IVMS ----------------------------------###
@bot.callback_query_handler(func=lambda call: call.data == 'callback_ivms')
def callback_ivms(call):
    chat_id = call.message.chat.id
    conversation_state[chat_id] = 'callback_ivms'
    last_state[chat_id] = time.time()
    msg = 'Aqui está algumas coisas que posso te ajudar:\n\
📲[Download App de Monitoramento](https://play.google.com/store/apps/details?id=com.icarvisions.iCarView&pcampaignid=web_share)\n\
📁[Central de Downloads](https://www.clearcftv.com.br/downloads)\n\
🎥[Treinamento Gestão de Frotas - App iCarview](https://youtube.com/playlist?list=PLERfymRp0uqk23J9l9fOsNLG0WAu5yMVa&si=k99OgarTRs4bjspe)\n\
🎥[Treinamento Gestão de Frotas com IVMS Client](https://youtube.com/playlist?list=PLERfymRp0uqlTObi_hJAvS3030DkRZFNW&si=MRDwHFn6mESc3kdf)\n\
📄\n\n\
Se não encontrou o que procura, fale com nosso /especialista'
    markup = InlineKeyboardMarkup()
    custom_keyboard = [InlineKeyboardButton('Voltar ↩️', callback_data='callback_veicular')]
    markup.add(custom_keyboard[0])
    bot.send_message(chat_id, msg, reply_markup=markup, parse_mode='Markdown', disable_web_page_preview= True)

### ---------------------------------------- CALLBACK CONTADOR  ----------------------------------###
@bot.callback_query_handler(func=lambda call: call.data == 'callback_contador_pessoas')
def callback_contador_pessoas(call):
    chat_id = call.message.chat.id
    conversation_state[chat_id] = 'callback_contador_pessoas'
    last_state[chat_id] = time.time()
    msg = 'Aqui está algumas coisas que posso te ajudar:\n\
🎥[Vídeo 1](https://www.youtube.com/channel/UC3gHVQQ-SFIkprT1wxC_50w)\n\
🎥[Vídeo 2](https://www.youtube.com/channel/UC3gHVQQ-SFIkprT1wxC_50w)\n\
🎥[Vídeo 3](https://www.youtube.com/channel/UC3gHVQQ-SFIkprT1wxC_50w)\n\
Se não encontrou o que procura, fale com nosso /especialista'
    markup = InlineKeyboardMarkup()
    custom_keyboard = [InlineKeyboardButton('Voltar ↩️', callback_data='callback_veicular')]
    markup.add(custom_keyboard[0])
    bot.send_message(chat_id, msg, reply_markup=markup, parse_mode='Markdown', disable_web_page_preview= True)

### ---------------------------------------- CALLBACK CAM AHD  ----------------------------------###
@bot.callback_query_handler(func=lambda call: call.data == 'callback_cam_ahd')
def callback_cam_ahd(call):
    chat_id = call.message.chat.id
    conversation_state[chat_id] = 'callback_cam_ahd'
    last_state[chat_id] = time.time()
    msg = 'Aqui está algumas coisas que posso te ajudar:\n\
🎥[Vídeo 1](https://www.youtube.com/channel/UC3gHVQQ-SFIkprT1wxC_50w)\n\
🎥[Vídeo 2](https://www.youtube.com/channel/UC3gHVQQ-SFIkprT1wxC_50w)\n\
🎥[Vídeo 3](https://www.youtube.com/channel/UC3gHVQQ-SFIkprT1wxC_50w)\n\
Se não encontrou o que procura, fale com nosso /especialista'
    markup = InlineKeyboardMarkup()
    custom_keyboard = [InlineKeyboardButton('Voltar ↩️', callback_data='callback_veicular')]
    markup.add(custom_keyboard[0])
    bot.send_message(chat_id, msg, reply_markup=markup, parse_mode='Markdown', disable_web_page_preview= True)

### ---------------------------------------- CALLBACK CAM IPC VEICULAR  ----------------------------------###
@bot.callback_query_handler(func=lambda call: call.data == 'callback_ipc_veicular')
def callback_ipc_veicular(call):
    chat_id = call.message.chat.id
    last_state[chat_id] = time.time()
    conversation_state[chat_id] = 'callback_ipc_veicular'
    msg = 'Aqui está algumas coisas que posso te ajudar:\n\
🎥[Vídeo 1](https://www.youtube.com/channel/UC3gHVQQ-SFIkprT1wxC_50w)\n\
🎥[Vídeo 2](https://www.youtube.com/channel/UC3gHVQQ-SFIkprT1wxC_50w)\n\
🎥[Vídeo 3](https://www.youtube.com/channel/UC3gHVQQ-SFIkprT1wxC_50w)\n\
Se não encontrou o que procura, fale com nosso /especialista'
    markup = InlineKeyboardMarkup()
    custom_keyboard = [InlineKeyboardButton('Voltar ↩️', callback_data='callback_veicular')]
    markup.add(custom_keyboard[0])
    bot.send_message(chat_id, msg, reply_markup=markup, parse_mode='Markdown', disable_web_page_preview= True)

### ------------------------------------- SUPORTE CFTV ------------------------------------------- ### 

@bot.callback_query_handler(func=lambda call: call.data == 'callback_cftv')
def callback_cftv(call):
    chat_id = call.message.chat.id
    conversation_state[chat_id] = 'callback_cftv'
    last_state[chat_id] = time.time()
    reply = InlineKeyboardMarkup()
    custom_keyboard = [InlineKeyboardButton('Reset de Senha', callback_data='callback_cpf'),
                      InlineKeyboardButton('Dúvidas Gerais', callback_data='callback_duvidas_gerais'),
                      InlineKeyboardButton('Voltar ↩️', callback_data='callback_suporte')]
    reply.add(custom_keyboard[0], custom_keyboard[1], custom_keyboard[2])
    msg = f'Perfeito! Aqui vão algumas opções disponíveis pra você:'
    bot.send_message(chat_id, msg, reply_markup=reply, disable_web_page_preview= True)

### ---------------------- CALLBACKS RESET DE SENHA -------------------------------------------### 

@bot.callback_query_handler(func=lambda call: call.data == 'callback_cpf')
def callback_cpf(call):
    chat_id = call.message.chat.id
    last_state[chat_id] = time.time()
    msg = 'Digite seu CPF (Apenas Números)'
    bot.send_message(chat_id, msg, parse_mode='Markdown')
    user_state[chat_id] = 'esperando_cpf'
    #esperando_cpf(call.message)

@bot.callback_query_handler(func=lambda call: call.data == 'callback_reset_de_senha')
def callback_reset_de_senha(call):
    chat_id = call.message.chat.id
    last_state[chat_id] = time.time()
    reply = InlineKeyboardMarkup()
    custom_keyboard = [InlineKeyboardButton('Reset por data', callback_data='callback_reset_data'),
                      InlineKeyboardButton('Reset por código key', callback_data='callback_reset_key')]
    reply.add(custom_keyboard[0], custom_keyboard[1])
    msg = f'Atualmente, eu só consigo realizar o reset de senha dos DVRs da linha Xmeye. Caso seja o seu modelo, escolha o método de reset de senha 👇'
    msg2 = 'Se não souber qual método usar, me mande um /ajuda ou clique no comando que eu te mostro...'
    bot.send_message(chat_id, msg, reply_markup=reply)
    bot.send_message(chat_id, msg2)

@bot.callback_query_handler(func=lambda call: call.data == 'callback_reset_data')
def callback_reset_data(call):
    chat_id = call.message.chat.id
    last_state[chat_id] = time.time()
    conversation_state[chat_id] = 'callback_reset_data'

    # Verifique se o usuário já forneceu a data anteriormente
    if user_state.get(chat_id) == 'esperando_data':
        bot.send_message(chat_id, 'Você já enviou a data. Aguarde uma resposta.')
    else:
        bot.send_message(chat_id, 'Envie a data que está sendo exibida na tela do *equipamento* no formato AAAAMMDD e aguarde alguns instantes...', parse_mode='Markdown')
        bot.send_message(chat_id, '*Exemplo*: Se a data informada é `14/09/2023`, digite: `20230914`', parse_mode='Markdown')
        user_state[chat_id] = 'esperando_data'

@bot.callback_query_handler(func=lambda call: call.data == 'callback_reset_key')
def callback_reset_key(call):
    chat_id = call.message.chat.id
    last_state[chat_id] = time.time()
    conversation_state[chat_id]  = 'callback_reset_key'

    # Verifique se o usuário já forneceu a data anteriormente
    if user_state.get(chat_id) == 'esperando_key':
        bot.send_message(chat_id, 'Você já enviou o código key. Aguarde uma resposta.')
    else:
        bot.send_message(chat_id, 'Envie o código Key que está sendo exibido na tela e aguarde alguns instantes...')
        user_state[chat_id] = 'esperando_key'

@bot.callback_query_handler(func=lambda call: call.data == 'callback_duvidas_gerais')
def callback_duvidas_gerais(call):
    
    chat_id = call.message.chat.id
    last_state[chat_id] = time.time()
    conversation_state[chat_id] = 'callback_duvidas_gerais'
    msg = 'Agora, preciso saber de qual produto estamos falando.'
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    custom_keyboard = [InlineKeyboardButton('DVR', callback_data='callback_duvida_dvr'),
                       InlineKeyboardButton('Câmeras Analógicas', callback_data='callback_cam_analog'),
                       InlineKeyboardButton('NVR', callback_data='callback_nvr'),
                       InlineKeyboardButton('Câmeras IP', callback_data='callback_ipc_cftv')]
    
    markup.add(custom_keyboard[0], custom_keyboard[1], custom_keyboard[2], custom_keyboard[3])
    bot.send_message(chat_id, msg, reply_markup=markup)

### ---------------------- CALLBACKS DVR ANALÓGICOS -------------------------------------------### 
### ESCOLHA QUAL DVR
@bot.callback_query_handler(func=lambda call: call.data == 'callback_duvida_dvr')
def callback_duvida_dvr(call):
    chat_id = call.message.chat.id
    conversation_state[chat_id] = 'callback_duvida_dvr'
    last_state[chat_id] = time.time()
    msg = 'Entendido! A Clear CFTV, possui mais de um modelo de DVR.'
    msg2 = 'Segue uma foto que vai te ajudar a você descobrir qual modelo é o seu:'
    msg3 = 'Escolha qual modelo é o seu. Se não encontrar, não se preocupe, você pode falar com nossos especialistas me enviando um /especialista a qualquer momento...'
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    custom_keyboard = [InlineKeyboardButton('DVR', callback_data='callback_dvr'),
                       InlineKeyboardButton('HVR', callback_data='callback_hvr'),
                       InlineKeyboardButton('XVR', callback_data='callback_xvr')]
    markup.add(custom_keyboard[0], custom_keyboard[1], custom_keyboard[2])
    bot.send_message(chat_id, msg)
    with open ('media/cftv/imgs/dvrs.png', 'rb') as photo:
        bot.send_photo(chat_id, photo, msg2)
    bot.send_message(chat_id, msg3, reply_markup=markup)

### DVR
@bot.callback_query_handler(func=lambda call: call.data == 'callback_dvr')
def callback_dvr(call):
    chat_id = call.message.chat.id
    conversation_state[chat_id] = 'callback_dvr'
    last_state[chat_id] = time.time()
    msg = 'Aqui está algumas coisas que posso te ajudar:\n\
📲[Download App Acesso Remoto](https://play.google.com/store/apps/details?id=com.mobile.myeye&pcampaignid=web_share)\n\
🌐[Configuração Básica de Rede]()\n\n\
Se não encontrou o que procura, fale com nosso /especialista'
    markup = InlineKeyboardMarkup()
    custom_keyboard = [InlineKeyboardButton('Voltar ↩️', callback_data='callback_duvidas_gerais')]
    markup.add(custom_keyboard[0])
    bot.send_message(chat_id, msg, reply_markup=markup, parse_mode='Markdown', disable_web_page_preview= True)


### HVR
@bot.callback_query_handler(func=lambda call: call.data == 'callback_hvr')
def callback_hvr(call):
    chat_id = call.message.chat.id
    conversation_state[chat_id] = 'callback_hvr'
    last_state[chat_id] = time.time()
    msg = 'Aqui está algumas coisas que posso te ajudar:\n\
🎥[Adicionando um usuário](https://www.youtube.com/watch?v=zT2Y3gQq2Jk)\n\
🎥[Acesso Remoto](https://www.youtube.com/watch?v=HxsZY7kpSUc)\n\
🎥[Configurando Detecção de Movimento](https://www.youtube.com/watch?v=OMWv4yWe_pg))\n\
Se não encontrou o que procura, fale com nosso /especialista'
    markup = InlineKeyboardMarkup()
    custom_keyboard = [InlineKeyboardButton('Voltar ↩️', callback_data='callback_duvidas_gerais')]
    markup.add(custom_keyboard[0])
    bot.send_message(chat_id, msg, reply_markup=markup, parse_mode='Markdown', disable_web_page_preview= True)

### XVR
@bot.callback_query_handler(func=lambda call: call.data == 'callback_xvr')
def callback_xvr(call):
    chat_id = call.message.chat.id
    conversation_state[chat_id] = 'callback_xvr'
    last_state[chat_id] = time.time()
    msg = 'Aqui está algumas coisas que posso te ajudar:\n\
🎥[Vídeo 1](https://www.youtube.com/channel/UC3gHVQQ-SFIkprT1wxC_50w)\n\
🎥[Vídeo 2](https://www.youtube.com/channel/UC3gHVQQ-SFIkprT1wxC_50w)\n\
🎥[Vídeo 3](https://www.youtube.com/channel/UC3gHVQQ-SFIkprT1wxC_50w)\n\
Se não encontrou o que procura, fale com nosso /especialista'
    markup = InlineKeyboardMarkup()
    custom_keyboard = [InlineKeyboardButton('Voltar ↩️', callback_data='callback_duvidas_gerais')]
    markup.add(custom_keyboard[0])
    bot.send_message(chat_id, msg, reply_markup=markup, parse_mode='Markdown', disable_web_page_preview= True)


### ---------------------- CALLBACKS CAM ANALÓGICA -------------------------------------------### 

@bot.callback_query_handler(func=lambda call: call.data == 'callback_cam_analog')
def callback_cam_analog(call):
    chat_id = call.message.chat.id
    conversation_state[chat_id] = 'callback_cam_analog'
    last_state[chat_id] = time.time()
    msg = 'Aqui está algumas coisas que posso te ajudar:\n\
🎥[Vídeo 1](https://www.youtube.com/channel/UC3gHVQQ-SFIkprT1wxC_50w)\n\
🎥[Vídeo 2](https://www.youtube.com/channel/UC3gHVQQ-SFIkprT1wxC_50w)\n\
🎥[Vídeo 3](https://www.youtube.com/channel/UC3gHVQQ-SFIkprT1wxC_50w)\n\
Se não encontrou o que procura, fale com nosso /especialista'
    markup = InlineKeyboardMarkup()
    custom_keyboard = [InlineKeyboardButton('Voltar ↩️', callback_data='callback_duvidas_gerais')]
    markup.add(custom_keyboard[0])
    bot.send_message(chat_id, msg, reply_markup=markup, parse_mode='Markdown', disable_web_page_preview= True)


### ---------------------- CALLBACKS NVR -----------------------------------------------------### 

@bot.callback_query_handler(func=lambda call: call.data == 'callback_nvr')
def callback_nvr(call):
    chat_id = call.message.chat.id
    conversation_state[chat_id] = 'callback_nvr'
    last_state[chat_id] = time.time()
    msg = 'Aqui está algumas coisas que posso te ajudar:\n\
🎥[Vídeo 1](https://www.youtube.com/channel/UC3gHVQQ-SFIkprT1wxC_50w)\n\
🎥[Vídeo 2](https://www.youtube.com/channel/UC3gHVQQ-SFIkprT1wxC_50w)\n\
🎥[Vídeo 3](https://www.youtube.com/channel/UC3gHVQQ-SFIkprT1wxC_50w)\n\
Se não encontrou o que procura, fale com nosso /especialista'
    markup = InlineKeyboardMarkup()
    custom_keyboard = [InlineKeyboardButton('Voltar ↩️', callback_data='callback_duvidas_gerais')]
    markup.add(custom_keyboard[0])
    bot.send_message(chat_id, msg, reply_markup=markup, parse_mode='Markdown', disable_web_page_preview= True)

### ---------------------- CALLBACKS IPC -----------------------------------------------------### 

@bot.callback_query_handler(func=lambda call: call.data == 'callback_ipc_cftv')
def callback_ipc_cftv(call):
    chat_id = call.message.chat.id
    conversation_state[chat_id] = 'callback_ipc_cftv'
    last_state[chat_id] = time.time()
    msg = 'Aqui está algumas coisas que posso te ajudar:\n\
💻[Software para encontrar câmera na rede (Opção 1)](https://drive.google.com/file/d/1T--VmNSxp3PYGYI3Ar-q4zleAvnQFLpj/view?usp=sharing)\n\n\
Se não encontrou o que procura, fale com nosso /especialista'
    markup = InlineKeyboardMarkup()
    custom_keyboard = [InlineKeyboardButton('Voltar ↩️', callback_data='callback_duvidas_gerais')]
    markup.add(custom_keyboard[0])
    bot.send_message(chat_id, msg, reply_markup=markup, parse_mode='Markdown', disable_web_page_preview= True)

### --------------------- ECHO MESSAGE HANDLER----------------------------------------------- ###

@bot.message_handler(func=lambda message: True)
def echo_message(message):
    chat_id = message.chat.id
    user_name = message.from_user.first_name 
    if conversation_state.get(chat_id) is None:
        bot.reply_to(message, f'Olá {user_name}! Digite /start para começar seu atendimento!')
        conversation_state[chat_id] = "menu_start"
        last_state[chat_id] = time.time()

    elif conversation_state.get(chat_id) is not None:
        # Não faça nada quando a conversa está em andamento
        last_state[chat_id] = time.time()
        pass
    else:
        # Lidere com mensagens quando a conversa não está em andamento
        pass

# Inicie a verificação de inatividade em segundo plano
inatividade_thread = threading.Thread(target=verificar_inatividade)
inatividade_thread.daemon = True
inatividade_thread.start()

# Inicie o bot
bot.infinity_polling()
