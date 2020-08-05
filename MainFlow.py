import dart_fss as dart
from dart_fss.corp.corp import Corp
import FilePathManager as fm
import pickle
from pandas import DataFrame
import pandas as pd
import AnalystFinancialStatementYear as DefaultAnalyister
import AnalystFinancialStatementQuarter as extracter

import os

"""
    한 회사의 재무제표를 분석하고
    회사의 정보를 저장 및 에러처리를 한다.
"""

def doMainFloow_Finalcial( fs_bs, fs_is, corp_code, stock_code , name, extracter = DefaultAnalyister ):
    resultDF = DataFrame()
    try:
        cv = extracter.calculCompanyValue( corp_code, stock_code , name, fs_bs, fs_is )
        if cv is None:
            print( 'Error Corp [{:s}]{:s}'.format( stock_code , name ) )
            return

        cv.calculateCompanyValue()
        if cv.isValuableCompany():
            cv.saveResult()
            dic = cv.to_Dict_info()
            resultDF = resultDF.append( DataFrame( [dic.values()] , columns=dic.keys() ) )
            resultDF.to_excel("{:s}/goodCorp.xlsx".format( fm.resultDirectory ))
            resultDF.to_pickle("{:s}/goodCorp.pkl".format( fm.resultDirectory ))
        print( 'Finish Analytics [{:s}]{:s}'.format( stock_code, name ) )
    except Exception:
        print( 'Error Analytics And Save [{:s}]{:s}'.format( stock_code , name ) )
        fs_bs.to_pickle( '{:s}/{:s}_{:s}_{:s}_fs_bs.pkl'.format( fm.errorCompDir, corp_code, stock_code , name ) )
        fs_is.to_pickle( '{:s}/{:s}_{:s}_{:s}_fs_is.pkl'.format( fm.errorCompDir, corp_code, stock_code , name ) )

dontknowReasonErrorCompany = []
def saveDontKnowReasonErrorCompany( stock_code ):
    global dontknowReasonErrorCompany
    dontknowReasonErrorCompany.append( stock_code )
    f = open( "{:s}/dontknowReasonErrorCompany.pkl".format( fm.resultDirectory ) , "wb" )
    pickle.dump( dontknowReasonErrorCompany, f )
    f.close()


def startDartAnalytics(oneMoreCompany, lastCode = None, extracter = DefaultAnalyister ):
    """
        Open DART API KEY 설정
        하루 최대 10,000건
        분당 100회 이상 요청시 서비스가 제한될 수 있음
        총 상장 회사 3214
        ba617a15720b47d38c7dee91382257e7cfb2c7df , e81485828c18bdd581d05833ea37180f6bb04492
    """
    api_key='ba617a15720b47d38c7dee91382257e7cfb2c7df' 
    dart.set_api_key(api_key=api_key)

    corp_list = dart.get_corp_list(True)    
    findLastCode = True if lastCode is None else False
    for corp in corp_list.corps:
        if corp._info['stock_code'] != None :
            if not findLastCode and corp._info['stock_code'] != lastCode:
                if corp._info['stock_code'] not in oneMoreCompany:
                    continue
            else:
                findLastCode = True
            print( 'Start Analytics [{:s}]{:s}'.format( corp._info['stock_code'] , corp._info['corp_name']) )
            try:
                fs_bs, fs_is = extracter.extractFinancialStatement( corp )
                if fs_bs is None or fs_is is None:
                    continue
                doMainFloow_Finalcial( fs_bs, fs_is , corp._info['corp_code'],  corp._info['stock_code'] ,  corp._info['corp_name'] )
            except Exception:
                saveDontKnowReasonErrorCompany( corp._info['stock_code'] )
                print( 'Error Analytics [{:s}]{:s}'.format( corp._info['stock_code'] , corp._info['corp_name']) )


api_key='ba617a15720b47d38c7dee91382257e7cfb2c7df' 
dart.set_api_key(api_key=api_key)

corp_list = dart.get_corp_list(True)
corp = corp_list.find_by_corp_name('삼성전자')[0]
fs_bs, fs_is = extracter.extractFinancialStatement( corp )
fs_bs.to_pickle( 'fs_bs.plk')
fs_is.to_pickle( 'fs_is.plk')
doMainFloow_Finalcial( fs_bs, fs_is , corp._info['corp_code'],  corp._info['stock_code'] ,  corp._info['corp_name'] )