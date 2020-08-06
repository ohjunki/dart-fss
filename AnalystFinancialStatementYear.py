from pandas import DataFrame
import FilePathManager as fm
from CompanyValue import ValueDataFrameModel
from decimal import *
import math

valueModel = ValueDataFrameModel()
def extractFinancialStatement( corp ):
    code , stockCode , name = corp._info['corp_code'], corp._info['stock_code'] ,  corp._info['corp_name']
    try:
        # return fm.loadFS(code , stockCode , name, fm.errorCompYearDir)
        fs = corp.extract_fs(bgn_de='20160101')
    except Exception:
        return None, None
    fs_bs = fs.show('bs')
    fs_is = fs.show('cis')
    fs_is = fs.show('is') if fs_is is None or len(fs_bs.columns) != len(fs_is.columns) else fs_is
    fs_is = fs.show('cf') if fs_is is None or len(fs_bs.columns) != len(fs_is.columns) else fs_is
    if fs_is is None or len(fs_bs.columns) != len(fs_is.columns):
        print('No FS_IS [{:s}]{:s}'.format( corp._info['stock_code'] , corp._info['corp_name']) )
        return None, None
    fm.saveFS( code , stockCode , name, fs_bs, fs_is, fm.errorCompYearDir )
    return fs_bs, fs_is

def calculCompanyValue(code , stockCode, name,  fs_bs : DataFrame , fs_is : DataFrame ):
    try:
        values_bs = fs_bs.drop( columns=[ fs_bs.columns[0],fs_bs.columns[1] ])
        values_bs.columns = values_bs.columns.droplevel(1)
        kr_bstype = fs_bs.loc[ : , [ fs_bs.columns[0] ]]

        values_is : DataFrame = fs_is.drop( columns=[ fs_is.columns[0],fs_is.columns[1] ])
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
    except:
        fm.saveFS(code , stockCode, name, fs_bs, fs_is, fm.errorCompQuarterDir )
        return None

    return df
    