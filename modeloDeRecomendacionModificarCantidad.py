from tvDatafeed import TvDatafeed, Interval
import pandas as pd
import json
import time
import requests
import pyodbc

from tkinter import messagebox


def get_current_price(symbol):
    if symbol == 'BTCUSD':
        moneda = "bitcoin"
    elif symbol == 'ETHUSD':
        moneda = "ethereum"
    elif symbol == 'DOGEUSD':
        moneda = "dogecoin"
    try:
        # CoinGecko usa símbolos en minúsculas y con guiones bajos
        moneda = moneda.lower().replace('/', '-')

        url = f'https://api.coingecko.com/api/v3/simple/price?ids={moneda}&vs_currencies=usd'
        response = requests.get(url)
        response.raise_for_status()  # Lanza una excepción para códigos de estado HTTP 4xx/5xx
        data = response.json()
        print(f"Respuesta de la API: {data}")
        if moneda in data and 'usd' in data[moneda]:
            return data[moneda]['usd']
        else:
            print(f"Error: No se encontró el precio para {moneda}")
            return None
    except Exception as e:
        print(f"Error al obtener el precio de {moneda}: {e}")
        return None


def save_price_to_db(currency_id, price, conexion):
    try:
        if conexion.closed:
            conexion = pyodbc.connect('DRIVER={SQL Server}; SERVER=DESKTOP-05H4Q3D\\TEW_SQLEXPRESS; DATABASE=proyectoSistemas; UID=soporte; PWD=123')

        cursor = conexion.cursor()
        cursor.execute('''
            UPDATE currencies
            SET price = ?,  -- El nuevo precio que deseas establecer
            price_date = GETDATE()  -- La fecha y hora actuales
            WHERE currency_id = ?;
        ''', (price, currency_id))
        conexion.commit()
    except Exception as e:
        print(f"Error al guardar el precio en la base de datos: {e}")
    finally:
        if not conexion.closed:
            cursor.close()

def buy_crypto(symbol, amount, price,conexion,capital_inicial, user_id):
    if symbol == 1:
        moneda = 'BTCUSD'
    elif symbol == 3:
        moneda = 'ETHUSD'
    elif symbol == 8:
        moneda = 'DOGEUSD'
    conn = conexion.cursor()
    try:
        conn.execute('''
            SELECT * FROM accounts where user_id = ? ''', (user_id))
        result = conn.fetchone()
        if result is None:
            conn.execute('''
            INSERT INTO accounts (user_id, initial_balance, current_balance)
            VALUES (?, ?, ?)
        ''', (user_id, capital_inicial,capital_inicial - price*amount))
            conexion.commit()
        else:
            conn.execute('''
            UPDATE accounts
            SET current_balance = current_balance - ?
            WHERE user_id = ?;
        ''', (amount*price, user_id))
            conexion.commit()

        conn.execute('''
            INSERT INTO transactions (symbol, action, amount, price)
            VALUES (?, 'buy', ?, ?)
        ''', (moneda, amount, price))
        conexion.commit()
        """Aca se va a guardar en el portafolio las criptomoneads que se tengan"""
        conn.execute('''
            SELECT * FROM portfolio where user_id = ? and currency_id = ?''' , (user_id,symbol))
        result = conn.fetchone()
    

        if result is None:
            conn.execute('''
            INSERT INTO portfolio (user_id, currency_id, amount, value)
            VALUES (?, ?, ?,?)
        ''', (user_id,symbol, amount, price))
            conexion.commit()
        else:
            if result is not None:
                conn.execute('''
            UPDATE portfolio
            SET amount = amount + ?, value = ?, last_updated = GETDATE()
            WHERE user_id = ? and currency_id = ?;
        ''', (amount,price ,user_id, symbol))
                conexion.commit()
        print(f"Bought {amount} of {symbol} at {price}")
    except Exception as e:
        conexion.rollback()
        print(f"Error al insertar datos: {e}")
    finally:
        conn.close()

