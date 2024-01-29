from settings import env_settings


def calculate_qty(now_stock_price):
    # 한정된 금액안에서 안전하게 매수 수량을 계산할 수 있도록, 10% 상승한 가격 기준 수량 계산
    ten_percent_price = now_stock_price * 1.1
    stock_buy_max_balance = env_settings.TOTAL_BALANCE / env_settings.MAX_STOCKS
    available_qty = int(stock_buy_max_balance / ten_percent_price)

    if env_settings.ADD_BUY_FLAG == "1":  # 추가 매수면 절반씩 매수해야함.
        available_qty = int(available_qty / 2)

    return available_qty


def calculate_profit_price(price, percent):
    return price * (1 + (percent / 100))


def calculate_loss_price(price, percent):
    return price * (1 - (percent / 100))
