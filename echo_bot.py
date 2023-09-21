import telebot
import logging
from reset_senha import ResetXiongmaiDate
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

# Carregar o token a partir de um arquivo de configuração externo
with open('config.txt', "r") as config_file:
    TOKEN = config_file.read().strip()

# Informações de log
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)  # Outputs debug messages to console.

bot = telebot.TeleBot(TOKEN)

# Dicionário para armazenar o estado do usuário
user_state = {} # Rastreia se o usuário já enviou a data ou código key no processo de reset de senha
conversation_state = {} # Utilizado para rastrear se o usuário já inciou um atendimento ou não, se não iniciou, o message handler com message:True entra em ação

# Start Point 
@bot.message_handler(commands=['start', 'inicio'])
def start_message(message):
    chat_id = message.chat.id
    user_firstname = message.from_user.first_name
    if conversation_state.get(chat_id) is None: # Aqui eu testo pra ver se ele já não passou por aqui quando ele usa o /inicio
        conversation_state[chat_id]='menu_start'
        msg = 'Olá! 👋 Eu sou o Célio, o chatbot da Clear CFTV. Posso te ajudar em algumas coisas, mas antes preciso que você aceite nossa política de privacidade que\
    pode ser encontrada [aqui](https://www.clearcftv.com.br/pol%C3%ADtica-de-privacidade)'

        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        custom_keyboard = [InlineKeyboardButton('Aceito', callback_data='callback_start'),
                        InlineKeyboardButton('Não aceito', callback_data='callback_privacidade_negada')]
        
        markup.add(custom_keyboard[0], custom_keyboard[1])

        bot.send_message(chat_id, msg, parse_mode='Markdown', reply_markup=markup)
    else:
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        custom_keyboard = [InlineKeyboardButton('Reiniciar atendimento', callback_data='callback_start')]
        
        markup.add(custom_keyboard[0])
        msg = 'Clique no botão para recomeçar ou envie /sair para encerrar o atendimento'
        bot.send_message(chat_id, msg, parse_mode='Markdown', reply_markup=markup)



# Message Handlers - Respostas aos comandos
@bot.message_handler(commands=['veicular'])
def veicular(message):  
    chat_id = message.chat.id
    conversation_state[chat_id]='comercial_veicular'
    bot.send_message(message.chat.id, 'Aqui vai um [vídeo](https://www.youtube.com/watch?v=SqESxWL17bQ) para você conhecer mais sobre nossa linha veicular: ', parse_mode='Markdown')
    bot.send_message(message.chat.id, 'Para receber nosso Catálogo, me envie\n/catalogoveicular, ou clique no comando que eu envio para você... ')
    bot.send_message(message.chat.id, 'Se desejar encerrar seu atendimento, digite /sair ou se quiser retornar ao início, digite /incio')

@bot.message_handler(commands=['catalogoveicular'])
def catalogoveicular(message):    
    bot.send_message(message.chat.id, 'Ok! Um momento... ')
    with open('media/veicular/docs/CatalogoVeicular.pdf', 'rb') as catalogo_veicular:
        bot.send_document(message.chat.id,catalogo_veicular, caption='Aqui está!')
    bot.send_message(message.chat.id, 'Se desejar encerrar seu atendimento, digite /sair ou se quiser retornar ao início, digite /inicio')

@bot.message_handler(commands=['cftv','CFTV'])
def cftv(message):
    chat_id = message.chat.id
    conversation_state[chat_id] = 'comercial_cftv'
    bot.send_message(chat_id, 'Vou te encaminhar nosso catálogo de produtos para você conhecer nossas novidades...')
    with open('media/cftv/docs/catalogo_cftv.pdf','rb') as catalogo_cftv:
        bot.send_document(chat_id, catalogo_cftv, caption='Aqui está! Se tiver dúvidas, entre em contato com nossos consultores, será um prazer te ajudar...')
    bot.send_message(chat_id, 'Se desejar encerrar seu atendimento, digite /sair ou se quiser retornar ao início, digite /inicio')

@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == 'esperando_key')
def handle_key(message):
    conversation_state[chat_id]='resetando_senha'
    chat_id = message.chat.id
    user_input = message.text
    try:
        key = int(user_input)
        senha = ResetXiongmaiDate(key, 'key')
        bot.send_message(chat_id, f'Aqui está: {senha}')
        bot.send_message(chat_id, 'Insira a senha acima no seu DVR. Em seguida, aguarde. Após o procedimento, a senha será nula (em branco)')
        bot.send_message(chat_id, 'Para reiniciar seu atendimento envie /inicio ou /start. Ou clique nos comandos dessa mensagem')
    except ValueError:
        bot.send_message(chat_id, 'Não foi possível entender o que você escreveu. Tente novamente clicando no botão "Reset de Senha" e verifique se digitou corretamente.')

    user_state.pop(chat_id)  # Remova o estado do usuário após a conclusão

