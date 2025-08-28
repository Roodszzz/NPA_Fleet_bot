import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, filters, ContextTypes
)
from openpyxl import load_workbook
from openpyxl.drawing.image import Image

from openpyxl.styles import Alignment
from io import BytesIO
from datetime import datetime
from googletrans import Translator
from unidecode import unidecode
import base64
import smtplib
import re
from email.message import EmailMessage
import os
import os
from dotenv import load_dotenv

load_dotenv()  # Загружаем .env
TOKEN = os.getenv("TOKEN")


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ===== Встроенный Excel =====

def get_workbook():
    # Берем путь относительно текущего скрипта
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "excel", "LDR.xlsx")  # путь к Excel файлу в папке excel проекта
    return load_workbook(file_path)


# def get_workbook():
#     file_path = "/home/noob/BOT/excel/excel.txt"  # путь к txt с base64
#     with open(file_path, "r") as f:
#         encoded_excel = f.read()
#     file_bytes = base64.b64decode(encoded_excel)
#     return load_workbook(filename=BytesIO(file_bytes))

# ===== Встроенный логотип =====

def get_logo_bytes():
    # Берем путь относительно текущего скрипта
    current_dir = os.path.dirname(__file__)
    logo_path = os.path.join(current_dir, "logo", "Drive the NPA way.png")
    with open(logo_path, "rb") as f:
        return BytesIO(f.read())


# ===== Состояния =====
SERIAL, ALLOCATION, TEAM_NUMBER, USER, DESCRIPTION = range(5)
translator = Translator()
# Менеджеры по локации
managers = {
    "Shyroke": "manager_shyroke@example.com",
    "Mykolaiv": "manager_mykolaiv@example.com"
}


async def translate_to_en(text: str) -> str:
    result = await translator.translate(text, dest='en')
    return result.text

# ===== Вспомогательные функции =====
def set_cell(ws, cell, value):
    ws[cell] = value
    ws[cell].alignment = Alignment(horizontal="center", vertical="center")

def auto_adjust(ws, cells):
    for cell in cells:
        value = ws[cell].value
        if value:
            col_letter = ''.join(filter(str.isalpha, cell))
            ws.column_dimensions[col_letter].width = max(
                ws.column_dimensions[col_letter].width or 10,
                len(str(value)) + 2
            )
            ws.row_dimensions[ws[cell].row].height = max(
                ws.row_dimensions[ws[cell].row].height or 15,
                15
            )



async def send_excel_to_manager(location, file_stream):
    email_to = managers.get(location)
    if not email_to:
        logging.warning(f"No manager found for location: {location}")
        return

    # Заглушка — просто логируем, что файл "отправлен"
    logging.info(f"[TEST MODE] Excel would be sent to {email_to} for location {location}")
    print(f"[TEST MODE] Excel would be sent to {email_to} for location {location}")
            


# async def send_excel_to_manager(location, file_stream):
#     if location == "Shyroke":
#         email_to = "OleRud441@npaid.org"
#         msg = EmailMessage()
#         msg['Subject'] = f"NPA Vehicle Report - {location}"
#         msg['From'] = email_to
#         msg['To'] = email_to
#         msg.set_content(f"Please find attached the latest vehicle report for {location}.")

#         file_stream.seek(0)
#         msg.add_attachment(
#             file_stream.read(),
#             maintype='application',
#             subtype='vnd.openxmlformats-officedocument.spreadsheetml.sheet',
#             filename="report.xlsx"
#         )

#         # Настройки SMTP для Outlook
#         with smtplib.SMTP("smtp.office365.com", 587) as server:
#             server.starttls()
#             server.login(email_to, "Shyroke-441")  # пароль
#             server.send_message(msg)

#         logging.info(f"Excel sent to {email_to} for {location}")
#     else:
#         # Заглушка для других менеджеров
#         logging.info(f"[TEST MODE] Excel would be sent to manager for {location}")
#         print(f"[TEST MODE] Excel would be sent to manager for {location}")





# ===== Главное меню =====
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard_inline = [
        [InlineKeyboardButton("LDR / ЛДР", callback_data="ldr")],
        [InlineKeyboardButton("MFR / МФР", callback_data="mfr")],
        [InlineKeyboardButton("VAR / ВАР", callback_data="var")],
        [InlineKeyboardButton("Contacts / Контакти", callback_data="contacts")],
        [InlineKeyboardButton("Other questions / Інші питання", callback_data="other_questions")]
    ]
    reply_markup_inline = InlineKeyboardMarkup(keyboard_inline)
    text = ("Hello! This is the NPA Fleet bot 🚗\nI can help you create reports for vehicles.\n"
            "Привіт! Це бот NPA Fleet 🚗\nЯ допоможу вам створювати звіти по автомобілях.\n"
            "What are you interested in today? / Що вас цікавить сьогодні?")

    if update.callback_query:
        await update.callback_query.answer()
        try:
            await update.callback_query.message.delete()
        except:
            pass
        await update.callback_query.message.reply_text(text=text, reply_markup=reply_markup_inline)
    elif update.message:
        await update.message.reply_text(text=text, reply_markup=reply_markup_inline)