def sell_crypto(symbol, amount, price, conexion,user_id):
    if symbol == 1:
        moneda = 'BTCUSD'
    elif symbol == 3:
        moneda = 'ETHUSD'
    elif symbol == 8:
        moneda = 'DOGEUSD'
    conn = conexion
    cursor = conn.cursor()
    cursor.execute('''
            UPDATE accounts
            SET current_balance = current_balance + ?, last_updated = GETDATE()
            WHERE user_id = ?;
        ''', (amount*price, user_id))
    conn.commit()
    cursor.execute(f'''
        INSERT INTO transactions (symbol, action, amount, price)
        VALUES ({moneda}, 'sell', {amount}, {price})
    ''')
    conn.commit()
    cursor.execute('''
            UPDATE portfolio
            SET amount = amount - ?, value = ?,
            WHERE user_id = ? and currency_id = ?;
        ''', (amount,price ,user_id, symbol))
    conn.commit()
    cursor
    

    conn.close()
    print(f"Sold {amount} of {symbol} at {price}")

def get_crypto_data(symbol, exchange, interval, n_bars):
    tv = TvDatafeed()
    data = tv.get_hist(symbol=symbol, exchange=exchange, interval=interval, n_bars=n_bars)
    return data

def calculate_rsi(data, window):
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def get_amount_to_trade(conexion, currency_id):
    try:
        cursor = conexion.cursor()
        cursor.execute('''
            SELECT price
            FROM currencies
            WHERE currency_id = ?
        ''', (currency_id,))
        result = cursor.fetchone()
        return result[0] if result else 1
    except Exception as e:
        print(f"Error al obtener la cantidad a comerciar: {e}")
        return 1

def update_amount_to_trade(new_amount, file_path='amount.json'):
    with open(file_path, 'w') as file:
        json.dump({'amount_to_trade': new_amount}, file)

def calculate_amount(capital, percentage, price):
    amount_in_usd = capital * (percentage / 100)
    amount_in_crypto = amount_in_usd / price
    return amount_in_crypto
def guardarEnRegistroPrincipal(conexion, symbol, action, amount, price):
    conn = conexion.cursor()
    try:
        conn.execute('''
            INSERT INTO transactions (symbol, action, amount, price)
            VALUES (?, ?, ?, ?)
        ''', (symbol, action, amount, price))
        conexion.commit()
        print(f"Bought {amount} of {symbol} at {price}")
    except Exception as e:
        conexion.rollback()
        print(f"Error al insertar datos: {e}")
    finally:
        conn.close()
def simulate_trading(data, initial_capital, rsi_oversold, rsi_overbought,conexion, currency_id):
    capital = initial_capital
    position = 0
    portfolio_value = [initial_capital]  # Initialize with initial capital

    for i in range(1, len(data)):
        amount_to_trade = get_amount_to_trade(conexion,currency_id)
        amount_to_trade = float(amount_to_trade)
        
        if data['RSI'].iloc[i] < rsi_oversold and capital >= data['close'].iloc[i] * amount_to_trade:
            # Buy signal
            if amount_to_trade is not None:
                position += amount_to_trade
                capital -= data['close'].iloc[i] * amount_to_trade
                print(f"Buying {amount_to_trade} units at {data['close'].iloc[i]} on {data.index[i]}")
            else:
                print("Error: amount_to_trade is None")
        elif data['RSI'].iloc[i] > rsi_overbought and position >= amount_to_trade:
            # Sell signal
            if amount_to_trade is not None:
                position -= amount_to_trade
                capital += data['close'].iloc[i] * amount_to_trade
                print(f"Selling {amount_to_trade} units at {data['close'].iloc[i]} on {data.index[i]}")
            else:
                print("Error: amount_to_trade is None")
        portfolio_value.append(capital + position * data['close'].iloc[i])
        # Update amount to trade based on some logic
        new_amount_to_trade = amount_to_trade + 1 if amount_to_trade is not None else 1  # Example logic
        
        update_amount_to_trade(new_amount_to_trade)

    data['Portfolio Value'] = portfolio_value
    return data

