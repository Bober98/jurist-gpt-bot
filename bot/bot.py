from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import logging
import openai

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

API_TOKEN = "8083616114:AAGNPKZir7AYihRgb8rC_01izvejz80Kn3o"
OPENAI_API_KEY = "sk-proj-0zXcXFclFhRItLRpVlrczQppV3VjdxfLmLL-igzhx_uasJSk1LYgLApGDyPkvzY_YCEAJOZ-RMTDhL1BCnmGP3kYaM3qUDQ5yBeeVS1kcV78OvfVXDKZ5PjT-E-0mTyw_JTdJySMO0pt12NIDI6RDaOFRbsA"
openai.api_key = OPENAI_API_KEY

COURT_MODE = {}
LAW_MODE = {}
SELECTED_LAW = {}
STATE_DUTY_MODE = {}
DEBT_CHECK_MODE = {}
GPT_MODE = {}

COURT_INFO = {
    "санкт-петербург": """🏛 Суды Санкт-Петербурга:
1️⃣ Санкт-Петербургский городской суд
Адрес: ул. Бассейная, д. 6, Санкт-Петербург, 196128
Телефон: (812) 459-59-66
Сайт: https://sankt-peterburgsky.spb.sudrf.ru/modules.php?name=info_court&rid=20

2️⃣ Тринадцатый арбитражный апелляционный суд
Адрес: Суворовский пр., д. 50/52, Санкт-Петербург, 191015
Сайт: https://13aas.arbitr.ru/?tid=633200018&ysclid=m8kmseeays59872084

3️⃣ Смольнинский районный суд
Адрес: ул. Моисеенко, д. 2А, Санкт-Петербург, 191144
Телефон: (812) 401-92-57
Сайт: smolninsky.spb.sudrf.ru""",

    "москва": """🏛 Суды Москвы:
1️⃣ Московский городской суд
Адрес: ул. Богородский Вал, д. 8, Москва, 107076
Телефон: (495) 963-55-55
Сайт: https://mos-gorsud.ru/mgs/contacts

2️⃣ Девятый арбитражный апелляционный суд
Адрес: ул. Большая Тульская, д. 17, Москва, 115191
Телефон: (495) 953-85-55
Сайт: https://9aas.arbitr.ru/?additionalmenu=1&ysclid=m8kmwgvv25876901620

3️⃣ Тверской районный суд
Адрес: ул. Цветной бульвар, д. 25А, Москва, 127051
Телефон: (495) 650-59-80
Сайт: https://mos-gorsud.ru/rs/tverskoj""",

    "казань": """🏛 Суды Казани:
1️⃣ Арбитражный суд Республики Татарстан
Адрес: ул. Ново-Песочная, д. 40, Казань, 420107
Телефон: (843) 291-10-00
Сайт: https://tatarstan.arbitr.ru/

2️⃣ Советский районный суд г. Казани Республики Татарстан
Адрес: ул. Патриса Лумумбы, д. 48, Казань, 420138
Телефон: (843) 272-72-72
Сайт: https://sovetsky.tat.sudrf.ru/""",

    "новосибирск": """🏛 Суды Новосибирска:
1️⃣ Новосибирский областной суд
Адрес: ул. Писарева, д. 35, Новосибирск, 630091
Телефон: (383) 210-54-00
Сайт: https://oblsud.nsk.sudrf.ru/modules.php?name=press_dep&op=3

2️⃣ Пятый апелляционный суд общей юрисдикции
Адрес: ул. Державина, д. 28, Новосибирск, 630005
Телефон: (383) 201-00-00
Сайт: https://5ap.sudrf.ru/modules.php?name=info_court&rid=11

3️⃣ Арбитражный суд Новосибирской области
Адрес: ул. Нижегородская, д. 6, Новосибирск, 630102
Телефон: (383) 223-00-00
Сайт: www.novosibirsk.arbitr.ru"""
}

LAWYER_MODE = {}