# ===== Start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    logo_bytes = get_logo_bytes()
    logo_file = InputFile(logo_bytes, filename="logo.png")
    keyboard = [[InlineKeyboardButton("Start / Почати", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_photo(photo=logo_file, caption="Welcome to NPA Fleet bot 🚗\nЛаскаво просимо в NPA Fleet бот", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_photo(photo=logo_file, caption="Welcome to NPA Fleet bot 🚗\nЛаскаво просимо в NPA Fleet бот", reply_markup=reply_markup)

async def start_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await main_menu(update, context)

# ===== Cancel =====


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Очищаем данные пользователя
    context.user_data.clear()

    if update.callback_query:
        # Отвечаем на callback_query, чтобы убрать "часики"
        await update.callback_query.answer()
        # Пытаемся удалить старое сообщение
        try:
            await update.callback_query.message.delete()
        except:
            pass

    # Возврат в главное меню
    await main_menu(update, context)

    return ConversationHandler.END



# ===== LDR =====
async def ldr_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("Flat tire / Пошкоджене колесо", callback_data="flat_tire")],
        [InlineKeyboardButton("Wipers replacement / Заміна дворників", callback_data="wipers")],
        [InlineKeyboardButton("Other request / Інше звернення", callback_data="other_request")],
        [InlineKeyboardButton("Cancel / Відмінити", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try: await query.message.delete()
    except: pass
    await query.message.reply_text("Choose request type / Виберіть тип звернення:", reply_markup=reply_markup)

async def ldr_request_type_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "cancel":
        return await cancel(update, context)
    if data == "other_request":
        keyboard = [[InlineKeyboardButton("Cancel / Відмінити", callback_data="cancel")]]
        try: await query.message.delete()
        except: pass
        await query.message.reply_text("You chose: Other request / Ви обрали: Інше звернення. Function in progress / Функція ще в розробці", reply_markup=InlineKeyboardMarkup(keyboard))
        return ConversationHandler.END

    context.user_data['wb'] = get_workbook()
    context.user_data['ws'] = context.user_data['wb'].active
    ws = context.user_data['ws']
    if data == "flat_tire":
        set_cell(ws, "B4", "Flat tyre / Пошкоджене колесо")
    elif data == "wipers":
        set_cell(ws, "B4", "Wipers replacement / Заміна дворників")
    set_cell(ws, "D4", "Serial / ID / Серійний номер / ID")

    keyboard = [
        [InlineKeyboardButton("Shyroke", callback_data="Shyroke")],
        [InlineKeyboardButton("Mykolaiv", callback_data="Mykolaiv")],
        [InlineKeyboardButton("Cancel / Відмінити", callback_data="cancel")]
    ]
    try: await query.message.delete()
    except: pass
    await query.message.reply_text("Select vehicle location / Оберіть локацію автомобіля:", reply_markup=InlineKeyboardMarkup(keyboard))
    return ALLOCATION

# ===== Ввод данных =====



async def serial_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().upper()  # переводим в верхний регистр
    text = text.replace(" ", "")  # убираем пробелы

    # Если пользователь ввел без дефиса, например AA12, добавим дефис автоматически
    if re.fullmatch(r"[A-Z]{2}\d{2}", text):
        text = text[:2] + "-" + text[2:]

    # проверка формата: две буквы - дефис - две цифры
    if not re.fullmatch(r"[A-Z]{2}-\d{2}", text):
        await update.message.reply_text(
            "❌ Неверный формат номера авто. Формат должен быть: AA-12\nTry again / Спробуйте ще раз:"
        )
        return SERIAL

    ws = context.user_data['ws']
    set_cell(ws, "D4", text)  # записываем нормализованный номер

    keyboard = [
        [InlineKeyboardButton("LOGS", callback_data="LOGS")],
        [InlineKeyboardButton("MTT", callback_data="MTT")],
        [InlineKeyboardButton("MDD", callback_data="MDD")],
        [InlineKeyboardButton("TFM", callback_data="TFM")],
        [InlineKeyboardButton("QA", callback_data="QA")],
        [InlineKeyboardButton("NTS", callback_data="NTS")],
        [InlineKeyboardButton("Cancel / Відмінити", callback_data="cancel")]
    ]
    await update.message.reply_text(
        "Choose Allocation / Оберіть Allocation:", 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ALLOCATION

# async def serial_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     text = update.message.text.strip().upper()  # переводим в верхний регистр
#     text = text.replace(" ", "")  # убираем пробелы

#     # проверка формата: две буквы - дефис - две цифры
#     if not re.fullmatch(r"[A-Z]{2}-\d{2}", text):
#         await update.message.reply_text(
#             "❌ Неверный формат номера авто. Формат должен быть: AA-12\nTry again / Спробуйте ще раз:"
#         )
#         return SERIAL

#     ws = context.user_data['ws']
#     set_cell(ws, "D4", text)  # записываем нормализованный номер

#     keyboard = [
#         [InlineKeyboardButton("LOGS", callback_data="LOGS")],
#         [InlineKeyboardButton("MTT", callback_data="MTT")],
#         [InlineKeyboardButton("MDD", callback_data="MDD")],
#         [InlineKeyboardButton("TFM", callback_data="TFM")],
#         [InlineKeyboardButton("QA", callback_data="QA")],
#         [InlineKeyboardButton("NTS", callback_data="NTS")],
#         [InlineKeyboardButton("Cancel / Відмінити", callback_data="cancel")]
#     ]
#     await update.message.reply_text(
#         "Choose Allocation / Оберіть Allocation:", 
#         reply_markup=InlineKeyboardMarkup(keyboard)
#     )
#     return ALLOCATION



# async def serial_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     text = update.message.text.strip()
#     if not text:
#         await update.message.reply_text("❌ You did not enter a vehicle number / ❌ Ви не ввели номер авто. Try again / Спробуйте ще раз:")
#         return SERIAL
#     ws = context.user_data['ws']
#     set_cell(ws, "D4", text)

#     keyboard = [
#         [InlineKeyboardButton("LOGS", callback_data="LOGS")],
#         [InlineKeyboardButton("MTT", callback_data="MTT")],
#         [InlineKeyboardButton("MDD", callback_data="MDD")],
#         [InlineKeyboardButton("TFM", callback_data="TFM")],
#         [InlineKeyboardButton("QA", callback_data="QA")],
#         [InlineKeyboardButton("NTS", callback_data="NTS")],
#         [InlineKeyboardButton("Cancel / Відмінити", callback_data="cancel")]
#     ]
#     await update.message.reply_text("Choose Allocation / Оберіть Allocation:", reply_markup=InlineKeyboardMarkup(keyboard))
#     return ALLOCATION




    

async def allocation_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    selection = query.data
    if selection == "cancel":
        return await cancel(update, context)
    ws = context.user_data['ws']

    if selection in ["Shyroke", "Mykolaiv"]:
        context.user_data['location'] = selection
        set_cell(ws, "B6", selection)
        try: await query.message.delete()
        except: pass
        await query.message.reply_text("Enter vehicle number or call sign (e.g. HP-12) / Введіть номер авто або call sign (напр. HP-12):", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Cancel / Відмінити", callback_data="cancel")]]))
        return SERIAL

    if selection.upper() in ["NTS", "MTT", "MDD"]:
        context.user_data['allocation'] = selection.upper()
        try: await query.message.delete()
        except: pass
        await query.message.reply_text(f"Enter team number for {selection.upper()} / Введіть номер команди для {selection.upper()}:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Cancel / Відмінити", callback_data="cancel")]]))
        return TEAM_NUMBER

    set_cell(ws, "D6", selection)
    try: await query.message.delete()
    except: pass
    await query.message.reply_text("Enter your full name / Введіть ваше ПІБ:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Cancel / Відмінити", callback_data="cancel")]]))
    return USER