def main_Bitcoin(initial_capital, percentage, conexion,user_id, accion):
    symbol = 'BTCUSD'
    exchange = 'BINANCE'
    interval = Interval.in_daily
    n_bars = 100
    rsi_window = 14
    rsi_oversold = 48
    rsi_overbought = 70

    try:
        while not accion:
            data = get_crypto_data(symbol, exchange, interval, n_bars)
            data['RSI'] = calculate_rsi(data, window=rsi_window)
            
            data = simulate_trading(data, initial_capital, rsi_oversold, rsi_overbought,conexion, user_id)

            current_rsi = data['RSI'].iloc[-1]
            print(f"Current RSI: {current_rsi:.2f}")

            price = get_current_price(symbol)
            save_price_to_db(1, price, conexion)
            if current_rsi < rsi_oversold:
                print("Recommendation: It's a good time to buy.")
                amount = calculate_amount(initial_capital, percentage, price)
                print("HOLA")
                buy_crypto(1, amount, price, conexion, initial_capital, user_id)  # Ejecuta una orden de compra
            elif current_rsi > rsi_overbought:
                print("Recommendation: It's a good time to sell.")
                amount = calculate_amount(initial_capital, percentage, price)
                sell_crypto(1, amount,price,conexion, user_id)   # Ejecuta una orden de venta
            else:
                print("Recommendation: Hold.")
            time.sleep(60)


    except KeyboardInterrupt:
        print("Proceso interrumpido por el usuario.")
    except Exception as e:
        print(f"Error en main_Bitcoin: {e}")
    finally:
        if not conexion.closed:
            conexion.close()
def main_Etherium(initial_capital, porcentage, conexion, user_id, accion):
    symbol = 'ETHUSD'
    exchange = 'BINANCE'
    interval = Interval.in_daily
    n_bars = 100
    rsi_window = 14
    rsi_oversold = 30
    rsi_overbought = 70
    try:
        while not accion:

            data = get_crypto_data(symbol, exchange, interval, n_bars)
            data['RSI'] = calculate_rsi(data, window=rsi_window)

            data = simulate_trading(data, initial_capital, rsi_oversold, rsi_overbought,conexion, 3)

            current_rsi = data['RSI'].iloc[-1]
            print(f"Current RSI: {current_rsi:.2f}")

        
            price = get_current_price(symbol)
            save_price_to_db(3, price, conexion)
            if current_rsi < rsi_oversold:
                print("Recommendation: It's a good time to buy.")
                amount = calculate_amount(initial_capital, porcentage, price)
                buy_crypto(3, amount, price, conexion, initial_capital, user_id)  # Ejecuta una orden de compra
            elif current_rsi > rsi_overbought:
                print("Recommendation: It's a good time to sell.")
                amount = calculate_amount(initial_capital, porcentage, price)
                sell_crypto(3, amount,price,conexion, user_id)   # Ejecuta una orden de venta
            else:
                print("Recommendation: Hold.")
            time.sleep(60)
    except KeyboardInterrupt:
        print("Proceso interrumpido por el usuario.")
    except Exception as e:
        print(f"Error en main_Bitcoin: {e}")
    finally:
        if not conexion.closed:
            conexion.close()

def main_dogecoin(initial_capital, percentage, conexion, user_id, accion):
    symbol = 'DOGEUSD'
    exchange = 'BINANCE'
    interval = Interval.in_daily
    n_bars = 100
    rsi_window = 14
    rsi_oversold = 30
    rsi_overbought = 70

    try:
        while not accion:
            data = get_crypto_data(symbol, exchange, interval, n_bars)
            data['RSI'] = calculate_rsi(data, window=rsi_window)

            data = simulate_trading(data, initial_capital, rsi_oversold, rsi_overbought, conexion, 8)

            current_rsi = data['RSI'].iloc[-1]
            print(f"Current RSI: {current_rsi:.2f}")

            price = get_current_price(symbol)
            save_price_to_db(8, price, conexion)
            if current_rsi < rsi_oversold:
                print("Recommendation: It's a good time to buy.")
                amount = calculate_amount(initial_capital, percentage, price)
                buy_crypto(8, amount, price, conexion, initial_capital, user_id)  # Ejecuta una orden de compra
            elif current_rsi > rsi_overbought:
                print("Recommendation: It's a good time to sell.")
                amount = calculate_amount(initial_capital, percentage, price)
                sell_crypto(8, amount,price,conexion, user_id)  # Ejecuta una orden de venta
            else:
                print("Recommendation: Hold.")
            time.sleep(60)
    except KeyboardInterrupt:
        print("Proceso interrumpido por el usuario.")
    except Exception as e:
        print(f"Error en main_Bitcoin: {e}")
    finally:
        if not conexion.closed:
            conexion.close()
def main():
    pass
if __name__ == "__main__":
    main()

    