import pandas as pd
import pandas_datareader as pdr
from datetime import datetime, timedelta
from urllib import request
from bs4 import BeautifulSoup
from decimal import *

# 종목 타입에 따라 download url이 다름. 종목코드 뒤에 .KS .KQ등이 입력되어야해서 Download Link 구분 필요
stock_type = {
    'kospi': 'stockMkt',
    'kosdaq': 'kosdaqMkt'
}


# download url 조합
def get_download_stock(market_type=None):
  market_type_param = stock_type[market_type]
  download_link = 'http://kind.krx.co.kr/corpgeneral/corpList.do'
  download_link = download_link + '?method=download'
  download_link = download_link + '&marketType=' + market_type_param

  df = pd.read_html(download_link, header=0)[0]
  return df;

# kospi 종목코드 목록 다운로드
def get_download_kospi():
  df = get_download_stock('kospi')
  df.종목코드 = df.종목코드.map('{:06d}.KS'.format)
  return df

# kosdaq 종목코드 목록 다운로드
def get_download_kosdaq():
  df = get_download_stock('kosdaq')
  df.종목코드 = df.종목코드.map('{:06d}.KQ'.format)
  return df


# kospi, kosdaq 종목코드 각각 다운로드
kospi_df = get_download_kospi()
kosdaq_df = get_download_kosdaq()

# data frame merge
code_df = pd.concat([kospi_df, kosdaq_df])

# data frame정리
code_df = code_df[['회사명', '종목코드']]

# data frame title 변경 '회사명' = name, 종목코드 = 'code'
code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'})

# 회사명으로 주식 종목 코드를 획득할 수 있도록 하는 함수
def get_code( name):
    code = code_df.query("name=='{}'".format(name))['code'].to_string(index=False)
    # 위와같이 code명을 가져오면 앞에 공백이 붙어있는 상황이 발생하여 앞뒤로 sript() 하여 공백 제거
    code = code.strip()
    return code

def get_close_stock_price_with_name( company_name ):
    code = get_code( company_name )
    df = pdr.get_data_yahoo(code)
    return df['Open'].iloc[-1]

def get_close_stock_price_with_code( company_code ):
    df = pdr.get_data_yahoo(company_code)
    return df['Open'].iloc[-1]


"""
  한국거래소에서 제공하는 XML를 활용해서 데이터를 수집하는 방법
  https://tariat.tistory.com/892
"""
def get_sise(stock_code, try_cnt):
    try:
        url="http://asp1.krx.co.kr/servlet/krx.asp.XMLSiseEng?code={}".format(stock_code)
        req=request.urlopen(url)
        result=req.read()
        xmlsoup=BeautifulSoup(result,"lxml-xml")
        stock = xmlsoup.find("TBL_StockInfo")
        stock_df=pd.DataFrame(stock.attrs, index=[0])
        stock_df=stock_df.applymap(lambda x: x.replace(",",""))
        return stock_df

    except request.HTTPError as e:
        if try_cnt>=3:
            return None
        else:
            get_sise(stock_code,try_cnt=+1)

def get_total_stock_count( stock_code ):
    temp=get_sise( stock_code,1)
    return Decimal(temp.loc[0]['Amount'])

def get_recent_open_total_stock_price( stock_code ):
    temp=get_sise(stock_code,1)
    return Decimal(temp.loc[0]['Amount']) * Decimal(temp.loc[0]['StartJuka'])
