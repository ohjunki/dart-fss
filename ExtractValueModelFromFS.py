
from pandas import DataFrame
from decimal import *
import math
import logging
logger = logging.Logger('catch_all')


def extract( fs_bs : DataFrame , fs_is : DataFrame , valueModel ):
    try:
        values_bs = fs_bs.drop( columns=[ fs_bs.columns[0] ])
        kr_bstype = fs_bs.loc[ : , [ fs_bs.columns[0] ]]

        values_is : DataFrame = fs_is.drop( columns=[ fs_is.columns[0] ])
        values_is.columns = values_bs.columns
        kr_istype = fs_is.loc[ : , [ fs_is.columns[0] ]]

        df = DataFrame( [], columns=values_bs.columns, index=valueModel.getDFindex() )

        for column in values_bs.columns:
            curbs = values_bs.loc[ : , [column] ]
            dic = valueModel.getBSDataColumns()
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
            dic = valueModel.getISDataColumns()
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
    except Exception as e:
        logger.error(e, exc_info=True)
        raise ExtractError(e)

    return df
    
def extracterTest(code , stockCode , name):
    fs_bs, fs_is = fm.loadFS( code , stockCode , name, fm.errorCompQuarterDir, "extractError " )
    import ValueCalculer
    resultBS, resultIS = extract(fs_bs, fs_is, ValueCalculer.Model() )
    
class ExtractError(Exception):
    def __init__(self, e=None):
        self.e = e
        self.message = 'Extract Error'

