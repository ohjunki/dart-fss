from pandas import DataFrame
import pandas as pd
import FilePathManager as fm
from dart_fss.errors import NotFoundConsolidated
from decimal import *
import logging
from datetime import datetime, timedelta
logger = logging.Logger('catch_all')


######## Annual Report
def requestAnnual( corp , bgn_de='20160101' ):
    code , stockCode , name = corp._info['corp_code'], corp._info['stock_code'] ,  corp._info['corp_name']
    try:
        # return fm.loadFS(code , stockCode , name, fm.errorCompYearDir)
        fs = corp.extract_fs(bgn_de=bgn_de )
    except NotFoundConsolidated:
        fs = corp.extract_fs(bgn_de=bgn_de, separate=True )
    except Exception as e:
        logger.error(e, exc_info=True)
        raise DartError(e)

    fs_bs = fs.show('bs')
    fs_is = fs.show('cis')
    fs_is = fs.show('is') if fs_is is None or len(fs_bs.columns) != len(fs_is.columns) else fs_is
    fs_is = fs.show('cf') if fs_is is None or len(fs_bs.columns) != len(fs_is.columns) else fs_is
    if fs_is is None : 
        raise NoISFSError()
    elif len(fs_bs.columns) != len(fs_is.columns):
        raise FSColumnLengthNotMatch()

    # fm.saveFS( code , stockCode , name, fs_bs, fs_is, fm.errorCompQuarterDir, "before_refine" )
    try:
        resultBS, resultIS = remainOnlyKoreanNaming( fs_bs, fs_is )
    except Exception as e:
        fm.saveFS( code , stockCode , name, fs_bs, fs_is, fm.errorCompQuarterDir, "before_refine" )
        logger.error(e, exc_info=True)
        print("{:s} {:s} {:s} No Catched Error in requestQuarter.refine".format(code , stockCode , name ))
        raise NoCatchedError(e)

    #fm.saveFS( code , stockCode , name, resultBS, resultIS, fm.errorCompYearDir, "after_refine" )
    return resultBS, resultIS

def remainOnlyKoreanNaming( fs_bs, fs_is ):
    resultBS = fs_bs
    resultIS = fs_is
    if resultBS.columns[1][1] == 'label_en' :
        resultBS = resultBS.drop( columns=[resultBS.columns[1]])
    
    resultBS.columns = resultBS.columns.droplevel(1)

    if resultIS.columns[1][1] == 'label_en' :
        resultIS = resultIS.drop( columns=[resultIS.columns[1]])
    resultIS.columns = resultIS.columns.droplevel(1)

    tmp = list(resultIS.columns)
    tmp[0] = '카테고리'
    resultIS.columns = tmp
    tmp = list(resultBS.columns)
    tmp[0] = '카테고리'
    resultBS.columns = tmp
    return resultBS, resultIS

####### Quarter Report 받아와서 정제 작업 #######
def requestQuarter( corp, extractFSCategory, checkYearRange = 1 ):
    code , stockCode , name = corp._info['corp_code'], corp._info['stock_code'] ,  corp._info['corp_name']
    try:
        targetBeginDate = (timedelta( days=-365*checkYearRange ) + datetime.today() ).strftime( '%Y%m%d' )
        fs = corp.extract_fs(bgn_de=targetBeginDate, report_tp='quarter' )
    except NotFoundConsolidated:
        targetBeginDate = (timedelta( days=-365*checkYearRange ) + datetime.today() ).strftime( '%Y%m%d' )
        fs = corp.extract_fs(bgn_de=targetBeginDate, report_tp='quarter' , separate=True )
    except Exception as e:
        logger.error(e, exc_info=True)
        raise DartError(e)


    fs_bs : DataFrame = fs.show('bs')
    fs_is = fs.show('cis')
    fs_is = fs.show('is') if fs_is is None else fs_is
    fs_is = fs.show('cf') if fs_is is None else fs_is ## colums 길이 통일 필요
    if fs_is is None or fs_bs is None:
        raise NoISFSError()

    # fm.saveFS( code , stockCode , name, fs_bs, fs_is, fm.errorCompQuarterDir, "before_refine" )
    try:
        resultBS, resultIS = remainOnlyKoreanNaming(fs_bs, fs_is)
        resultBS, resultIS = refineQuarterFS(resultBS, resultIS, extractFSCategory)
    except Exception as e:
        fm.saveFS( code , stockCode , name, fs_bs, fs_is, fm.errorCompQuarterDir, "before_refine" )
        logger.error(e, exc_info=True)
        print("{:s} {:s} {:s} No Catched Error in requestQuarter.refine".format(code , stockCode , name ))
        raise NoCatchedError(e)

    #fm.saveFS( code , stockCode , name, resultBS, resultIS, fm.errorCompQuarterDir, "after_refine" )
    return resultBS, resultIS

