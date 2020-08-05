import dart_fss as dart
from dart_fss.corp.corp import Corp
import FilePathManager as fm
import pickle
from pandas import DataFrame
import pandas as pd
import stockprice
from CompanyValue import CompanyValueAlgo1
import fsExtractManager
import os
import random

"""
    Open DART API KEY 설정
    하루 최대 10,000건
    총 상장 회사 3214
    ba617a15720b47d38c7dee91382257e7cfb2c7df , e81485828c18bdd581d05833ea37180f6bb04492
"""
api_key='ba617a15720b47d38c7dee91382257e7cfb2c7df' 
dart.set_api_key(api_key=api_key)

corp_list = dart.get_corp_list(True)

publicList = []
for corp in corp_list.corps:
    if corp._info['stock_code'] != None:
        publicList.append( corp )
        
def check_fs( extractedCorp, exceptCorp , publicList , index):
    corp = publicList[index]
    if corp in extractedCorp or corp in exceptCorp:
        return False
    try:
        fs = corp.extract_fs(bgn_de='20160101', report_tp='quarter' )
    except Exception:
        exceptCorp.append(corp)
        return False

    fs_bs = fs.show('bs')
    fs_is = fs.show('cis')
    fs_is = fs.show('is') if fs_is is None else fs_is
    fs_is = fs.show('cf') if fs_is is None else fs_is
    if fs_is is None :
        exceptCorp.append(corp)
        return False

    fs_bs.to_excel( 'testQuarterData/fs_bs_[{:s}]{:s}.xlsx'.format( corp._info['stock_code'] , corp._info['corp_name'] ))
    fs_is.to_excel( 'testQuarterData/fs_is_[{:s}]{:s}.xlsx'.format( corp._info['stock_code'] , corp._info['corp_name'] ))
    extractedCorp.append( corp )
    return True
    
extractCount = 10
extractedCorp = []
exceptCorp = []
def extract_quarter( targetIndex ):
    global extractCount
    global extractedCorp
    global exceptCorp
    global publicList
    index = random.randint( 0, len(publicList)-1 )
    print( 'Start Work Thread[{:d}'.format(targetIndex ))
    if check_fs( extractedCorp, exceptCorp , publicList , index) :
        extractCount -= 1

import MultiThreadProcess

def is_inWhile( targetIndex ):
    return extractCount > 0

MultiThreadProcess.doMultiThread_While_State( extract_quarter, is_inWhile, 3 )