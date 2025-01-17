import os
import random
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
)

# Настройка логгирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен берется из переменных окружения
TOKEN = os.getenv("TOKEN")

# Проверка наличия токена
if not TOKEN:
    logger.error(
        "Токен не задан. Убедитесь, что переменная окружения TOKEN установлена."
    )
    exit(1)

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

# Состояния для ConversationHandler
SELECT_STEP, GET_MODULATION, SELECT_TONALITY, GET_TONALITY_MODULATION = range(4)


# Функция для генерации случайной модуляции
def generate_modulation(step=None):
    try:
        if step:
            # Генерация модуляции для конкретной ступени
            result = []
            if step in MAJOR_STEPS:
                # Используем только мажорные тональности для мажорных ступеней
                result.extend(
                    [f"{tonality}, {step} ступень" for tonality in MAJOR_TONALITIES]
                )
            elif step in MINOR_STEPS:
                # Используем только минорные тональности для минорных ступеней
                result.extend(
                    [f"{tonality}, {step} ступень" for tonality in MINOR_TONALITIES]
                )
            return random.choice(result) if result else None
        else:
            # Генерация случайной модуляции
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


# Обработчик команды /select_step
async def select_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(
            "Введите ступень (например, 'V'), чтобы получать модуляции для неё.\n"
            "Используйте /cancel, чтобы выйти из режима выбора ступени."
        )
        return SELECT_STEP
    except Exception as e:
        logger.error(f"Ошибка в команде /select_step: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте ещё раз.")
        return ConversationHandler.END


# Обработчик ввода ступени
async def handle_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        step = update.message.text.upper()
        if step in MAJOR_STEPS or step in MINOR_STEPS:
            context.user_data["step"] = step
            modulation = generate_modulation(step)
            await update.message.reply_text(modulation)
            await update.message.reply_text(
                "Используйте /next, чтобы получить ещё одну модуляцию для этой ступени.\n"
                "Используйте /cancel, чтобы выйти из режима выбора ступени."
            )
            return GET_MODULATION
        else:
            await update.message.reply_text("Некорректная ступень. Попробуйте ещё раз.")
            return SELECT_STEP
    except Exception as e:
        logger.error(f"Ошибка при обработке ступени: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте ещё раз.")
        return SELECT_STEP


# Обработчик команды /next
async def next_modulation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        step = context.user_data.get("step")
        if step:
            modulation = generate_modulation(step)
            await update.message.reply_text(modulation)
            await update.message.reply_text(
                "Используйте /next, чтобы получить ещё одну модуляцию для этой ступени.\n"
                "Используйте /cancel, чтобы выйти из режима выбора ступени."
            )
            return GET_MODULATION
        else:
            await update.message.reply_text(
                "Сначала выберите ступень с помощью /select_step."
            )
            return ConversationHandler.END
    except Exception as e:
        logger.error(f"Ошибка в команде /next: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте ещё раз.")
        return ConversationHandler.END


# Обработчик команды /select_tonality
async def select_tonality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(
            "Введите тональность (например, 'C-dur' или 'a-moll'), чтобы получать случайные ступени для неё.\n"
            "Используйте /cancel, чтобы выйти из режима выбора тональности."
        )
        return SELECT_TONALITY
    except Exception as e:
        logger.error(f"Ошибка в команде /select_tonality: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте ещё раз.")
        return ConversationHandler.END


# Обработчик ввода тональности
async def handle_tonality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        tonality = update.message.text
        if tonality in ALL_TONALITIES:
            context.user_data["tonality"] = tonality
            modulation = generate_step_for_tonality(tonality)
            await update.message.reply_text(modulation)
            await update.message.reply_text(
                "Используйте /next_tonality, чтобы получить ещё одну ступень для этой тональности.\n"
                "Используйте /cancel, чтобы выйти из режима выбора тональности."
            )
            return GET_TONALITY_MODULATION
        else:
            await update.message.reply_text(
                "Некорректная тональность. Попробуйте ещё раз."
            )
            return SELECT_TONALITY
    except Exception as e:
        logger.error(f"Ошибка при обработке тональности: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте ещё раз.")
        return SELECT_TONALITY


# Обработчик команды /next_tonality
async def next_tonality_modulation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        tonality = context.user_data.get("tonality")
        if tonality:
            modulation = generate_step_for_tonality(tonality)
            await update.message.reply_text(modulation)
            await update.message.reply_text(
                "Используйте /next_tonality, чтобы получить ещё одну ступень для этой тональности.\n"
                "Используйте /cancel, чтобы выйти из режима выбора тональности."
            )
            return GET_TONALITY_MODULATION
        else:
            await update.message.reply_text(
                "Сначала выберите тональность с помощью /select_tonality."
            )
            return ConversationHandler.END
    except Exception as e:
        logger.error(f"Ошибка в команде /next_tonality: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте ещё раз.")
        return ConversationHandler.END


# Обработчик команды /cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(
            "Режим выбора ступени или тональности отменён. Возврат к абсолютному рандому."
        )
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Ошибка в команде /cancel: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте ещё раз.")
        return ConversationHandler.END


def main():
    try:
        # Создаем Application и передаем ему токен
        application = Application.builder().token(TOKEN).build()

        # Обработчик команд
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("modulate", modulate))

        # ConversationHandler для режима выбора ступени
        conv_handler_step = ConversationHandler(
            entry_points=[CommandHandler("select_step", select_step)],
            states={
                SELECT_STEP: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_step)
                ],
                GET_MODULATION: [
                    CommandHandler("next", next_modulation),
                    CommandHandler("cancel", cancel),
                ],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
        )
        application.add_handler(conv_handler_step)

        # ConversationHandler для режима выбора тональности
        conv_handler_tonality = ConversationHandler(
            entry_points=[CommandHandler("select_tonality", select_tonality)],
            states={
                SELECT_TONALITY: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tonality)
                ],
                GET_TONALITY_MODULATION: [
                    CommandHandler("next_tonality", next_tonality_modulation),
                    CommandHandler("cancel", cancel),
                ],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
        )
        application.add_handler(conv_handler_tonality)

        # Запускаем бота
        application.run_polling()
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")


if __name__ == "__main__":
    main()
