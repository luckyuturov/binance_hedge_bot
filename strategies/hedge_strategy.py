from binance.client import Client
from config.settings import API_KEY, API_SECRET, TRADE_SYMBOL, TRADE_QUANTITY
import time

# Подключаемся к Binance Futures
client = Client(API_KEY, API_SECRET, tld="com", testnet=True)

# Функция для проверки текущих позиций
def get_current_positions():
    try:
        positions = client.futures_position_information(symbol=TRADE_SYMBOL)
        long_position = next((pos for pos in positions if pos['positionSide'] == 'LONG'), None)
        short_position = next((pos for pos in positions if pos['positionSide'] == 'SHORT'), None)

        return long_position, short_position

    except Exception as e:
        print("Ошибка при получении позиций:", e)
        return None, None

# Функция для открытия лонг позиции
def open_long_position():
    long_position, _ = get_current_positions()
    
    if long_position and float(long_position['positionAmt']) > 0:
        print(f"Лонг позиция уже открыта по цене: {long_position['entryPrice']}")
        return float(long_position['entryPrice'])

    try:
        order = client.futures_create_order(
            symbol=TRADE_SYMBOL,
            side="BUY",
            positionSide="LONG",
            type="MARKET",
            quantity=TRADE_QUANTITY
        )
        long_open_price = float(client.futures_position_information(symbol=TRADE_SYMBOL)[0]['entryPrice'])
        print(f"Лонг позиция открыта по цене: {long_open_price}")
        return long_open_price
    except Exception as e:
        print("Ошибка при открытии лонг позиции:", e)
        return None

# Функция для открытия шорт позиции
def open_short_position():
    _, short_position = get_current_positions()

    if short_position and float(short_position['positionAmt']) < 0:
        print(f"Шорт позиция уже открыта по цене: {short_position['entryPrice']}")
        return float(short_position['entryPrice'])

    try:
        order = client.futures_create_order(
            symbol=TRADE_SYMBOL,
            side="SELL",
            positionSide="SHORT",
            type="MARKET",
            quantity=TRADE_QUANTITY
        )
        short_open_price = float(client.futures_position_information(symbol=TRADE_SYMBOL)[1]['entryPrice'])
        print(f"Шорт позиция открыта по цене: {short_open_price}")
        return short_open_price
    except Exception as e:
        print("Ошибка при открытии шорт позиции:", e)
        return None

# Функция для закрытия лонг позиции
def close_long_position():
    try:
        order = client.futures_create_order(
            symbol=TRADE_SYMBOL,
            side="SELL",
            positionSide="LONG",  # Указываем, что закрываем лонг позицию
            type="MARKET",
            quantity=TRADE_QUANTITY,
            reduce_only=True
        )
        print("Лонг позиция закрыта:", order)
    except Exception as e:
        print("Ошибка при закрытии лонг позиции:", e)

# Функция для закрытия шорт позиции
def close_short_position():
    try:
        order = client.futures_create_order(
            symbol=TRADE_SYMBOL,
            side="BUY",
            positionSide="SHORT",  # Указываем, что закрываем шорт позицию
            type="MARKET",
            quantity=TRADE_QUANTITY,
            reduce_only=True
        )
        print("Шорт позиция закрыта:", order)
    except Exception as e:
        print("Ошибка при закрытии шорт позиции:", e)

# Функция для проверки прибыли и закрытия прибыльной позиции
def check_profit_and_close_position():
    try:
        # Получаем информацию о текущих позициях
        long_position, short_position = get_current_positions()
        
        # Текущая цена
        current_price = float(client.futures_mark_price(symbol=TRADE_SYMBOL)['markPrice'])
        print(f"Текущая цена: {current_price}")

        # Рассчитываем PNL (прибыль/убыток)
        if long_position:
            long_pnl = float(long_position['unRealizedProfit'])
            print(f"Текущая прибыль по лонг позиции: {long_pnl}")
            if long_pnl >= 3:
                print(f"Закрытие лонг позиции с прибылью: {long_pnl}")
                close_long_position()
                open_long_position()
        
        if short_position:
            short_pnl = float(short_position['unRealizedProfit'])
            print(f"Текущая прибыль по шорт позиции: {short_pnl}")
            if short_pnl >= 3:
                print(f"Закрытие шорт позиции с прибылью: {short_pnl}")
                close_short_position()
                open_short_position()

    except Exception as e:
        print("Ошибка при проверке прибыли/убытка:", e)

# Основная логика хеджирования
def hedge_trade():
    open_long_price = open_long_position()
    open_short_price = open_short_position()

    if open_long_price and open_short_price:
        while True:
            # Проверяем PNL и закрываем позиции, если необходимо
            check_profit_and_close_position()

            print("\n=== Открытые сделки ===\n")
            # get_open_positions()
            # time.sleep(5)
    else:
        print("Ошибка: не удалось открыть обе позиции.")    
