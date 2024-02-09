from confluent_kafka import Producer
from requests import get
import time
import json


URL = 'https://production.api.coindesk.com/v2/tb/price/ticker?assets='


def main():

    # Algo pour récupérer toutes les cryptos disponibles sur l'api
    #match = re.findall(r'\[([^]]+)]', json_data['message'])
    #symbols = re.sub(r'\s+', '', match[1])

    # Liste de cryptos à récupérer si on ne veut pas toutes les cryptos disponibles
    symbols = "BTC,ETH,XRP,BCH,ADA,XLM,NEO,LTC"

    print("Récupération des cryptomonnaies :", symbols)
    final_url = URL + symbols

    p = Producer({'bootstrap.servers': 'localhost:9093'})

    i = 0
    while i < 100000:
        result = get(final_url)
        json_data = result.json()

        p.produce('topic1', value=json.dumps(json_data).encode('utf-8'), callback=delivery_report)
        p.flush()

        time.sleep(1)
        i = i + 1


def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")


if __name__ == '__main__':
    main()
