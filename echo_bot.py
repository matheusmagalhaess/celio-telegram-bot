import telebot
import logging
from reset_senha import ResetXiongmaiDate
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

# Carregar o token a partir de um arquivo de configuração externo
with open('config.txt', "r") as config_file:
    TOKEN = config_file.read().strip()

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)  # Outputs debug messages to console.

bot = telebot.TeleBot(TOKEN)

# Dicionário para armazenar o estado do usuário
user_state = {}
conversation_state = {}

@bot.message_handler(commands=['start', 'voltar'])
def start_message(message):
    chat_id = message.chat.id
    user_firstname = message.from_user.first_name
    msg = f"Olá, {user_firstname} 👋!\nMeu nome é Célio, sou o chatbot da Clear CFTV!\nPosso te ajudar em algumas coisas:"
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    custom_keyboard = [InlineKeyboardButton('Veicular', callback_data='callback_veicular'),
                       InlineKeyboardButton('CFTV', callback_data='callback_cftv')]
    
    markup.add(custom_keyboard[0], custom_keyboard[1])

    bot.send_message(message.chat.id, msg, reply_markup=markup)

@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == 'esperando_key')
def handle_key(message):
    chat_id = message.chat.id
    user_input = message.text
    try:
        key = int(user_input)
        senha = ResetXiongmaiDate(key, 'key')
        bot.send_message(chat_id, f'Aqui está: {senha}')
        bot.send_message(chat_id, 'Insira a senha acima no seu DVR respeitando as letras maiúsculas e minúsculas. Em seguida, aguarde. Após o procedimento, a senha será nula (em branco)')
        bot.send_message(chat_id, 'Para reiniciar seu atendimento envie /voltar ou /start. Ou clique nos comandos dessa mensagem')
    except ValueError:
        bot.send_message(chat_id, 'Não foi possível entender o que você escreveu. Tente novamente clicando no botão "Reset de Senha" e verifique se digitou corretamente.')

    user_state.pop(chat_id)  # Remova o estado do usuário após a conclusão

@bot.message_handler(commands=['sair'])
def sair(message):
    chat_id = message.chat.id
    user_firstname = message.from_user.first_name  # Usar user_firstname em vez de user_first_name
    if chat_id in conversation_state:
        del conversation_state[chat_id]
    if chat_id in user_state:
        del user_state[chat_id]
    bot.send_message(chat_id, f'Espero ter te ajudado! Até breve, {user_firstname} 👋')


@bot.message_handler(commands=['ajuda'])
def ajuda(message):
    chat_id = message.chat.id
    reply = InlineKeyboardMarkup()
    custom_keyboard = [InlineKeyboardButton('Reset por data', callback_data='callback_reset_data'),
                      InlineKeyboardButton('Reset por código key', callback_data='callback_reset_key')]
    reply.add(custom_keyboard[0], custom_keyboard[1])
    with open('media\cftv\imgs\key.png', 'rb') as photo:
        bot.send_photo(chat_id, photo,'Se seu DVR tiver este símbolo -> ❓  então selecione a opção [Código Key]. Caso não tenha, selecione a opção [Reset por Data]', reply_markup=reply)

@bot.message_handler(func=lambda message: True)
def echo_message(message):
    chat_id = message.chat.id
    if conversation_state.get(chat_id) is None:
        bot.reply_to(message, 'Digite /start para começar')
        conversation_state[chat_id] = "em_andamento"
    elif conversation_state.get(chat_id) == "em_andamento":
        # Não faça nada quando a conversa está em andamento
        pass
    else:
        # Lidere com mensagens quando a conversa não está em andamento
        pass


@bot.callback_query_handler(func=lambda call: call.data == 'callback_veicular')
def callback_veicular(call):
    msg = 'Recurso indisponível, utilize o /voltar para retornar'
    bot.send_message(call.message.chat.id, msg)

@bot.callback_query_handler(func=lambda call: call.data == 'callback_cftv')
def callback_cftv(call):
    reply = InlineKeyboardMarkup()
    custom_keyboard = [InlineKeyboardButton('Reset de Senha', callback_data='callback_reset_de_senha'),
                      InlineKeyboardButton('Dúvidas Gerais', callback_data='callback_duvidas_gerais')]
    reply.add(custom_keyboard[0], custom_keyboard[1])
    msg = f'Perfeito! Aqui vão algumas opções disponíveis pra você:'
    bot.send_message(call.message.chat.id, msg, reply_markup=reply)

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

    # Verifique se o usuário já forneceu a data anteriormente
    if user_state.get(chat_id) == 'esperando_data':
        bot.send_message(chat_id, 'Você já enviou a data. Aguarde uma resposta.')
    else:
        bot.send_message(chat_id, 'Envie a data que está sendo exibida na tela do *equipamento* no formato AAAAMMDD e aguarde alguns instantes...', parse_mode='Markdown')
        bot.send_message(chat_id, '*Exemplo*: Se a data informada é `14/09/2023`, digite: `20230914`', parse_mode='Markdown')
        user_state[chat_id] = 'esperando_data'

@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == 'esperando_data')
def handle_data(message):
    chat_id = message.chat.id
    user_input = message.text
    try:
        data = int(user_input)
        senha = ResetXiongmaiDate(data, 'date')
        bot.send_message(chat_id, f'Aqui está: {senha}')
        bot.send_message(chat_id, 'Insira a senha acima no seu DVR respeitando as letras maiúsculas e minúsculas. Em seguida, aguarde. Após o procedimento, a senha será nula (em branco)')
        bot.send_message(chat_id, 'Para reiniciar seu atendimento envie /voltar ou /start. Ou clique nos comandos dessa mensagem')

    except ValueError:
        bot.send_message(chat_id, 'Não foi possível entender o que você escreveu. Tente novamente clicando no botão "Reset de Senha" e verifique se digitou corretamente.')
    
    user_state.pop(chat_id)  # Remova o estado do usuário após a conclusão

@bot.callback_query_handler(func=lambda call: call.data == 'callback_reset_key')
def callback_reset_key(call):
    chat_id = call.message.chat.id

    # Verifique se o usuário já forneceu a data anteriormente
    if user_state.get(chat_id) == 'esperando_key':
        bot.send_message(chat_id, 'Você já enviou o código key. Aguarde uma resposta.')
    else:
        bot.send_message(chat_id, 'Envie o código Key que está sendo exibido na tela e aguarde alguns instantes...')
        user_state[chat_id] = 'esperando_key'





bot.polling()