LAWYERS_BY_CITY = {
    "санкт-петербург": """⚖️ Юристы Санкт-Петербурга:
1️⃣ Иванов Александр Дмитриевич — +7 (812) 345-12-34 — ivanov.spb@yuristmail.ru
2️⃣ Сергеева Юлия Николаевна — +7 (812) 567-89-10 — sergeeva.spb@yuristmail.ru
3️⃣ Петров Денис Владимирович — +7 (812) 432-65-47 — petrov.spb@yuristmail.ru
4️⃣ Васильева Ирина Сергеевна — +7 (812) 678-43-21 — vasilyeva.spb@yuristmail.ru
5️⃣ Никитин Роман Олегович — +7 (812) 223-56-78 — nikitin.spb@yuristmail.ru""",

    "москва": """⚖️ Юристы Москвы:
1️⃣ Смирнова Анна Викторовна — +7 (495) 123-45-67 — smirnova.msk@yuristmail.ru
2️⃣ Орлов Максим Игоревич — +7 (495) 987-65-43 — orlov.msk@yuristmail.ru
3️⃣ Кузнецов Павел Андреевич — +7 (495) 321-09-87 — kuznecov.msk@yuristmail.ru
4️⃣ Попова Дарья Михайловна — +7 (495) 654-32-10 — popova.msk@yuristmail.ru
5️⃣ Соловьёв Евгений Борисович — +7 (495) 876-54-32 — solovyev.msk@yuristmail.ru""",

    "казань": """⚖️ Юристы Казани:
1️⃣ Ахметова Лейла Рустамовна — +7 (843) 111-22-33 — ahmetova.kzn@yuristmail.ru
2️⃣ Галиев Руслан Марсович — +7 (843) 444-55-66 — galiev.kzn@yuristmail.ru
3️⃣ Муратов Тимур Рашидович — +7 (843) 777-88-99 — muratov.kzn@yuristmail.ru
4️⃣ Низамова Алия Ильдаровна — +7 (843) 222-33-44 — nizamova.kzn@yuristmail.ru
5️⃣ Хабибуллин Рафаэль Искандерович — +7 (843) 555-66-77 — habibullin.kzn@yuristmail.ru""",

    "новосибирск": """⚖️ Юристы Новосибирска:
1️⃣ Захаров Дмитрий Евгеньевич — +7 (383) 101-11-22 — zaharov.nsk@yuristmail.ru
2️⃣ Егорова Ольга Семёновна — +7 (383) 202-22-33 — egorova.nsk@yuristmail.ru
3️⃣ Федотов Алексей Геннадьевич — +7 (383) 303-33-44 — fedotov.nsk@yuristmail.ru
4️⃣ Комаров Андрей Викторович — +7 (383) 404-44-55 — komarov.nsk@yuristmail.ru
5️⃣ Лукина Екатерина Павловна — +7 (383) 505-55-66 — lukina.nsk@yuristmail.ru"""
}


MAIN_MENU = [
    ["📄 Шаблоны", "⚖️ Найти юриста"],
    ["💬 Консультация", "📚 Законы"],
    ["💰 Госпошлина", "🏛 Суд"],
    ["🔍 Проверка долгов"],
    ["❌ Завершить"]
]

TEMPLATE_MENU = [
    ["📄 Трудовой договор", "🏠 Договор аренды"],
    ["⚖️ Исковое заявление", "📑 Договор купли-продажи"],
    ["🎁 Договор дарения", "🚚 Договор поставки"],
    ["💍 Брачный договор", "🔄 Договор мены"],
    ["⬅️ Назад"]
]

LAW_MENU = [
    ["📖 Конституция РФ", "📘 Гражданский кодекс РФ"],
    ["📕 Уголовный кодекс РФ", "📗 КоАП РФ"],
    ["📙 Трудовой кодекс РФ", "🚔 Закон о полиции"],
    ["👨‍👩‍👧‍👦 Семейный кодекс РФ", "🌱 Земельный кодекс РФ"],
    ["💼 Налоговый кодекс РФ", "⬅️ Назад"]
]


# === Функция GPT ===
from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)

async def ask_gpt(question: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты опытный юрист. Отвечай чётко, по закону РФ."},
                {"role": "user", "content": question}
            ],
            temperature=0.5,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Ошибка при запросе к ChatGPT:\n\n{str(e)}"

