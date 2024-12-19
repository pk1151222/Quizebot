import json
import os
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Store user states
user_states = {}

# Commands List
commands = {
    "/start": "Start the quiz",
    "/stop": "Stop the bot",
    "/help": "Get help",
    "/language": "Change language (Hindi/English)",
    "/score": "Check your score"
}
# Start Command
@bot.message_handler(commands=['start'])
def start_quiz(message):
    chat_id = message.chat.id
    user_states[chat_id] = {"quiz_active": True, "score": 0}
    bot.send_message(chat_id, "Welcome to the Quiz Bot!\nType /help to see available commands.")
    show_commands_menu(chat_id)
    
# Stop Command
@bot.message_handler(commands=['stop'])
def stop_bot(message):
    chat_id = message.chat.id
    user_states[chat_id] = {"quiz_active": False}
    bot.send_message(chat_id, "Quiz stopped. Thank you for playing!")
    # Optionally remove the user state
    user_states.pop(chat_id, None)


# Help Command
@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = "Here are the available commands:\n"
    for cmd, desc in commands.items():
        help_text += f"{cmd}: {desc}\n"
    bot.send_message(message.chat.id, help_text)

 Show Commands Menu
def show_commands_menu(chat_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    for cmd in commands:
        markup.add(KeyboardButton(cmd))
    bot.send_message(chat_id, "Use the buttons below to interact with the bot:", reply_markup=markup)

# Fallback Handler



# Quiz data structure
quiz_data = {"questions": [], "current_question": 0, "score": 0}


def load_questions():
    """
    Load questions from the local JSON file.
    """
    with open("questions_hindi.json", "r", encoding="utf-8") as file:
        return json.load(file)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Start the quiz and send the first question.
    """
    quiz_data["questions"] = load_questions()
    quiz_data["current_question"] = 0
    quiz_data["score"] = 0
    await send_question(update)


async def send_question(update: Update):
    """
    Send the current question with options to the user.
    """
    question_index = quiz_data["current_question"]
    if question_index < len(quiz_data["questions"]):
        question = quiz_data["questions"][question_index]
        question_text = (
            f"Q{question_index + 1}: {question['question_hindi']} ({question['question']})"
        )
        options = [
            InlineKeyboardButton(f"{opt_h} ({opt_e})", callback_data=opt_e)
            for opt_e, opt_h in zip(question["options"], question["options_hindi"])
        ]
        keyboard = InlineKeyboardMarkup.from_column(options)

        if update.callback_query:
            await update.callback_query.message.reply_text(question_text, reply_markup=keyboard)
        else:
            await update.message.reply_text(question_text, reply_markup=keyboard)
    else:
        await update.message.reply_text(
            f"🎉 Quiz finished! Your score is {quiz_data['score']} / {len(quiz_data['questions'])}"
        )


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the user's answer and provide feedback.
    """
    query = update.callback_query
    await query.answer()
    selected_answer = query.data

    question_index = quiz_data["current_question"]
    correct_answer = quiz_data["questions"][question_index]["correct_answer"]

    if selected_answer == correct_answer:
        quiz_data["score"] += 1
        await query.edit_message_text("✅ Correct!")
    else:
        correct_answer_hindi = quiz_data["questions"][question_index]["correct_answer_hindi"]
        await query.edit_message_text(
            f"❌ Incorrect! Correct answer: {correct_answer_hindi} ({correct_answer})"
        )

    quiz_data["current_question"] += 1
    await send_question(update)


def main():
    """
    Main function to start the bot.
    """
    
    application = Application.builder().token(BOT_TOKEN).build()
# Fallback Handler
@bot.message_handler(func=lambda message: True)
def fallback(message):
    chat_id = message.chat.id
    if user_states.get(chat_id, {}).get("quiz_active", False):
        bot.send_message(chat_id, "Please use the commands or answer the quiz.")
    else:
        bot.send_message(chat_id, "The bot is stopped. Type /start to begin again.")

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_answer))

    print("Bot is running...")
    application.run_polling()


if __name__ == "__main__":
    main()
