import requests, os, re, logging, sqlite3, telebot
from bs4 import BeautifulSoup
from telebot import types
from sqlite3 import Error

TOKEN = os.getenv('TELEGRAM_TOKEN')

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG) # Outputs debug messages to console.


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
    except Error as e:
        print(e)

    return conn


def select_latest_record(conn, bank):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {bank} WHERE ID = (SELECT MAX(id) FROM {bank});")

    rows = cur.fetchall()

    return rows


# Function definition is here
def get_exchange_rate(conn, operation='none', currency='none', bank='absolute', isdate=0):

    full_data=select_latest_record(conn, bank)

    usd_buy = full_data[0][1]
    usd_sell = full_data[0][2]
    eur_buy = full_data[0][3]
    eur_sell = full_data[0][4]
    date = full_data[0][6]

    if currency == 'usd':
        if operation == 'buy':
            return usd_buy;
        elif operation == 'sell':
            return usd_sell;
    elif currency == 'eur':
        if operation == 'buy':
            return eur_buy;
        elif operation == 'sell':
            return eur_sell;

    if isdate == 1:
        return date


def main():
    database = r"/usr/src/app/db/currency.db"
    # create a database connection
    conn = create_connection(database)

    with conn:

        bot = telebot.TeleBot(TOKEN)

        markup = telebot.types.ReplyKeyboardMarkup()
        itembtn_usdsell = types.KeyboardButton('Курс продажи BYN->USD')
        itembtn_usdbuy = types.KeyboardButton('Курс покупки USD->BYN')
        itembtn_eursell = types.KeyboardButton('Курс продажи BYN->EUR')
        itembtn_eurbuy = types.KeyboardButton('Курс покупки EUR->BYN')
        markup.row(itembtn_usdsell, itembtn_eursell)
        markup.row(itembtn_usdbuy, itembtn_eurbuy)


        @bot.message_handler(commands=['start'])
        def start_message(message):
            bot.send_message(message.chat.id, 'Привет, на клавиатуре ниже Вы можете выбрать интересующий Вас курс. \n\nИли отправьте боту сумму, которую Вы желаете купить (в валюте), и он посчитает, сколько Вам потребуется BYN', reply_markup=markup)


        @bot.message_handler(content_types=['text'])
        def send_text(message):
            if message.text.lower() == 'курс продажи byn->usd':
                bot.send_message(message.chat.id, "== Курс продажи 1 USD ==="
                + "\nОбновлено: " + (str(get_exchange_rate(conn, isdate=1))).replace('T', ' ')
                + "\n\nФрансаБанк: " + str(get_exchange_rate(conn, 'sell', 'usd', 'fransabank')) + " BYN"
                + "\nАбсолютБанк: " + str(get_exchange_rate(conn, 'sell', 'usd', 'absolute')) + " BYN"
                + "\nПаритетБанк: " + str(get_exchange_rate(conn, 'sell', 'usd', 'paritet')) + " BYN")
            elif message.text.lower() == 'курс покупки usd->byn':
                bot.send_message(message.chat.id, "== Курс покупки 1 USD ==="
                + "\nОбновлено: " + (str(get_exchange_rate(conn, isdate=1))).replace('T', ' ')
                + "\n\nФрансаБанк: " + str(get_exchange_rate(conn, 'buy', 'usd', 'fransabank')) + " BYN"
                + "\nАбсолютБанк: " + str(get_exchange_rate(conn, 'buy', 'usd', 'absolute')) + " BYN"
                + "\nПаритетБанк: " + str(get_exchange_rate(conn, 'buy', 'usd', 'paritet')) + " BYN")

            elif message.text.lower() == 'курс продажи byn->eur':
                bot.send_message(message.chat.id, "== Курс продажи 1 EUR ==="
                + "\nОбновлено: " + (str(get_exchange_rate(conn, isdate=1))).replace('T', ' ')
                + "\n\nФрансаБанк: " + str(get_exchange_rate(conn, 'sell', 'eur', 'fransabank')) + " BYN"
                + "\nАбсолютБанк: " + str(get_exchange_rate(conn, 'sell', 'eur', 'absolute')) + " BYN"
                + "\nПаритетБанк: " + str(get_exchange_rate(conn, 'sell', 'eur', 'paritet')) + " BYN")
            elif message.text.lower() == 'курс покупки eur->byn':
                bot.send_message(message.chat.id, "== Курс покупки 1 EUR ==="
                + "\nОбновлено: " + (str(get_exchange_rate(conn, isdate=1))).replace('T', ' ')
                + "\n\nФрансаБанк: " + str(get_exchange_rate(conn, 'buy', 'eur', 'fransabank')) + " BYN"
                + "\nАбсолютБанк: " + str(get_exchange_rate(conn, 'buy', 'eur', 'absolute')) + " BYN"
                + "\nПаритетБанк: " + str(get_exchange_rate(conn, 'buy', 'eur', 'paritet')) + " BYN")

            elif re.search('\w', message.text):

                try:
                    i = int(message.text)
                    fb_usd = get_exchange_rate(conn, 'sell', 'usd', 'fransabank')
                    ab_usd = get_exchange_rate(conn, 'sell', 'usd', 'absolute')
                    pb_usd = get_exchange_rate(conn, 'sell', 'usd', 'paritet')
                    r_fb_usd = i * fb_usd
                    r_ab_usd = i * ab_usd
                    r_pb_usd = i * pb_usd

                    bot.send_message(message.chat.id, "=== USD ==="
                    + "\nОбновлено: " + (str(get_exchange_rate(conn, isdate=1))).replace('T', ' ')
                    )

                    bot.send_message(message.chat.id, "ФрансаБанк: " + str(round(r_fb_usd,2)) + " BYN"
                    + "\nАбсолютБанк: " + str(round(r_ab_usd,2)) + " BYN"
                    + "\nПаритетБанк: " + str(round(r_pb_usd,2)) + " BYN")

                    fb_eur = get_exchange_rate(conn, 'sell', 'eur', 'fransabank')
                    ab_eur = get_exchange_rate(conn, 'sell', 'eur', 'absolute')
                    pb_eur = get_exchange_rate(conn, 'sell', 'eur', 'paritet')
                    r_fb_eur = i * fb_eur
                    r_ab_eur = i * ab_eur
                    r_pb_eur = i * pb_eur

                    bot.send_message(message.chat.id, "=== EUR ===")
                    bot.send_message(message.chat.id, "ФрансаБанк: " + str(round(r_fb_eur,2)) + " BYN"
                    + "\nАбсолютБанк: " + str(round(r_ab_eur,2)) + " BYN"
                    + "\nПаритетБанк: " + str(round(r_pb_eur,2)) + " BYN")
                except:
                     bot.send_message(message.chat.id, "Вы ввели неверные данные")


        bot.polling()

if __name__ == '__main__':
    main()
