import json
import os
from dotenv import load_dotenv
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    Update,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Quiz data structure
quiz_data = {"questions": [], "current_question": 0, "score": 0}

# Commands List
commands = {
    "/start": "Start the quiz",
    "/stop": "Stop the bot",
    "/help": "Get help",
    "/language": "Change language (Hindi/English)",
    "/score": "Check your score",
}

# User States
user_states = {}


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
    chat_id = update.message.chat_id
    user_states[chat_id] = {"quiz_active": True, "score": 0}

    quiz_data["questions"] = load_questions()
    quiz_data["current_question"] = 0
    quiz_data["score"] = 0

    await update.message.reply_text("🎉 Welcome to the Quiz Bot!\nType /help to see available commands.")
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
            f"🎉 Quiz finished! Your score is {quiz_data['score']} / {len(quiz_data['questions'])}."
        )
        user_states.pop(update.message.chat_id, None)  # Reset state


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


async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show the help menu with available commands.
    """
    help_text = "Here are the available commands:\n"
    for cmd, desc in commands.items():
        help_text += f"{cmd}: {desc}\n"
    await update.message.reply_text(help_text)


async def show_commands_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show commands menu as a reply keyboard.
    """
    markup = ReplyKeyboardMarkup(
        [[KeyboardButton(cmd)] for cmd in commands], resize_keyboard=True
    )
    await update.message.reply_text("Use the buttons below to interact with the bot:", reply_markup=markup)


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Stop the quiz and reset the user state.
    """
    chat_id = update.message.chat_id
    user_states[chat_id] = {"quiz_active": False}
    await update.message.reply_text("Quiz stopped. Thank you for playing!")
    user_states.pop(chat_id, None)


async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle fallback messages when no command is matched.
    """
    chat_id = update.message.chat_id
    if user_states.get(chat_id, {}).get("quiz_active", False):
        await update.message.reply_text("Please use the commands or answer the quiz.")
    else:
        await update.message.reply_text("The bot is stopped. Type /start to begin again.")


def main():
    """
    Main function to start the bot.
    """
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("help", show_help))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback))
    application.add_handler(CallbackQueryHandler(handle_answer))

    print("Bot is running...")
    application.run_polling()


if __name__ == "__main__":
    main()
