import time
import datetime
import pandas as pd
from dhanhq import dhanhq

# Add your client_id and access_token here
client_id = "f u"
access_token = "f u"
dhan = dhanhq(client_id, access_token)

def is_market_open():
    current_time = datetime.datetime.now().time()
    start_time = datetime.time(9, 30)
    end_time = datetime.time(15, 30)
    return start_time <= current_time <= end_time

def get_intraday_data():
    try:
        data = dhan.intraday_minute_data(
            security_id='1660',
            exchange_segment='NSE_EQ',
            instrument_type='EQUITY'
        )
        df = pd.DataFrame(data['data'])
        df['timestamp'] = df['date']
        df['date'] = pd.to_datetime(df['timestamp'], unit='s')
        df.set_index('date', inplace=True)
        last_hour_data = df.loc[df.index > df.index.max() - pd.Timedelta(hours=1)]
        return last_hour_data
    except Exception as e:
        print(f"Error occurred while fetching intraday data: {e}")
        return pd.DataFrame()

def place_buy_order(current_price):
    stop_loss_price = current_price - 10
    take_profit_price = current_price + 10
    try:
        dhan.place_order(
            security_id='1660',
            exchange_segment=dhan.NSE,
            transaction_type=dhan.BUY,
            quantity=1,
            order_type=dhan.MARKET,
            product_type=dhan.INTRA,
            price=0,
            bo_profit_value=take_profit_price,
            bo_stop_loss_value=stop_loss_price
        )
        print(f"Buy order placed at Price: {current_price}, Stop Loss: {stop_loss_price}, Take Profit: {take_profit_price}")
    except Exception as e:
        print(f"Error occurred while placing buy order: {e}")

def place_sell_order(current_price):
    stop_loss_price = current_price + 10
    take_profit_price = current_price - 10
    try:
        dhan.place_order(
            security_id='1660',
            exchange_segment=dhan.NSE,
            transaction_type=dhan.SELL,
            quantity=1,
            order_type=dhan.MARKET,
            product_type=dhan.INTRA,
            price=0,
            bo_profit_value=take_profit_price,
            bo_stop_loss_value=stop_loss_price
        )
        print(f"Sell order placed at Price: {current_price}, Stop Loss: {stop_loss_price}, Take Profit: {take_profit_price}")
    except Exception as e:
        print(f"Error occurred while placing sell order: {e}")

def implement_strategy(df):
    try:
        df['30EMA'] = df['close'].ewm(span=30, adjust=False).mean()
        df['3EMA'] = df['close'].ewm(span=3, adjust=False).mean()

        for i in range(2, len(df)):
            if df['30EMA'].iloc[i] > df['3EMA'].iloc[i] and df['30EMA'].iloc[i-1] < df['3EMA'].iloc[i-1]:
                prev_candles = df['close'].iloc[i-3:i]
                if prev_candles.iloc[-1] < prev_candles.iloc[-2] < prev_candles.iloc[-3]:
                    current_price = df.iloc[i]['close']
                    place_buy_order(current_price)
                else:
                    current_price = df.iloc[i]['close']
                    place_sell_order(current_price)
            else:
                print("Strategy running, no signal found")
    except Exception as e:
        print(f"Error occurred while implementing the strategy: {e}")

def main():
    while True:
        if is_market_open():
            print("Market is open")
            intraday_data = get_intraday_data()
            if not intraday_data.empty:
                implement_strategy(intraday_data)
            time.sleep(10)  # Wait for 5 minutes
        else:
            print("Market is closed")
            break

if __name__ == '__main__':
    main()
