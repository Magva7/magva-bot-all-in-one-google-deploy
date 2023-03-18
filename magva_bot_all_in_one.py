# версия 3.0 - работает запрос курсов МИР и МИГ, баш и запрос местоположения и погоды
import telebot
import requests  # для запроса адреса по координатам через яндекс и погоды через openweather
import lxml  # pip install lxml для распарсивания страницы
import re  # регулярки
from bs4 import BeautifulSoup
import random  # для выбора рандомной цитаты с из текстового файла с цитатами баша
from telebot import types
import datetime
from datetime import datetime, timedelta  # для перевода времени с UTC на человеческий
import os
os.system('cls||clear')  # очистка консоли перед запуском

bot = telebot.TeleBot('1706338684:AAGojuK3Xw50cqr1osXwC6uvTRql0gQ-5cw')  # Создаем бота
ya_token = 'a080eb21-a250-4036-8bee-7b2c7e97f34a'
open_wea_api_key = '2745926c9f2ffb7903aec82510e1bc65'

# ======= Блок приветствия и отрисовки кнопок ===================
@bot.message_handler(commands=["start"]) # прослушивание команды start и действия при ее получении
def send_hi_and_button(message, res=False): # функция, внутрь которой передаем объект message, у которого
    # есть мноооожество свойств, свойства объекта message- это текст сообщения и данные того
    # человека, который отправил боту команду start, т.е. id телеги этого человека, его ник и т.д.

    # ===Создаем клавиатуру с кнопками=======================
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)     # Оснастка для кнопок

    button_kurs = types.KeyboardButton("Курс")
    markup.add(button_kurs)

    button_bash = types.KeyboardButton("Баш")
    markup.add(button_bash)

    button_geo = types.KeyboardButton(text="Мое местоположение и погода", request_location=True)  # сама кнопка
    markup.add(button_geo)  # добавляем кнопку в оснастку

    # button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)  # сама кнопка
    # markup.add(button_geo)  # добавляем кнопку в оснастку
    # =======================================================================

    # Бот отправляет приветствие и отрисованную кнопку
    bot.send_message(message.chat.id, 'Нажмите кнопку', reply_markup=markup)  # при получении команды /start бот будет
    # отправлять сообщение 'Нажми кнопку', создавать и отправлять список кнопок

    print('Бот получил от юзверя', message.from_user.username, 'команду start, отправил ему '
                                                               'приветствие, и отрисованную кнопку.')
    # print(message)  # для интереса содержимое объекта message, т.е. все данные по тому человеку, который написал
# ============================================

# Прослушивание текстового сообщения start
# ============================================

# ======= Прослушивание команды /ping ===================
@bot.message_handler(commands=['ping'])
def send_welcome(message):
    bot.reply_to(message, f'pong')
    print('Получена команда ping, отправлен ответ')
# ========================================================

# ======= Прослушивание текстовых сообщений и echo бот ===================
@bot.message_handler(content_types=["text"])  # если пришел текст
def handle_text(message):
    if message.text == 'ping':  # если юзер написал ping текстом
        bot.send_message(message.chat.id, 'pong')
        print('Получен текст: ', message.text, ', отправлен ответ pong')
    elif message.text.strip() == 'Курс':  # если пришел текст "Курс", или юзер нажал на одноименную кнопкку
        answer = check_kurs_mir() + '\n' + check_kurs_mig()
        print('Запрошены и отправлен курсы МИР и МИГ')
    elif message.text.strip() == 'Баш':  # Если юзер нажал на кнопку, выдаем баш
        answer = random.choice(bash_citata)  # в переменную answer записывается рандомная цитата
        print('Запрошена и отправлена цитатка с баща')
    else:  # если написал любой другой текст
        answer = 'Вы написали: ' + message.text  # echo
        print('Получен текст: ', message.text, ', отправлен ответ')

    bot.send_message(message.chat.id, answer)  # отправка в чат содержимого переменной answer
# ========================================================

