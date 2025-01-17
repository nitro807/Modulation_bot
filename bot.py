import os
import random
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
)

# Настройка логгирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен берется из переменных окружения
TOKEN = os.getenv("TOKEN")

# Списки тональностей
MAJOR_TONALITIES = [
    "C-dur",
    "F-dur",
    "D-dur",
    "B-dur",
    "A-dur",
    "Es-dur",
    "E-dur",
    "As-dur",
    "H-dur",
    "Des-dur",
    "Fis-dur",
    "Ges-dur",
    "Cis-dur",
    "Ces-dur",
    "G-dur",
]

MINOR_TONALITIES = [
    "a-moll",
    "g-moll",
    "h-moll",
    "c-moll",
    "fis-moll",
    "f-moll",
    "cis-moll",
    "b-moll",
    "gis-moll",
    "es-moll",
    "dis-moll",
    "as-moll",
    "ais-moll",
    "e-moll",
    "d-moll",
]

# Общий список тональностей
ALL_TONALITIES = MAJOR_TONALITIES + MINOR_TONALITIES

# Списки ступеней
MAJOR_STEPS = ["II", "III", "IV", "V", "VI"]
MINOR_STEPS = ["III", "IV", "V", "VI", "VII"]


# Функция для генерации случайной модуляции
def generate_modulation(step=None):
    try:
        if step:
            result = []
            if step in MINOR_STEPS:
                result.extend(
                    [f"{tonality}, {step} ступень" for tonality in MINOR_TONALITIES]
                )
            if step in MAJOR_STEPS:
                result.extend(
                    [f"{tonality}, {step} ступень" for tonality in MAJOR_TONALITIES]
                )
            return random.choice(result) if result else None
        else:
            mode = random.choice(["major", "minor"])
            if mode == "major":
                tonality = random.choice(MAJOR_TONALITIES)
                step = random.choice(MAJOR_STEPS)
            else:
                tonality = random.choice(MINOR_TONALITIES)
                step = random.choice(MINOR_STEPS)
            return f"{tonality}, {step} ступень"
    except Exception as e:
        logger.error(f"Ошибка при генерации модуляции: {e}")
        return "Произошла ошибка при генерации модуляции. Попробуйте ещё раз."


# Функция для генерации случайной ступени для выбранной тональности
def generate_step_for_tonality(tonality):
    try:
        if tonality in MAJOR_TONALITIES:
            step = random.choice(MAJOR_STEPS)
        elif tonality in MINOR_TONALITIES:
            step = random.choice(MINOR_STEPS)
        else:
            return None
        return f"{tonality}, {step} ступень"
    except Exception as e:
        logger.error(f"Ошибка при генерации ступени для тональности: {e}")
        return "Произошла ошибка при генерации ступени. Попробуйте ещё раз."


# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(
            "Привет! Я бот для генерации случайных музыкальных модуляций.\n"
            "Используй команду /modulate, чтобы получить случайную тональность и ступень.\n"
            "Используй команду /select_step, чтобы выбрать ступень и получать модуляции для неё.\n"
            "Используй команду /select_tonality, чтобы выбрать тональность и получать случайные ступени для неё."
        )
    except Exception as e:
        logger.error(f"Ошибка в команде /start: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте ещё раз.")


# Обработчик команды /modulate
async def modulate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        modulation = generate_modulation()
        await update.message.reply_text(modulation)
    except Exception as e:
        logger.error(f"Ошибка в команде /modulate: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте ещё раз.")


# Обработчик команды /select_step с inline-кнопками
async def select_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        keyboard = [
            [
                InlineKeyboardButton(step, callback_data=f"step_{step}")
                for step in MAJOR_STEPS
            ],
            [
                InlineKeyboardButton(step, callback_data=f"step_{step}")
                for step in MINOR_STEPS
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "Выберите ступень, чтобы получать модуляции для неё:",
            reply_markup=reply_markup,
        )
    except Exception as e:
        logger.error(f"Ошибка в команде /select_step: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте ещё раз.")


# Обработчик выбора ступени из inline-кнопок
async def handle_step_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    step = query.data.split("_")[1]
    if step in MAJOR_STEPS or step in MINOR_STEPS:
        modulation = generate_modulation(step)

        # Обновляем сообщение с новыми кнопками
        keyboard = [
            [
                InlineKeyboardButton(step, callback_data=f"step_{step}")
                for step in MAJOR_STEPS
            ],
            [
                InlineKeyboardButton(step, callback_data=f"step_{step}")
                for step in MINOR_STEPS
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text=f"Модуляция для выбранной ступени {step}: {modulation}\n"
            "Выберите ещё ступень или введите /cancel для завершения.",
            reply_markup=reply_markup,
        )
    else:
        await query.edit_message_text("Некорректная ступень. Попробуйте снова.")


# Обработчик команды /select_tonality с inline-кнопками
async def select_tonality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        keyboard = [
            [
                InlineKeyboardButton(tonality, callback_data=f"tonality_{tonality}")
                for tonality in MAJOR_TONALITIES[:7]
            ],
            [
                InlineKeyboardButton(tonality, callback_data=f"tonality_{tonality}")
                for tonality in MINOR_TONALITIES[:7]
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "Выберите тональность, чтобы получать случайные ступени:",
            reply_markup=reply_markup,
        )
    except Exception as e:
        logger.error(f"Ошибка в команде /select_tonality: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте ещё раз.")


# Обработчик выбора тональности из inline-кнопок
async def handle_tonality_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    tonality = query.data.split("_")[1]
    if tonality in ALL_TONALITIES:
        modulation = generate_step_for_tonality(tonality)

        # Обновляем сообщение с новыми кнопками
        keyboard = [
            [
                InlineKeyboardButton(tonality, callback_data=f"tonality_{tonality}")
                for tonality in MAJOR_TONALITIES[:7]
            ],
            [
                InlineKeyboardButton(tonality, callback_data=f"tonality_{tonality}")
                for tonality in MINOR_TONALITIES[:7]
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text=f"Случайная ступень для выбранной тональности {tonality}: {modulation}\n"
            "Выберите ещё тональность или введите /cancel для завершения.",
            reply_markup=reply_markup,
        )
    else:
        await query.edit_message_text("Некорректная тональность. Попробуйте снова.")


# Обработчик команды /cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(
            "Отмена. Возврат к начальному меню.\n"
            "Используй команду /modulate, чтобы получить случайную тональность и ступень.\n"
            "Используй команду /select_step, чтобы выбрать ступень и получать модуляции для неё.\n"
            "Используй команду /select_tonality, чтобы выбрать тональность и получать случайные ступени для неё."
        )
    except Exception as e:
        logger.error(f"Ошибка в команде /cancel: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте ещё раз.")


# Регистрация новых обработчиков
def main():
    try:
        application = Application.builder().token(TOKEN).build()

        # Обработчики команд
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("modulate", modulate))
        application.add_handler(CommandHandler("cancel", cancel))

        # Inline-кнопки
        application.add_handler(
            CallbackQueryHandler(handle_step_callback, pattern="^step_")
        )
        application.add_handler(
            CallbackQueryHandler(handle_tonality_callback, pattern="^tonality_")
        )

        # Команды для inline-кнопок
        application.add_handler(CommandHandler("select_step", select_step))
        application.add_handler(CommandHandler("select_tonality", select_tonality))

        # Запуск бота
        application.run_polling()
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")


if __name__ == "__main__":
    if not TOKEN:
        logger.error(
            "Токен не задан. Убедитесь, что переменная окружения TOKEN установлена."
        )
        exit(1)

    try:
        main()
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        exit(1)
