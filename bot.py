import telebot
from telebot import types
import logging
import time
import game
import constants as const
from database import players_db_functions as pdb  # players database


# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='chess_bot.log',
    filemode='a'
)

logger = logging.getLogger(__name__)

bot = telebot.TeleBot(const.API_TOKEN)

# Constants for result codes
RESULT_ERROR = -1
RESULT_CANCELLED = -2
RESULT_BOT_WON = 0
RESULT_USER_WON = 1
RESULT_DRAW = 2


def main_menu_markup():
    if not hasattr(main_menu_markup, 'markup'):
        markup = types.InlineKeyboardMarkup(row_width=3)
        buttons = [
            types.InlineKeyboardButton(
                'Leaderboards',
                callback_data='leaderboards'),
            types.InlineKeyboardButton(
                'Play Blitz (3 + 0)',
                callback_data='blitz'),
            types.InlineKeyboardButton(
                'Play Bullet (2 + 1)',
                callback_data='bullet')]
        markup.add(*buttons)
        main_menu_markup.markup = markup
    return main_menu_markup.markup


def send_with_menu(chat_id, text, parse_mode=None):
    """Helper function to send messages with menu"""
    try:
        return bot.send_message(
            chat_id,
            text,
            parse_mode=parse_mode,
            reply_markup=main_menu_markup()
        )
    except Exception as e:
        logger.error(f"Failed to send message: {str(e)}")
        raise


def start_new_message(user_id, is_new, username):
    wins, losses, draws = pdb.get_user_stats(user_id)
    if is_new:
        return f"🏆Welcome to Chess Bot, @{username}!🏆\nI see you are a new player! Your stat is w:{wins} l:{losses} d:{draws}. \nChoose an option to get started:"
    return f"🏆Welcome back to Chess Bot, @{username}!🏆\n Your stat is w:{wins} l:{losses} d:{draws}. \nChoose an option to get started:"


@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        pdb.initialize_db()
        user_id = message.chat.id
        username = message.from_user.username
        is_new = pdb.register_user(user_id, username)
        text_message = start_new_message(user_id, is_new, username)
        send_with_menu(
            message.chat.id,
            text_message
        )
    except Exception as e:
        logger.error(f"Start command failed: {str(e)}")


@bot.callback_query_handler(func=lambda call: True)
def handle_button_press(call):
    try:
        bot.answer_callback_query(call.id)

        if call.data == 'leaderboards':
            show_leaderboards(call.message)
        elif call.data in const.GAME_MODES:
            play_game_chess(call.message, call.data)
        else:
            logger.warning(f"Unknown callback data: {call.data}")
            send_with_menu(call.message.chat.id, "❌ Unknown command!")

    except Exception as e:
        logger.error(f"Callback handler failed: {str(e)}")
        send_with_menu(call.message.chat.id, "❌ An error occurred!")


def play_game_chess(message, game_mode):
    """Handle game creation flow with proper error handling"""
    try:

        # Creating game
        challenge_id = game.create_lichess_game(
            const.API_CHESS_TOKEN,
            const.GAME_MODES[game_mode]
        )

        if game.check_if_error(challenge_id):
            raise RuntimeError("Game creation failed")

        # Send game link
        link = game.make_challenge_url(challenge_id)
        bot.send_message(
            message.chat.id,
            f"Here is the <a href='{link}'>link</a>. You have 1 minute to accept the challenge.",
            parse_mode="HTML")

        # Track game session
        result = game.track_session(
            const.USERNAME,
            const.API_CHESS_TOKEN,
            challenge_id
        )
        user_id = message.chat.id
        username = pdb.get_username(user_id)
        if (result >= 0):
            pdb.update_user_stats(user_id, result)
        wins, losses, draws = pdb.get_user_stats(user_id)
        # Send the result
        result_messages = {
            RESULT_ERROR: "❌ An error occurred, try again later",
            RESULT_CANCELLED: "Match was cancelled",
            RESULT_BOT_WON: f"I won you @{username}. Your stat is w:{wins} l:{losses} d:{draws}.",
            RESULT_USER_WON: f"You won me, @{username}. Your stat is w:{wins} l:{losses} d:{draws}.",
            RESULT_DRAW: f"This is a draw, @{username}. Your stat is w:{wins} l:{losses} d:{draws}."}

        text_message = result_messages.get(result)
        send_with_menu(message.chat.id, text_message)

    except Exception as e:
        logger.error(f"Game play error: {str(e)}")
        send_with_menu(
            message.chat.id,
            "❌ Game operation failed. Try again later.")


def show_leaderboards(message):
    try:
        text_message = '\n'.join(pdb.get_top_players())
        send_with_menu(
            message.chat.id,
            text_message
        )
    except Exception as e:
        logger.error(f"Leaderboards error: {str(e)}")
        send_with_menu(message.chat.id, "❌ Failed to load leaderboards")


if __name__ == '__main__':
    logger.info("Starting bot...")
    while True:
        try:
            bot.polling(none_stop=True, interval=2, timeout=30)
        except Exception as e:
            logger.error(f"Polling error: {str(e)}")
            time.sleep(10)
