import pandas as pd
import warnings


def get_kospi_kosdaq_stockcode():
    warnings.filterwarnings("ignore", category=UserWarning)
    url = "https://kind.krx.co.kr/corpgeneral/corpList.do"

    kosdaq = pd.read_html(
        url + "?method=download&marketType=kosdaqMkt", encoding="cp949"
    )[0]
    kospi = pd.read_html(
        url + "?method=download&marketType=stockMkt", encoding="cp949"
    )[0]

    kosdaq["종목코드"] = kosdaq["종목코드"].astype(str).apply(lambda x: x.zfill(6))
    kospi["종목코드"] = kospi["종목코드"].astype(str).apply(lambda x: x.zfill(6))

    stockcode_dict = {"kospi": set(kospi["종목코드"]), "kosdaq": set(kosdaq["종목코드"])}
    return stockcode_dict


# stockcode_dict = get_kospi_kosdaq_stockcode()
