from pandas import DataFrame
from CompanyValue import CompanyValueAlgo1
from decimal import *
import math

def extractFinancialStatement( corp ):
    try:
        fs = corp.extract_fs(bgn_de='20160101')
    except Exception:
        return None
    fs_bs = fs.show('bs')
    fs_is = fs.show('cis')
    fs_is = fs.show('is') if fs_is is None or len(fs_bs.columns) != len(fs_is.columns) else fs_is
    fs_is = fs.show('cf') if fs_is is None or len(fs_bs.columns) != len(fs_is.columns) else fs_is
    if fs_is is None or len(fs_bs.columns) != len(fs_is.columns):
        print('No FS_IS [{:s}]{:s}'.format( corp._info['stock_code'] , corp._info['corp_name']) )
        return None
    return fs_bs, fs_is

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
    