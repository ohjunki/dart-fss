from pandas import DataFrame
from CompanyValue import CompanyValueAlgo1
from decimal import *
import math

def calculCompanyValue( cv : CompanyValueAlgo1 , fs_bs : DataFrame , fs_is : DataFrame ):
    values_bs = fs_bs.drop( columns=[ fs_bs.columns[0],fs_bs.columns[1] ])
    values_bs.columns = values_bs.columns.droplevel(1)
    kr_bstype = fs_bs.loc[ : , [ fs_bs.columns[0] ]]

    values_is : DataFrame = fs_is.drop( columns=[ fs_is.columns[0],fs_is.columns[1] ])
    values_is.columns = values_bs.columns
    kr_istype = fs_is.loc[ : , [ fs_is.columns[0] ]]


    #df = DataFrame( [], columns=values_bs.columns, index=cv.getDFindex().keys() )
    df = DataFrame( [], columns=values_bs.columns, index=[ '유동자산', '투자자산', '유동부채', '비유동부채', '당기순이익(손실)', '회사가치' ] )

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
            print(key+" = "+str(sum))
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
            print(key+" = "+str(sum))
            df.loc[ key, [column] ] = sum
                        
    cv.appendNewDateInfo( df )
    cv.calculateCompanyValue()
    return cv