async def team_number_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text.isdigit():
        await update.message.reply_text("❌ Team number must be a number / ❌ Номер команди повинен бути числом. Try again / Спробуйте ще раз:")
        return TEAM_NUMBER
    ws = context.user_data['ws']
    allocation = context.user_data['allocation']
    set_cell(ws, "D6", f"{allocation}-{text}")
    await update.message.reply_text("Enter your full name / Введіть ваше ПІБ:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Cancel / Відмінити", callback_data="cancel")]]))
    return USER

async def user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text:
        await update.message.reply_text("❌ You did not enter your name / ❌ Ви не ввели ПІБ. Try again / Спробуйте ще раз:")
        return USER
    user_name_latin = unidecode(text)
    ws = context.user_data['ws']
    set_cell(ws, "F4", user_name_latin)
    set_cell(ws, "A10", user_name_latin)
    set_cell(ws, "D10", "F.A. Oleksandr Rudnov")
    today_str = datetime.now().strftime("%Y-%m-%d")
    set_cell(ws, "B10", today_str)
    await update.message.reply_text("Briefly describe the situation / Коротко опишіть ситуацію:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Cancel / Відмінити", callback_data="cancel")]]))
    return DESCRIPTION





from openpyxl.drawing.image import Image  # <- убедись, что импорт есть