def findDatFrame( df , columnString ):
    return df[:][columnString]

def refineQuarterFS( fs_bs : DataFrame , fs_is : DataFrame, extractFSISCategory, checkYearRange = 1 ):
    firstColumn = fs_bs.columns[1]
    fsISColumns = fs_is.columns
    recentYear = int(firstColumn[0:4]) # int
    quarterCode = firstColumn[4:]    # str
    
    resultBS = fs_bs.loc[ :, fs_bs.columns[0:1]]
    resultIS = fs_is.loc[ :, fs_is.columns[0:1]]
    
    dfISType = fs_is.loc[:][ fs_is.columns[0] ]
    hasMoveThenOneYear = False
    for i in range( 0, checkYearRange ):
        targetDate = '{:d}{:s}'.format( recentYear-i, quarterCode )
        startQuarter = '{:d}0101-{:d}{:s}'.format( recentYear-i, recentYear-i,   quarterCode )
        endQuarter = '{:d}0101-{:d}{:s}'.format( recentYear-1-i, recentYear-1-i, quarterCode )
        lastYear = '{:d}0101-{:d}1231'.format(  recentYear-1-i, recentYear-1-i )
        if startQuarter in fsISColumns and endQuarter in fsISColumns and lastYear in fsISColumns:
            startIS = findDatFrame( fs_is, startQuarter )
            endIS = findDatFrame( fs_is, endQuarter )
            lastYearIS = findDatFrame( fs_is, lastYear )
            for dic in extractFSISCategory.values():
                for key in dic.keys():
                    indexOfdKey = dfISType[ dfISType == key ].index
                    if indexOfdKey.size != 0 :
                        startIS[ indexOfdKey[0] ] = Decimal( startIS[ indexOfdKey[0]] ) + Decimal( lastYearIS[ indexOfdKey[0]] ) - Decimal( endIS[ indexOfdKey[0]]  )
            resultBS = pd.concat([resultBS, findDatFrame( fs_bs, targetDate )], axis=1)
            resultIS = pd.concat([resultIS, startIS], axis=1)
            hasMoveThenOneYear = True
        else:
            break

    if not hasMoveThenOneYear:
        print( "@@@@@@@@No One Year Data")
        raise NoMoreThenOneYearData()

    resultBS.columns = [ '{:s}Q'.format(c) for c in resultBS.columns ]
    resultIS.columns = resultBS.columns

    return resultBS, resultIS

def refineQuarterTest(code , stockCode , name):
    resultBS, resultIS = fm.loadFS( code , stockCode , name, fm.errorCompQuarterDir, "before_refine" )
    try:
        # resultBS, resultIS = remainOnlyKoreanNaming(fs_bs, fs_is)
        import ValueCalculer
        resultBS, resultIS = refineQuarterFS(resultBS, resultIS, ValueCalculer.Model().getISDataColumns() )
    except Exception as e:
        logger.error(e, exc_info=True)
        print("No Catched Error in requestQuarter.refine")
        raise NoCatchedError(e)

import os
for fileName in os.listdir( fm.errorCompQuarterDir ):
    if fileName.find( "fs_bs") == -1 :
        continue
    sp = fileName.split('_')
    refineQuarterTest( sp[0] , sp[1], sp[2] )

def refineYearTest(code , stockCode , name):
    fs_bs, fs_is = fm.loadFS( code , stockCode , name, fm.errorCompYearDir, "before_refine" )
    resultBS, resultIS = remainOnlyKoreanNaming(fs_bs, fs_is)

# refineQuarterTest()

    
class NoMoreThenOneYearData(Exception):
    def __init__(self, e=None):
        self.e = e
        self.message = 'No Available IS FS'

class NoISFSError(Exception):
    def __init__(self, e=None):
        self.e = e
        self.message = 'No Available IS FS'

    
class NoCatchedError(Exception):
    def __init__(self, e=None):
        self.e = e
        self.message = 'No Available IS FS'

class FSColumnLengthNotMatch(Exception):
    def __init__(self, e=None):
        self.e = e
        self.message = 'Columns of BS and IS are not equal'

class DartError(Exception):
    def __init__(self, e=None):
        self.e = e
        self.message = 'Dart Has Error'