# ======= Парсинг курсов ===================
# Парсинг курса МИР - функция обращается к странице, парсит ее и возвращает курс
def check_kurs_mir():
    # магия, чтобы запрос отработал
    param = {'pagenumber':6}
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36 OPR/58.0.3135.79'}

    url = 'https://mironline.ru/support/list/kursy_mir/?sphrase_id=113984'
    res = requests.get(url,params=param,headers=headers)

    page = res.text  # вся страница

    page2 = BeautifulSoup(page, 'lxml')  # распарсиваем страницу в переменную
    results = page2.find_all('tr', '')  # записываем в переменную содержимое всех тегов tr

    i = 0
    for result in results:  # перебираем все теги tr и выводим их содержимое
        i = i + 1
        if i == 5:  # наш курс 6-ой по списку
            tenge_kurs_string = result.text  # записываем его в строку

    tenge_kurs_list_view = re.findall(r'0,\d{5}', tenge_kurs_string) # ищем в строке цифры
    tenge_kurs_str = tenge_kurs_list_view[0]  # берем первый элемент из списка
    tenge_kurs_str = tenge_kurs_str.replace(',', '.')  # меняем запятую на точку
    tenge_kurs_num = float(tenge_kurs_str)  # переводим во float
    tenge_kurs_num = 1/tenge_kurs_num  # делим на 1, чтобы курс был в человеческом формате
    tenge_kurs_num = round(tenge_kurs_num, 2)  # округляем до 2 знаков после запятой
    tenge_kurs_result = 'Курс МИР: ' + str(tenge_kurs_num)
    print('Запрошен курс МИР, сейчас курс: ', tenge_kurs_num)
    return tenge_kurs_result


# check_kurs_mir()
# ========================================================

# Парсинг курса МИГ - функция обращается к странице, парсит ее и возвращает курс
def check_kurs_mig():
    url = 'https://www.mig.kz/'
    res = requests.get(url)

    page = res.text  # вся страница
    page2 = BeautifulSoup(page, 'lxml')  # распарсиваем страницу в переменную
    results = page2.find_all('tr', '')  # записываем в переменную содержимое всех тегов tr

    i = 0
    for result in results:  # перебираем все теги tr и выводим их содержимое
        i = i + 1
        if i == 3:  # наш курс 3-ий по списку
            tenge_kurs_mig_string = result.text  # записываем его в строку

    tenge_kurs_mig_list_view = re.findall(r'\d{1}.\d+', tenge_kurs_mig_string) # ищем в строке цифру, потом точку и опять цифру
    tenge_kurs_mig_str = tenge_kurs_mig_list_view[0]  # берем первый элемент из списка
    tenge_kurs_mig_result = 'Курс МИГ: ' + tenge_kurs_mig_str
    print('Запрошен курс МИГ, сейчас курс: ', tenge_kurs_mig_str)
    return tenge_kurs_mig_result


# =======  Загружаем баш =================================
temp_var_for_open_bash = open('data/bash.txt', 'r', encoding='UTF-8')
bash_citata = temp_var_for_open_bash.read().split('000')
temp_var_for_open_bash.close()
# ========================================================

