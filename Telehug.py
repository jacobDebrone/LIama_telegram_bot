import telebot
from hugchat import hugchat
from hugchat.login import Login
import time
import traceback
import logging

logging.basicConfig(level=logging.INFO)

# Set up the Telegram bot
bot_token = "Token"
bot = telebot.TeleBot(bot_token)
chatbot = None
def initialize_chatbot():
    global chatbot
    try:
        # Initialize the HugChat chatbot
        sign = Login("Huggingfcace_email", "Huggingface_password")
        cookies = sign.login()
        sign.saveCookiesToDir()
        chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
        logging.info("HugChat chatbot initialized successfully.")
    except Exception as e:
        logging.error(f"Error initializing HugChat chatbot: {e}")
        raise  # Reraise the exception to trigger reconnect
# Initialize the chatbot in the global scope


# Dictionary to store user-specific conversations
user_conversations = {}
initialize_chatbot()

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    try:
        # Create or get the user's conversation ID
      # Add a longer delay before attempting to reconnect again

        user_chat_id = message.chat.id
        if user_chat_id not in user_conversations:
            # Create a new conversation for the user
            user_conversations[user_chat_id] = chatbot.new_conversation()

        # Switch to the user's conversation
        chatbot.change_conversation(user_conversations[user_chat_id])

        # Handle the user's message
        handle_message(message)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        traceback.print_exc()
        reconnect_and_handle_errors()

def handle_message(message):
    user_input = message.text
    bot.send_chat_action(message.chat.id, 'typing')
    time.sleep(1)

    response = str(chatbot.chat(user_input))

    # Split the response into chunks of a certain length (e.g., 4096 characters)
    max_message_length = 4096
    chunks = [response[i:i + max_message_length] for i in range(0, len(response), max_message_length)]

    # Send only unique chunks
    previous_chunk = None
    for chunk in chunks:
        if chunk != previous_chunk:
            bot.send_message(message.chat.id, chunk)
            previous_chunk = chunk


@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Welcome to the AI chatbot. You can start by typing your message.")

def reconnect_and_handle_errors():
    global bot
    while True:
        try:
            bot.stop_polling()
            bot = telebot.TeleBot(bot_token)
            bot.infinity_polling(timeout=30, long_polling_timeout=5)
        except Exception as e:
            print(f"Reconnection failed: {e}")
            traceback.print_exc()
            time.sleep(10)
# Start the bot
try:
    bot.infinity_polling(timeout=30, long_polling_timeout=5)
except Exception as e:
    print(f"An error occurred: {e}")
    traceback.print_exc()
    initialize_chatbot()
    reconnect_and_handle_errors()