def calculate_state_duty(amount: float) -> float:
    if amount <= 20000:
        fee = max(400, amount * 0.04)
    elif amount <= 100000:
        fee = 800 + (amount - 20000) * 0.03
    elif amount <= 200000:
        fee = 3200 + (amount - 100000) * 0.02
    elif amount <= 1000000:
        fee = 5200 + (amount - 200000) * 0.01
    else:
        fee = 13200 + (amount - 1000000) * 0.005
        fee = min(fee, 60000)
    return fee

async def start(update: Update, context: CallbackContext):
    keyboard = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)
    await update.message.reply_text("👋 Привет! Я бот ЮрКонсульт. Чем могу помочь?", reply_markup=keyboard)

async def button_handler(update: Update, context: CallbackContext):
    handled = False
    text = update.message.text.lower()
    user_id = update.message.from_user.id

    if text == "⬅️ назад":
        handled = True
        # Сброс только активных режимов
        COURT_MODE[user_id] = False
        LAW_MODE[user_id] = False
        LAWYER_MODE[user_id] = False
        STATE_DUTY_MODE[user_id] = False
        DEBT_CHECK_MODE[user_id] = False
        SELECTED_LAW[user_id] = None

        keyboard = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)
        await update.message.reply_text("🔙 Возвращаюсь в главное меню.", reply_markup=keyboard)
        return  # Обязательно: выйти после возврата в меню!

    if text == "📄 шаблоны":
        keyboard = ReplyKeyboardMarkup(TEMPLATE_MENU, resize_keyboard=True)
        await update.message.reply_text("📜 Выберите нужный шаблон:", reply_markup=keyboard)
        handled = True

    elif text == "📄 трудовой договор":
        handled = True
        try:
            with open("trudovoy.docx", "rb") as file:
                await update.message.reply_document(file, filename="trudovoy.docx")
        except FileNotFoundError:
            await update.message.reply_text("❌ Файл шаблона trudovoy.docx не найден.")

    elif text == "🏠 договор аренды":
        handled = True
        with open("arenda.docx", "rb") as file:
            await update.message.reply_document(file, filename="Договор аренды.docx")

    elif text == "⚖️ исковое заявление":
        handled = True
        with open("isk.docx", "rb") as file:
            await update.message.reply_document(file, filename="Исковое заявление.docx")

    elif text == "📑 договор купли-продажи":
        handled = True
        with open("kuplja_prodazha.docx", "rb") as file:
            await update.message.reply_document(file, filename="Договор купли-продажи.docx")

    elif text == "🎁 договор дарения":
        handled = True
        with open("dareniye.docx", "rb") as file:
            await update.message.reply_document(file, filename="Договор дарения.docx")

    elif text == "🚚 договор поставки":
        handled = True
        with open("postavka.docx", "rb") as file:
            await update.message.reply_document(file, filename="Договор поставки.docx")

    elif text == "💍 брачный договор":
        handled = True
        with open("brachniy.docx", "rb") as file:
            await update.message.reply_document(file, filename="Брачный договор.docx")

    elif text == "🔄 договор мены":
        handled = True
        with open("mena.docx", "rb") as file:
            await update.message.reply_document(file, filename="Договор мены.docx")

    if GPT_MODE.get(user_id):
        handled = True
        await update.message.reply_text("⏳ Обрабатываю ваш запрос...")
        response = await ask_gpt(text)
        await update.message.reply_text(response)



    elif text == "💬 консультация":

        handled = True

        GPT_MODE[user_id] = True

        await update.message.reply_text(

            "🧠 Напишите ваш юридический вопрос, и я постараюсь ответить с помощью ChatGPT.\n"

            "Когда закончите, нажмите '⬅️ Назад', чтобы вернуться в главное меню."

        )


    elif text == "📚 законы":
        handled = True
        LAW_MODE[user_id] = True
        keyboard = ReplyKeyboardMarkup(LAW_MENU, resize_keyboard=True)
        await update.message.reply_text("📚 Выберите закон или кодекс:", reply_markup=keyboard)
        handled = True
        GPT_MODE[user_id] = False

    elif LAW_MODE.get(user_id) and text in [
        "📖 конституция рф", "📘 гражданский кодекс рф", "📕 уголовный кодекс рф",
        "📗 коап рф", "📙 трудовой кодекс рф", "🚔 закон о полиции",
        "👨‍👩‍👧‍👦 семейный кодекс рф", "🌱 земельный кодекс рф", "💼 налоговый кодекс рф"]:
        SELECTED_LAW[user_id] = text
        await update.message.reply_text("🔢 Введите номер статьи:")
        handled = True
        GPT_MODE[user_id] = False

    elif text.isdigit() and SELECTED_LAW.get(user_id):
        law_name = SELECTED_LAW[user_id][2:].capitalize()
        await update.message.reply_text(f"📜 Статья {text} {law_name}:")
        handled = True
        SELECTED_LAW[user_id] = None
        LAW_MODE[user_id] = False
    user_id = update.message.from_user.id


    if text == "💰 госпошлина":
        handled = True
        STATE_DUTY_MODE[user_id] = True
        await update.message.reply_text("💰 Введите сумму иска для расчета госпошлины (в рублях):")

    elif STATE_DUTY_MODE.get(user_id):
        handled = True
        try:
            amount = float(text.replace(",", "."))
            fee = calculate_state_duty(amount)
            await update.message.reply_text(f"✅ Размер госпошлины при сумме иска {amount:.2f} ₽ составляет: {fee:.2f} ₽")
        except ValueError:
            await update.message.reply_text("❌ Пожалуйста, введите сумму цифрами (например, 15000).")
        STATE_DUTY_MODE[user_id] = False
        GPT_MODE[user_id] = False

    elif text == "🏛 суд":
        handled = True
        COURT_MODE[user_id] = True
        court_keyboard = ReplyKeyboardMarkup([
            ["Санкт-Петербург", "Москва"],
            ["Казань", "Новосибирск"],
            ["⬅️ Назад"]
        ], resize_keyboard=True)
        await update.message.reply_text("🏛 Выберите город:", reply_markup=court_keyboard)
        GPT_MODE[user_id] = False

    elif COURT_MODE.get(user_id):
        handled = True
        city = text.lower()
        info = COURT_INFO.get(city)
        if info:
            await update.message.reply_text(info)
        else:
            await update.message.reply_text(
                "❌ Информация о судах для данного города отсутствует. Попробуйте другой город.")
        COURT_MODE[user_id] = False
        GPT_MODE[user_id] = False

    elif text == "⚖️ найти юриста":

        handled = True

        LAWYER_MODE[user_id] = True

        lawyer_keyboard = ReplyKeyboardMarkup([

            ["Санкт-Петербург", "Москва"],

            ["Казань", "Новосибирск"],

            ["⬅️ Назад"]

        ], resize_keyboard=True)
        GPT_MODE[user_id] = False
        await update.message.reply_text("⚖️ Выберите город для поиска юристов:", reply_markup=lawyer_keyboard)



    elif LAWYER_MODE.get(user_id):

        handled = True

        city_key = text.lower()

        if city_key in LAWYERS_BY_CITY:

            await update.message.reply_text(LAWYERS_BY_CITY[city_key])

        else:

            await update.message.reply_text("❌ Информация о юристах в этом городе пока недоступна.")

        LAWYER_MODE[user_id] = False
        GPT_MODE[user_id] = False

    elif text == "🔍 проверка долгов":
        handled = True
        DEBT_CHECK_MODE[user_id] = True
        await update.message.reply_text("🔍 Введите ИНН или ФИО для проверки задолженности:")
        GPT_MODE[user_id] = False
    elif DEBT_CHECK_MODE.get(user_id):
        handled = True
        query = text.strip()
        await update.message.reply_text(
    f"🔎 Проверяю данные по: {query}...\n\n"
    "⚠️ Прямая интеграция с ФССП и Налог.ру пока недоступна.\n"
    "Вы можете проверить вручную:\n\n"
    "ФССП: https://fssp.gov.ru\n"
    "Налоговая: https://service.nalog.ru/zd.do"
)
        DEBT_CHECK_MODE[user_id] = False
        GPT_MODE[user_id] = False


def main():
    application = Application.builder().token(API_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler))
    logger.info("✅ Бот запущен.")
    application.run_polling()



if __name__ == "__main__":
    main()