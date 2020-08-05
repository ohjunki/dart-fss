from pandas import DataFrame
from CompanyValue import CompanyValueAlgo1, ValueDataFrameModel
from decimal import *
import math
from datetime import datetime
from datetime import timedelta
import pandas as pd

def extractFinancialStatement( corp ):
    try:
        targetBeginDate = (timedelta( days=-365*2 ) + datetime.today() ).strftime( '%Y%m%d' )
        fs = corp.extract_fs(bgn_de=targetBeginDate, report_tp='quarter' )
    except Exception:
        return None

    fs_bs = fs.show('bs')
    fs_is = fs.show('cis')
    fs_is = fs.show('is') if fs_is is None else fs_is
    fs_is = fs.show('cf') if fs_is is None else fs_is ## colums 길이 통일 필요
    if fs_is is None or fs_bs is None:
        return None

    fs_bs, fs_is = refineFS(fs_bs, fs_is)
    return fs_bs, fs_is

"""
    Column을 동일화하고
    불필요한 Column들을 삭제한다.
"""
def refineFS( fs_bs : DataFrame , fs_is : DataFrame):
    firstColumn = fs_bs.columns[2][0]
    fsISColumns = [ c[0] for c in fs_is.columns ][2:]
    recentYear = int(firstColumn[0:4]) # int
    quarterCode = firstColumn[4:]    # str
    
    yearCount = 0
    resultBS = fs_bs.loc[ :, fs_bs.columns[0:2]]
    resultIS = fs_is.loc[ :, fs_is.columns[0:2]]
    
    dfISType = fs_is.loc[:][ fs_is.columns[0] ]
    
    for i in range( 0, 4 ):
        targetDate = '{:d}{:s}'.format( recentYear-i, quarterCode )
        startQuarter = '{:d}0101-{:d}{:s}'.format( recentYear-i, recentYear-i,   quarterCode )
        endQuarter = '{:d}0101-{:d}{:s}'.format( recentYear-1-i, recentYear-1-i, quarterCode )
        lastYear = '{:d}0101-{:d}1231'.format(  recentYear-1-i, recentYear-1-i )
        if startQuarter in fsISColumns and endQuarter in fsISColumns and lastYear in fsISColumns:
            yearCount += 1
            startIS = findDatFrame( fs_is, startQuarter )
            endIS = findDatFrame( fs_is, endQuarter )
            lastYearIS = findDatFrame( fs_is, lastYear )
            for dic in ValueDataFrameModel().getISDataColumns().values():
                for key in dic.keys():
                    indexOfdKey = dfISType[ dfISType == key ].index
                    if indexOfdKey.size != 0 :
                        startIS[ indexOfdKey[0] ] = Decimal( startIS[ indexOfdKey[0]] ) + Decimal( endIS[ indexOfdKey[0]] ) + Decimal( lastYearIS[ indexOfdKey[0]] )
            resultBS = pd.concat([resultBS, findDatFrame( fs_bs, targetDate )], axis=1)
            resultIS = pd.concat([resultIS, startIS], axis=1)
        else:
            break

    resultIS.columns = resultBS.columns
    return resultBS, resultIS

def findDatFrame( df , columnString ):
    for column in df.columns:
        if columnString in column[0]:
            return df[:][column]
    return None

def calculCompanyValue( corp_code, stock_code , name, fs_bs : DataFrame , fs_is : DataFrame ):
    cv = CompanyValueAlgo1( corp_code, stock_code , name )
    if cv.isErrorCorp :
        return None

    values_bs = fs_bs.drop( columns=[ fs_bs.columns[0],fs_bs.columns[1] ])
    values_bs.columns = values_bs.columns.droplevel(1)
    kr_bstype = fs_bs.loc[ : , [ fs_bs.columns[0] ]]

    values_is : DataFrame = fs_is.drop( columns=[ fs_is.columns[0],fs_is.columns[1] ])
    values_is.columns = values_bs.columns
    kr_istype = fs_is.loc[ : , [ fs_is.columns[0] ]]


    df = DataFrame( [], columns=values_bs.columns, index=cv.getDFindex() )

    for column in values_bs.columns:
        curbs = values_bs.loc[ : , [column] ]
        dic = cv.getBSDataColumns()
        for key in dic.keys():
            sum = Decimal(0.0)
            for dKey in dic[key].keys():
                indexOfdKey = kr_bstype[ kr_bstype[kr_bstype.columns[0]] == dKey].index
                if indexOfdKey.size != 0 :
                    try:
                        if type(curbs.loc[ indexOfdKey[0]][0]) != None and not math.isnan( curbs.loc[ indexOfdKey[0]][0]):
                            sum += Decimal(curbs.loc[ indexOfdKey[0]][0])
                    except Exception:
                        pass
            # print(key+" = "+str(sum))
            df.loc[ key, [column] ] = sum

    for column in values_is.columns:
        curbs = values_is.loc[ : , [column] ]
        dic = cv.getISDataColumns()
        for key in dic.keys():
            sum = Decimal(0.0)
            for dKey in dic[key].keys():
                indexOfdKey = kr_istype[ kr_istype[kr_istype.columns[0]] == dKey].index
                if indexOfdKey.size != 0 :
                    try:
                        if type(curbs.loc[ indexOfdKey[0]][0]) != None and not math.isnan( curbs.loc[ indexOfdKey[0]][0]):
                            sum += Decimal(curbs.loc[ indexOfdKey[0]][0])
                    except Exception:
                        pass
            # print(key+" = "+str(sum))
            df.loc[ key, [column] ] = sum
                        
    cv.appendNewDateInfo( df )
    return cv
    