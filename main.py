from strategies.hedge_strategy import hedge_trade
import time

def main():
    print("Запуск хедж-бота для Binance Futures...")

    while True:
        try:
            hedge_trade()
            print("Цикл хедж-торговли завершен. Перезапуск через 1 минуту...")
            time.sleep(60)
        except Exception as e:
            print("Ошибка в главном цикле торговли:", e)
            print("Перезапуск через 1 минуту...")
            time.sleep(60)

if __name__ == "__main__":
    main()