@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == 'esperando_data')
def handle_data(message):
    chat_id = message.chat.id
    user_input = message.text
    try:
        data = int(user_input)
        senha = ResetXiongmaiDate(data, 'date')
        bot.send_message(chat_id, f'Aqui está: {senha}')
        bot.send_message(chat_id, 'Insira a senha acima no seu DVR respeitando as letras maiúsculas e minúsculas. Em seguida, aguarde. Após o procedimento, a senha será nula (em branco)')
        bot.send_message(chat_id, 'Para reiniciar seu atendimento envie /inicio ou /start. Ou clique nos comandos dessa mensagem')

    except ValueError:
        bot.send_message(chat_id, 'Não foi possível entender o que você escreveu. Tente novamente clicando no botão "Reset de Senha" e verifique se digitou corretamente.')
    
    del user_state[chat_id]  # Remova o estado do usuário após a conclusão

@bot.message_handler(commands =['especialista'])
def especialista(message):
    chat_id = message.chat.id
    conversation_state[chat_id] = 'especialista'
    msg = 'No momento, você pode falar com um de nossos especialistas através do nosso WhatsApp oficial do Suporte Técnico clicando [aqui](wa.me/+553534734043).\nLembre-se que nossos especialistas estão disponíveis\
 de *segunda à sexta das 08:00 às 18:00*.'
    bot.send_message(chat_id, msg, parse_mode='Markdown')

@bot.message_handler(commands=['ajuda'])
def ajuda(message):
    chat_id = message.chat.id
    conversation_state[chat_id] = 'ajuda'
    reply = InlineKeyboardMarkup()
    custom_keyboard = [InlineKeyboardButton('Reset por data', callback_data='callback_reset_data'),
                      InlineKeyboardButton('Reset por código key', callback_data='callback_reset_key')]
    reply.add(custom_keyboard[0], custom_keyboard[1])
    with open('media/cftv/imgs/key.png', 'rb') as photo:
        bot.send_photo(chat_id, photo,'Se seu DVR tiver este símbolo -> ❓  então selecione a opção [Código Key]. Caso não tenha, selecione a opção [Reset por Data]', reply_markup=reply)

@bot.message_handler(commands=['sair'])
def sair(message):
    chat_id = message.chat.id
    user_firstname = message.from_user.first_name  # Usar user_firstname em vez de user_first_name
    if chat_id in conversation_state:
        del conversation_state[chat_id]
    if chat_id in user_state:
        del user_state[chat_id]
    bot.send_message(chat_id, f'Espero ter te ajudado! Até breve, {user_firstname} 👋')


# Callback Query Handlers - Respostas aos botões
@bot.callback_query_handler(func=lambda call: call.data == 'callback_start')
def callback_start(call):
    chat_id = call.message.chat.id
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
    msg = 'Lamento mas não posso dar sequência no seu atendimento sem que aceite nossos termos.'
    msg2 = 'Espero poder te ajudar em breve 👋'
    if chat_id in conversation_state:
        del conversation_state[chat_id]
    if chat_id in user_state:
        del user_state[chat_id]
    bot.send_message(chat_id, msg)
    bot.send_message(chat_id, msg2)

# Callback Comercial
@bot.callback_query_handler(func=lambda call: call.data == 'callback_comercial')
def callback_comercial(call):
    chat_id = call.message.chat.id
    conversation_state[chat_id] = 'callback_comercial'
    user_firstname = call.from_user.first_name
    msg = f'{user_firstname}, aqui vai algumas opções que posso fazer por você:\n\n\
☎️ - Fale conosco: 3534734000\n\
🚛 - Conheça nossa linha /veicular\n\
🎥 - Conheça nossa linha /CFTV\n\
💻 - Acesse nosso [site](www.clearcftv.com.br)👇\n\n\
                             '
   
    bot.send_message(chat_id, msg, parse_mode='Markdown')
    msg2 = 'Se precisar retornar, digite /inicio para voltar.'
    bot.send_message(chat_id, msg2)


# Callback Suporte Técnico 👇👇
@bot.callback_query_handler(func=lambda call: call.data == 'callback_suporte')
def callback_suporte(call):
    chat_id = call.message.chat.id
    conversation_state[chat_id]='callback_suporte'
    msg = "Vejo que você precisa de ajuda com nossos produtos.\nSelecione a vertical de produtos que precisa de suporte. 👇"
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    custom_keyboard = [InlineKeyboardButton('Veicular', callback_data='callback_veicular'),
                       InlineKeyboardButton('CFTV', callback_data='callback_cftv')]
    
    markup.add(custom_keyboard[0], custom_keyboard[1])

    bot.send_message(chat_id, msg, reply_markup=markup)
    msg2 = 'Se precisar retornar, digite /inicio para voltar.'
    bot.send_message(chat_id, msg2)

