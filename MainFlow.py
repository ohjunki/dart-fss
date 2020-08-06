import dart_fss as dart
from dart_fss.corp.corp import Corp
import FilePathManager as fm
import pickle
from pandas import DataFrame
import pandas as pd

import DownloadFinancialStatement as downloadFS
import ExtractValueModelFromFS as extracter
import ValueCalculer
from CompanyValue import Company

import MultiThreadProcess
import os
import logging
logger = logging.Logger('catch_all')


"""
    보고서 제출일은 결산일 12월 기준 대략 0331(사업) 0515(1분기) 0815 1115 이다.
    ~0515 : 작년가치
    ~0815 : 1분기까지 가치
    ~1115 : 2분기까지 가치
    ~0331 : 3분기까지 가치

    한 회사의 재무제표를 분석하고
    회사의 정보를 저장 및 에러처리를 한다.
"""


resultDF = DataFrame()
def doMainFlow_Finalcial( corp : Corp ):
    global resultDF
    code , stockCode , name = corp._info['corp_code'], corp._info['stock_code'] ,  corp._info['corp_name']
    company = Company( code , stockCode , name )
    if company.isErrorCorp :
        print( 'Error Corp [{:s}][{:s}]{:s}'.format( code, stockCode , name ) )
        return

    valueModel = ValueCalculer.Model()
    try:
        ### Quarter Append ###
        errorPath = fm.errorCompYearDir
        fs_bs, fs_is = downloadFS.requestQuarter( corp, valueModel.getISDataColumns() )
        df = extracter.extract( fs_bs, fs_is, valueModel )
        company.appendNewDateInfo(df)

        ### Annual Append ###
        errorPath = fm.errorCompQuarterDir
        fs_bs, fs_is = downloadFS.requestAnnual( corp )
        df = extracter.extract( fs_bs, fs_is, valueModel )
        company.appendNewDateInfo(df)
    except (downloadFS.NoMoreThenOneYearData, downloadFS.NoCatchedError, downloadFS.NoISFSError, downloadFS.DartError, downloadFS.FSColumnLengthNotMatch):
        return
    except extracter.ExtractError:
        fm.saveFS( code , stockCode , name, fs_bs, fs_is, errorPath , "extractError")
    except Exception as e :
        logger.error(e, exc_info=True)
        print( 'Error Analytics [{:s}][{:s}]{:s}'.format( code, stockCode , name ) )
        return

    valueModel.calculateCompanyValue(company.df, company)
    if valueModel.isValuableCompany():
        company.saveResult()
        dic = { **(company.to_Dict_info()) , **(valueModel.to_Dict_info()) }
        resultDF = resultDF.append( DataFrame( [dic.values()] , columns=dic.keys() ) )
        resultDF.to_excel("{:s}/goodCorp.xlsx".format( fm.resultDirectory ))
        resultDF.to_pickle("{:s}/goodCorp.pkl".format( fm.resultDirectory ))
    print( 'Finish Analytics [{:s}][{:s}]{:s}'.format( code, stockCode, name ) )

dontknowReasonErrorCompany = []
def saveDontKnowReasonErrorCompany( stockCode ):
    global dontknowReasonErrorCompany
    dontknowReasonErrorCompany.append( stockCode )
    f = open( "{:s}/dontknowReasonErrorCompany.pkl".format( fm.resultDirectory ) , "wb" )
    pickle.dump( dontknowReasonErrorCompany, f )
    f.close()

def startDartAnalytics(oneMoreCompany = [], lastCode = None ):
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
        if corp._info['stock_code'] == None :
            continue

        if not findLastCode and corp._info['stock_code'] != lastCode:
            if corp._info['stock_code'] not in oneMoreCompany:
                continue
        else:
            findLastCode = True
    
        print( 'Start Analytics [{:s}]{:s}'.format( corp._info['stock_code'] , corp._info['corp_name']) )
        doMainFlow_Finalcial( corp )

def startOneCompany( stockCode ):
    api_key='ba617a15720b47d38c7dee91382257e7cfb2c7df' 
    dart.set_api_key(api_key=api_key)
    corp_list = dart.get_corp_list(True)    
    corp = corp_list.find_by_stock_code(stockCode)
    doMainFlow_Finalcial( corp )


def testValueModel( code , stockCode , name ):
    valueModel = ValueCalculer.Model()
    company = Company( code , stockCode , name )

    fs_bs, fs_is = fm.loadFS(code , stockCode , name, fm.errorCompQuarterDir, "after_refine")
    df = extracter.extract( fs_bs, fs_is, valueModel )
    company.appendNewDateInfo(df)

    fs_bs, fs_is = fm.loadFS(code , stockCode , name, fm.errorCompYearDir, "after_refine")
    df = extracter.extract( fs_bs, fs_is, valueModel )
    company.appendNewDateInfo(df)
    
    valueModel.calculateCompanyValue(company.df, company)


def startMultiThreading(oneMoreCompany = [], lastCode = [None,None,None] ):
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

    def func_work( threadIndex, targetIndex ):
        findLastCode = True if lastCode[threadIndex] is None else False
        corp = corp_list.corps[targetIndex]
        if corp._info['stock_code'] == None :
            return
        if not findLastCode and corp._info['stock_code'] != lastCode:
            if corp._info['stock_code'] not in oneMoreCompany:
                return
        else:
            findLastCode = True
    
        logger.warning( 'Start Analytics [Thread-{:d}][{:s}][{:s}]{:s}'.format( threadIndex, corp._info['corp_code'], corp._info['stock_code'] , corp._info['corp_name']) )
        doMainFlow_Finalcial( corp )

    MultiThreadProcess.doMultiThread_For_Index_State( func_work, 3, len(corp_list.corps) )

# testValueModel( '00293886', '044340', '위닉스' )

# api_key='ba617a15720b47d38c7dee91382257e7cfb2c7df' 
# dart.set_api_key(api_key=api_key)

# corp_list = dart.get_corp_list(True)
# corp = corp_list.find_by_corp_name('삼성전자')[0]
# fs_bs, fs_is = DefaultAnalyister.extractFinancialStatement( corp )
# fs_bs.to_pickle( 'fs_bs.plk')
# fs_is.to_pickle( 'fs_is.plk')
# doMainFloow_Finalcial( fs_bs, fs_is , corp._info['corp_code'],  corp._info['stock_code'] ,  corp._info['corp_name'] )

startMultiThreading()