# Блок получения координат и ответа об этом пользователю
@bot.message_handler(content_types=['location'])  # прослушивание, что боту передали координаты
def location(message):
    if message.location is not None:  # если передали не пустые данные
        koordinaty = message.location  # полные координаты

        latitude = str(koordinaty.latitude)  # 43.209693
        longitude = str(koordinaty.longitude) # 76.869619

        # ==== Яндекс - адрес по координатам ==================================
        base_url_ya = 'https://geocode-maps.yandex.ru/1.x?format=json&lang=ru_RU&kind=house&geocode='
        final_url_ya = base_url_ya + longitude + ',' + latitude + '&apikey=' + ya_token
        address_data = requests.get(final_url_ya).json()

        # вытаскиваем из всего пришедшего json именно строку с полным адресом.
        address_str = address_data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"][
                    "metaDataProperty"]["GeocoderMetaData"]["AddressDetails"]["Country"][
                    "AddressLine"]
        # =====================================================================

        # ==== Openweather - получение текущей погоды и почасового прогноза погодыпо координатам ==========
        # final_url_current_wea_manual = 'http://api.openweathermap.org/data/2.5/weather?appid=2745926c9f2ffb7903aec82510e1bc65&lat=43.209693&lon=76.869619&units=metric&lang=RU' # полный url для проверки в браузере
        # final_url_forecast_wea_manual = 'https://api.openweathermap.org/data/2.5/onecall?appid=2745926c9f2ffb7903aec82510e1bc65&lat=43.209693&lon=76.869619&units=metric&lang=RU'

        base_url_open_weat = "http://api.openweathermap.org/data/2.5/onecall?"
        final_url_current_wea = base_url_open_weat + "appid=" + open_wea_api_key + "&lat=" + latitude + "&lon=" + longitude + '&units=metric&lang=RU'

        forecast_wea_data = requests.get(final_url_current_wea).json()  # запрашиваем погоду

        # распарсиваем результат
        timezone_offset = forecast_wea_data['timezone_offset']  # смещение часового пояса в секундах

        # проверяем температуру, если больше нуля, то добавляем +
        temp_for_check = round(forecast_wea_data['current']['temp'])
        if temp_for_check > 0:
            temp_for_check = '+' + str(temp_for_check)
        # print(temp_for_check)

        current_temp = '\nСейчас:  ' + '' + str(temp_for_check) + ' по цельсию'
        current_wind = 'Ветер:  ' + str(round(forecast_wea_data['current']['wind_speed'])) + ' м/с'
        current_rain = forecast_wea_data['current']['weather'][0]['description']  # осадки

        current_weather = current_temp + '\n' + current_wind + ', ' + current_rain  # погода на текущий момент

        # почасовой прогноз на ближайшие 4 часа, первый результат пропускаем, т.к. в нем текущая погода, мы её уже показали
        all_forecast = ''  # все прогнозы
        i = 1
        while i < 5:
            my_this_forecast = forecast_wea_data['hourly'][i]  # погода в первом прогнозе
            my_this_forecast_time_unix = my_this_forecast['dt']  # время в первом прогнозе в unix формате
            # my_this_forecast_time_human = datetime.utcfromtimestamp(my_this_forecast_time_unix).strftime('%H:%M')  # время
            # без смещения
            my_this_forecast_time_human = (datetime.utcfromtimestamp(my_this_forecast_time_unix) + timedelta(hours=(
                    timezone_offset / 3600))).strftime('%H:%M')  # смещение времени


            # проверяем температуру в каждом прогнозе, если больше 0, добавляем +
            check_my_this_forecast_temp = round(my_this_forecast['temp'])
            if check_my_this_forecast_temp > 0:
                check_my_this_forecast_temp = '+' + str(check_my_this_forecast_temp)
            my_this_forecast_temp = str(check_my_this_forecast_temp)  # температура в первом прогнозе

            # проверяем температуру, которая ощущается в каждом прогнозе, если больше 0, добавляем +
            check_my_this_forecast_feels_like = round(my_this_forecast['feels_like'])
            if check_my_this_forecast_feels_like > 0:
                check_my_this_forecast_feels_like = '+' + str(check_my_this_forecast_feels_like)
            my_this_forecast_feels_like = ' ощущается как ' + str(check_my_this_forecast_feels_like)  # температура, как ощущается


            # my_this_forecast_wind_speed = 'Ветер:  ' + str(
            #     round(my_this_forecast['wind_speed'])) + ' м/с'  # скорость ветра
            my_this_forecast_rain = my_this_forecast['weather'][0]['description']  # осадки

            my_this_forecast_sum = my_this_forecast_time_human + '  ' + \
                                   my_this_forecast_temp + \
                                   ',' + my_this_forecast_feels_like + ', ' + my_this_forecast_rain

            all_forecast += my_this_forecast_sum + '\n'

            # print(my_this_forecast_sum)
            i = i + 1
        final_forecast = '\n\nПогода на ближайшие часы:\n' + all_forecast

        # === Отправка сообщения ботом пользователю =============
        bot.send_message(message.chat.id, "Координаты приняты, Ваш адрес:\n" + address_str +
        current_weather + final_forecast)

        # === Записываем координаты, которые получили от юзверя в текстовый файл
        message_for_txt_and_console = 'В такое-то время ' + 'получены координаты от юзверя с ником ' + message.from_user.username + ', id' + str(message.from_user.id) +', он находится тут: ' + address_str
        with open('location_log.txt', 'a') as f:
            f.write(str(message_for_txt_and_console))
            f.write('\n')

        # выводим то же самое в консоль
        print(message_for_txt_and_console)

bot.polling(none_stop=True)
input()