@bot.callback_query_handler(func=lambda call: call.data == 'callback_veicular')
def callback_veicular(call):
    chat_id = call.message.chat.id
    conversation_state[chat_id] = 'callback_veicular'
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    custom_keyboard = [InlineKeyboardButton('Voltar', callback_data='callback_suporte')]
    markup.add(custom_keyboard[0])
    msg = 'Eu ainda estou aprendendo sobre este recurso 🤔... Não posso te ajudar com isso no momento mas você pode me pedir através do /especialista para\
te encaminhar para nossos especialistas'
    bot.send_message(chat_id, msg, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'callback_cftv')
def callback_cftv(call):
    chat_id = call.message.chat.id
    conversation_state[chat_id] = 'callback_cftv'
    reply = InlineKeyboardMarkup()
    custom_keyboard = [InlineKeyboardButton('Reset de Senha', callback_data='callback_reset_de_senha'),
                      InlineKeyboardButton('Dúvidas Gerais', callback_data='callback_duvidas_gerais'),
                      InlineKeyboardButton('Voltar', callback_data='callback_suporte')]
    reply.add(custom_keyboard[0], custom_keyboard[1], custom_keyboard[2])
    msg = f'Perfeito! Aqui vão algumas opções disponíveis pra você:'
    bot.send_message(chat_id, msg, reply_markup=reply)

@bot.callback_query_handler(func=lambda call: call.data == 'callback_reset_de_senha')
def callback_cftv(call):
    reply = InlineKeyboardMarkup()
    custom_keyboard = [InlineKeyboardButton('Reset por data', callback_data='callback_reset_data'),
                      InlineKeyboardButton('Reset por código key', callback_data='callback_reset_key')]
    reply.add(custom_keyboard[0], custom_keyboard[1])
    msg = f'Perfeito! Atualmente, eu só consigo realizar o reset de senha dos DVRs da linha Xmeye. Caso seja o seu modelo, escolha o método de reset de senha 👇'
    msg2 = 'Se não souber qual método usar, me mande um /ajuda ou clique no comando que eu te mostro...'
    bot.send_message(call.message.chat.id, msg, reply_markup=reply)
    bot.send_message(call.message.chat.id, msg2)

@bot.callback_query_handler(func=lambda call: call.data == 'callback_reset_data')
def callback_reset_data(call):
    chat_id = call.message.chat.id
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
    conversation_state[chat_id] = 'callback_duvidas_gerais'
    msg = 'Agora, preciso saber de qual produto estamos falando.'
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    custom_keyboard = [InlineKeyboardButton('DVR', callback_data='callback_duvida_dvr'),
                       InlineKeyboardButton('Câmeras Analógicas', callback_data='callback_duvida_cam_analog'),
                       InlineKeyboardButton('NVR', callback_data='callback_duvida_nvr'),
                       InlineKeyboardButton('Câmeras IP', callback_data='callback_duvida_ipc')]
    
    markup.add(custom_keyboard[0], custom_keyboard[1], custom_keyboard[2], custom_keyboard[3])
    bot.send_message(chat_id, msg, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'callback_duvida_dvr')
def callback_duvida_dvr(call):
    chat_id = call.message.chat.id
    conversation_state[chat_id] = 'callback_duvida_dvr'
    msg = 'Entendido! A Clear CFTV, possui mais de um modelo de DVR.'
    msg2 = 'Segue uma foto que vai te ajudar a você descobrir qual modelo é o seu:'
    msg3 = 'Escolha qual modelo é o seu. Se não encontrar, não se preocupe, você pode falar com nossos especialistas me enviando um /especialista a qualquer momento...'
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    custom_keyboard = [InlineKeyboardButton('DVR', callback_data='callback_produto_dvr'),
                       InlineKeyboardButton('HVR', callback_data='callback_produto_hvr'),
                       InlineKeyboardButton('XVR', callback_data='callback_produto_xvr')]
    markup.add(custom_keyboard[0], custom_keyboard[1], custom_keyboard[2])
    bot.send_message(chat_id, msg)
    with open ('media/cftv/imgs/dvrs.png', 'rb') as photo:
        bot.send_photo(chat_id, photo, msg2)
    bot.send_message(chat_id, msg3, reply_markup=markup)



#### echo message handler ####
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    chat_id = message.chat.id
    if conversation_state.get(chat_id) is None:
        bot.reply_to(message, 'Digite /start para começar')
        conversation_state[chat_id] = "em_andamento"
    elif conversation_state.get(chat_id) is not None:
        # Não faça nada quando a conversa está em andamento
        pass
    else:
        # Lidere com mensagens quando a conversa não está em andamento
        pass


bot.infinity_polling()


