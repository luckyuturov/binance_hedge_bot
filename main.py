import argparse
import time
from strategies.hedge_strategy import hedge_trade
from strategies.ma_strategy import ma_strategy

def main(strategy):
    print(f"Запуск стратегии: {strategy}")

    if strategy == "hedge":
        while True:
            try:
                hedge_trade()
                print("Цикл хедж-торговли завершен. Перезапуск через 1 минуту...")
                time.sleep(60)
            except Exception as e:
                print("Ошибка в хедж-стратегии:", e)
                print("Перезапуск через 1 минуту...")
                time.sleep(60)
    elif strategy == "ma":
        while True:
            try:
                ma_strategy()
                print("Цикл стратегии на основе скользящих средних завершен. Перезапуск через 5 минут...")
                time.sleep(300)
            except Exception as e:
                print("Ошибка в стратегии скользящих средних:", e)
                print("Перезапуск через 5 минут...")
                time.sleep(300)
    else:
        print("Ошибка: неизвестная стратегия. Пожалуйста, выберите 'hedge' или 'ma'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Запуск торгового бота для Binance Futures")
    parser.add_argument("strategy", type=str, help="Название стратегии для запуска (например, 'hedge' или 'ma')")

    args = parser.parse_args()
    main(args.strategy)
