from binance.client import Client
from config.settings import API_KEY, API_SECRET, TRADE_SYMBOL, TRADE_QUANTITY
import pandas as pd
import time

from strategies.hedge_strategy import open_long_position, open_short_position, close_long_position, close_short_position

# Подключаемся к Binance Futures
client = Client(API_KEY, API_SECRET, tld="com", testnet=True)

# Периоды для скользящих средних
SHORT_MA_PERIOD = 7
MID_MA_PERIOD = 25
LONG_MA_PERIOD = 99
INTERVAL = '3m'  # Используем 3-минутный таймфрейм

# Порог прибыли для закрытия позиции
PROFIT_THRESHOLD = 5.0  # $5

# Функция для получения данных и расчета скользящих средних
def get_moving_averages():
    try:
        klines = client.futures_klines(symbol=TRADE_SYMBOL, interval=INTERVAL, limit=LONG_MA_PERIOD + 1)
        df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 
                                           'close_time', 'quote_asset_volume', 'number_of_trades', 
                                           'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
        df['close'] = pd.to_numeric(df['close'])
        df['ma_short'] = df['close'].rolling(window=SHORT_MA_PERIOD).mean()
        df['ma_mid'] = df['close'].rolling(window=MID_MA_PERIOD).mean()
        df['ma_long'] = df['close'].rolling(window=LONG_MA_PERIOD).mean()
        return df.iloc[-1]  # Возвращаем последнюю строку с текущими значениями
    except Exception as e:
        print("Ошибка при расчете скользящих средних:", e)
        return None

# Функция для проверки текущих позиций
def get_current_position():
    try:
        positions = client.futures_position_information(symbol=TRADE_SYMBOL)
        for pos in positions:
            if float(pos['positionAmt']) != 0:  # Проверяем, есть ли открытая позиция
                return pos
        return None
    except Exception as e:
        print("Ошибка при получении позиций:", e)
        return None

# Функция для открытия позиции на основе скользящих средних
def open_position_based_on_ma():
    current_position = get_current_position()
    if current_position:
        print("Позиция уже открыта. Не открываем новую.")
        return

    ma_data = get_moving_averages()
    if ma_data is None:
        return

    short_ma = ma_data['ma_short']
    mid_ma = ma_data['ma_mid']
    long_ma = ma_data['ma_long']
    print(f"Текущие значения: MA(7)={short_ma}, MA(25)={mid_ma}, MA(99)={long_ma}")

    if short_ma > mid_ma > long_ma:
        print("Сигнал на открытие лонг позиции")
        open_long_position()
    elif short_ma < mid_ma < long_ma:
        print("Сигнал на открытие шорт позиции")
        open_short_position()

# Функция для проверки прибыли и закрытия позиции
def check_profit_and_close_position():
    position = get_current_position()
    if not position:
        print("Нет открытых позиций для проверки.")
        return

    entry_price = float(position['entryPrice'])
    current_price = float(client.futures_mark_price(symbol=TRADE_SYMBOL)['markPrice'])
    unrealized_profit = float(position['unRealizedProfit'])

    print(f"Позиция открыта по цене: {entry_price}, Текущая цена: {current_price}, Прибыль: {unrealized_profit}")

    if unrealized_profit >= PROFIT_THRESHOLD:
        print(f"Закрываем позицию с прибылью: {unrealized_profit}")
        if float(position['positionAmt']) > 0:
            close_long_position()
        elif float(position['positionAmt']) < 0:
            close_short_position()

# Основная логика стратегии с тремя скользящими средними
def ma_strategy():
    while True:
        try:
            check_profit_and_close_position()  # Проверяем, нужно ли закрыть текущую позицию
            open_position_based_on_ma()  # Проверяем, нужно ли открыть новую позицию
            print("Цикл стратегии на основе скользящих средних завершен. Перезапуск через 3 минут...")
            time.sleep(180)  # Ожидание 3 минут (180 секунд)
        except Exception as e:
            print("Ошибка в стратегии на основе скользящих средних:", e)
            print("Перезапуск через 3 минут...")
            time.sleep(180)