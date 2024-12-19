import json
import os
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Quiz Data Structure
quiz_data = {"questions": [], "current_question": 0, "score": 0}

# Load Questions from JSON
def load_questions():
    """
    Load questions from the local JSON file.
    """
    with open("questions_hindi.json", "r", encoding="utf-8") as file:
        return json.load(file)

# Commands List
commands = {
    "/start": "Start the quiz",
    "/stop": "Stop the bot",
    "/help": "Get help",
    "/language": "Change language (Hindi/English)",
    "/score": "Check your score"
}

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Start the quiz and send the first question.
    """
    quiz_data["questions"] = load_questions()
    quiz_data["current_question"] = 0
    quiz_data["score"] = 0
    await send_question(update)

# Stop Command
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Stop the quiz.
    """
    await update.message.reply_text("Quiz stopped. Thank you for playing!")

# Help Command
async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show help information with the list of commands.
    """
    help_text = "Here are the available commands:\n"
    for cmd, desc in commands.items():
        help_text += f"{cmd}: {desc}\n"
    await update.message.reply_text(help_text)

# Send Question
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

# Handle Answer
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

# Fallback Handler
async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle unexpected messages.
    """
    await update.message.reply_text("Please use the commands or answer the quiz.")

# Show Commands Menu
async def show_commands_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show a dynamic menu with all commands.
    """
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    for cmd in commands:
        markup.add(KeyboardButton(cmd))
    await update.message.reply_text(
        "Use the buttons below to interact with the bot:", reply_markup=markup
    )

# Main Function
def main():
    """
    Main function to start the bot.
    """
    application = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("help", show_help))
    application.add_handler(CallbackQueryHandler(handle_answer))

    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
