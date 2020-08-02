import dart_fss as dart
from dart_fss.corp.corp import Corp
import pickle
from pandas import DataFrame
import pandas as pd
import stockprice
from CompanyValue import CompanyValueAlgo1
import fsExtractManager

# Open DART API KEY 설정
api_key='ba617a15720b47d38c7dee91382257e7cfb2c7df'
dart.set_api_key(api_key=api_key)

corp_list = dart.get_corp_list(False)

dart.api.info.get_capital_increase()
# 삼성전자 검색
samsung : Corp = corp_list.find_by_corp_name('삼성전자', exactly=True)[0]

# 2012년부터 연간 연결재무제표 불러오기
fs = samsung.extract_fs(bgn_de='20150101')
fs_bs : DataFrame = fs.show('bs')
fs_is : DataFrame  = fs.show('is')

# fs_bs = pd.read_pickle( "fs_bs.pkl")
# fs_is = pd.read_pickle( "fs_is.pkl")

cv = CompanyValueAlgo1( '00126380', '005930' , '삼성전자' ) #samsung._info['corp_code'],  samsung._info['corp_name'] )
cv = fsExtractManager.calculCompanyValue( cv, fs_bs, fs_is )

print( cv.getExpectReturnRatio() )