from openpyxl.drawing.image import Image  # убедись, что импорт есть

async def description_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text:
        await update.message.reply_text(
            "❌ Describe the situation / ❌ Опишіть ситуацію. Try again / Спробуйте ще раз:"
        )
        return DESCRIPTION

    # Перевод текста на английский
    text_en = await translate_to_en(text)

    ws = context.user_data['ws']
    set_cell(ws, "A9", text_en)
    auto_adjust(ws, ["B4","D4","B6","D6","F4","A10","A9","B10"])

    # ==== Вставляем логотип в Excel ====
    logo_path = os.path.join(os.path.dirname(__file__), "logo", "Лого ексель.png")
    img = Image(logo_path)
    img.width = 396  # ширина в пикселях
    img.height = 72  # высота в пикселях
    ws.add_image(img, "A1")  # вставляем в ячейку A1

    # Сохраняем workbook в поток памяти
    file_stream = BytesIO()
    ws.parent.save(file_stream)
    file_stream.seek(0)

    # Отправка пользователю
    # await update.message.reply_document(document=file_stream, filename="result.xlsx")
    await update.message.reply_text("✅ File sent / ✅ Файл відправлено")

    # Отправка менеджерам по локации
    location = context.user_data.get('location')
    if location:
        ADMIN_ID = int(os.getenv("ADMIN_ID"))
        tg_users = {
            "Shyroke": [ADMIN_ID],
            "Mykolaiv": [] # заглушка
        }  
        
        for user_id in tg_users.get(location, []):
            file_stream.seek(0)
            await context.bot.send_document(chat_id=user_id, document=file_stream, filename="result.xlsx")
        
        if location != "Shyroke":
            logging.info(f"[TEST MODE] Excel would be sent to manager for {location}")

    # Очистка данных пользователя
    context.user_data.clear()

    # Стартовое окно с логотипом для Telegram
    logo_bytes_start = get_logo_bytes()
    logo_file = InputFile(logo_bytes_start, filename="logo.png")
    keyboard = [[InlineKeyboardButton("Start / Почати", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_photo(
        photo=logo_file,
        caption="Welcome to NPA Fleet bot 🚗\nЛаскаво просимо в NPA Fleet бот",
        reply_markup=reply_markup
    )

    return ConversationHandler.END






# ===== Заглушки =====
async def generic_stub(update: Update, context: ContextTypes.DEFAULT_TYPE, name="Function"):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("Cancel / Відмінити", callback_data="cancel")]]
    try: await query.message.delete()
    except: pass
    await query.message.reply_text(f"You selected / Ви обрали {name}. Function in progress / Функція ще в розробці", reply_markup=InlineKeyboardMarkup(keyboard))

async def mfr_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await generic_stub(update, context, "MFR / МФР")
async def var_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await generic_stub(update, context, "VAR / ВАР")
async def contacts_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await generic_stub(update, context, "Contacts / Контакти")
async def other_questions_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await generic_stub(update, context, "Other questions / Інші питання")

# ===== Запуск =====
def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(ldr_request_type_callback, pattern="^(flat_tire|wipers|other_request|Shyroke|Mykolaiv)$")],
        states={
            SERIAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, serial_input)],
            ALLOCATION: [CallbackQueryHandler(allocation_input, pattern="^(?!cancel$).*$")],
            TEAM_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, team_number_input)],
            USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, user_input)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, description_input)],
        },
        fallbacks=[CommandHandler("cancel", cancel), CallbackQueryHandler(cancel, pattern="cancel")],
        per_user=True,
        conversation_timeout=900
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(start_button_callback, pattern="main_menu"))
    app.add_handler(CallbackQueryHandler(ldr_callback, pattern="ldr"))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(mfr_callback, pattern="mfr"))
    app.add_handler(CallbackQueryHandler(var_callback, pattern="var"))
    app.add_handler(CallbackQueryHandler(contacts_callback, pattern="contacts"))
    app.add_handler(CallbackQueryHandler(other_questions_callback, pattern="other_questions"))
    app.add_handler(CallbackQueryHandler(cancel, pattern="cancel"))

    app.run_polling()

if __name__ == "__main__":
    main()
