from binance.client import Client
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import pytz



def mostrar_grafico_etherium():
    # Configura tu API key y Secret (Opcional, para acceder a más funcionalidades)
    # client = Client("YOUR_API_KEY", "YOUR_API_SECRET")
    client = Client()

    # Define el par de trading y el intervalo
    symbol = "ETHUSDT"
    interval = Client.KLINE_INTERVAL_1MINUTE  # Intervalo de 1 minuto

    # Establece la zona horaria local
    local_tz = pytz.timezone('Etc/GMT-5')  # Cambia 'Your_City' por tu ciudad o zona horaria


    # Obtén la hora actual y la hora de hace 24 horas
    now = datetime.datetime.now()
    start_time = now - datetime.timedelta(hours=24)

    # Convierte las fechas a timestamps en milisegundos
    start_time_str = str(int(start_time.timestamp() * 1000))
    end_time_str = str(int(now.timestamp() * 1000))

    # Obtén los datos históricos desde las últimas 24 horas
    candlesticks = client.get_klines(
        symbol=symbol,
        interval=interval,
        startTime=start_time_str,
        endTime=end_time_str
    )

    # Convertir los datos a un DataFrame de pandas
    df = pd.DataFrame(candlesticks, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
        'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
        'taker_buy_quote_asset_volume', 'ignore'
    ])

    # Convertir el timestamp a un formato legible
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms').dt.tz_localize('UTC').dt.tz_convert(local_tz)
    df['close'] = df['close'].astype(float)


    # Graficar los datos de precios de cierre
    plt.figure(figsize=(12, 6))
    plt.plot(df['timestamp'], df['close'], label='Precio ETH')

    plt.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray')

    plt.xlabel('Hora')
    plt.ylabel('Precio de Cierre (USDT)')
    plt.title('Gráfico de precios de ETH/USDT (Últimas 24 horas)')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    mostrar_grafico_etherium()