import dart_fss as dart
from dart_fss.corp.corp import Corp
import FilePathManager as fm
import pickle
from pandas import DataFrame
import pandas as pd
import stockprice
from CompanyValue import CompanyValueAlgo1
import fsExtractManager
from pandas_datareader._utils import RemoteDataError
import os

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
resultDF = DataFrame()

def one_company( fs, fs_bs, fs_is, corp_code, stock_code , name ):
    try:
        global resultDF
        cv = CompanyValueAlgo1( corp_code, stock_code , name )
        if cv.isErrorCorp:
            print( 'Error Corp [{:s}]{:s}'.format( stock_code , name ) )
            return
        cv = fsExtractManager.calculCompanyValue( cv, fs_bs, fs_is )
        if cv.getExpectReturnRatio() > 10 :
            print( '[{:d}]{:s}'.format(int(cv.getExpectReturnRatio()) , cv.name ) )
            cv.saveResult()
            dic = cv.to_Dict_info()
            resultDF = resultDF.append( DataFrame( [dic.values()] , columns=dic.keys() ) )
            resultDF.to_excel("{:s}/goodCorp.xlsx".format( fm.resultDirectory ))
            resultDF.to_pickle("{:s}/goodCorp.pkl".format( fm.resultDirectory ))
        print( 'Finish Analytics [{:s}]{:s}'.format( stock_code, name ) )
    except Exception:
        print( 'Error Analytics And Save [{:s}]{:s}'.format( stock_code , name ) )
        if fs is not None:
            fs.save()
        fs_bs.to_pickle( '{:s}/{:s}_{:s}_{:s}_fs_bs.pkl'.format( fm.errorCompDir, corp_code, stock_code , name ) )
        fs_is.to_pickle( '{:s}/{:s}_{:s}_{:s}_fs_is.pkl'.format( fm.errorCompDir, corp_code, stock_code , name ) )

dontknowReasonErrorCompany = []
def saveDontKnowReasonErrorCompany( stock_code ):
    global dontknowReasonErrorCompany
    dontknowReasonErrorCompany.append( stock_code )
    f = open( "{:s}/dontknowReasonErrorCompany.pkl".format( fm.resultDirectory ) , "wb" )
    pickle.dump( dontknowReasonErrorCompany, f )
    f.close()


def main():
    #TODO oneMore 필요 유무 체크하기
    f = open( "{:s}/oneMoreCompany.pkl".format( fm.sharedDirectory ) , "rb" )
    oneMoreCompany = pickle.load( f )
    f.close()

    global resultDF
    lastCode = '073110' # 192820이거부터 다시하기
    findLastCode = False
    for corp in corp_list.corps:
        if corp._info['stock_code'] != None :
            if not findLastCode and corp._info['stock_code'] != lastCode:
                if corp._info['stock_code'] not in oneMoreCompany:
                    continue
            else:
                findLastCode = True
            print( 'Start Analytics [{:s}]{:s}'.format( corp._info['stock_code'] , corp._info['corp_name']) )
            try:
                try:
                    fs = corp.extract_fs(bgn_de='20160101')
                except Exception:
                    continue
                fs_bs = fs.show('bs')
                fs_is = fs.show('cis')
                fs_is = fs.show('is') if fs_is is None or len(fs_bs.columns) != len(fs_is.columns) else fs_is
                fs_is = fs.show('cf') if fs_is is None or len(fs_bs.columns) != len(fs_is.columns) else fs_is
                if fs_is is None or len(fs_bs.columns) != len(fs_is.columns):
                    print('No FS_IS [{:s}]{:s}'.format( corp._info['stock_code'] , corp._info['corp_name']) )
                    continue
                one_company( fs, fs_bs, fs_is , corp._info['corp_code'],  corp._info['stock_code'] ,  corp._info['corp_name'] )
            except dart.errors.NoDataReceived:
                print( 'No Analytics [{:s}]{:s}'.format( corp._info['stock_code'] , corp._info['corp_name']) )
            except dart.errors.NotFoundConsolidated:
                print( 'No Analytics [{:s}]{:s}'.format( corp._info['stock_code'] , corp._info['corp_name']) )
            except Exception:
                saveDontKnowReasonErrorCompany( corp._info['stock_code'] )
                print( 'Error Analytics [{:s}]{:s}'.format( corp._info['stock_code'] , corp._info['corp_name']) )
                pass
            

# main()

def checkErrorCorp():
    oneMoreCompany = []
    count = 0
    for fileName in os.listdir( fm.errorCompDir ):
        if fileName.find( "fs_bs") == -1 :
            continue
        # print( fileName )
        sp = fileName.split("_")
        corp_code = sp[0]
        stock_code = sp[1]
        name = sp[2].replace("_fs_is.pkl","")
        fs_bs = pd.read_pickle( '{:s}/{:s}'.format(fm.errorCompDir,fileName) )
        try :
            fs_is = pd.read_pickle( '{:s}/{:s}_{:s}_{:s}_fs_is.pkl'.format( fm.errorCompDir, corp_code, stock_code , name ))
        except Exception:
            continue

        if len(fs_bs.columns) != len(fs_is.columns):
            oneMoreCompany.append(stock_code)
            count += 1
            continue
        one_company( None, fs_bs, fs_is, corp_code, stock_code, name )

    # resultDF.to_excel( "{:s}/goodCorp.xlsx".format(fm.resultDirectory) )
    # resultDF.to_pickle( "{:s}/goodCorp.pkl".format(fm.resultDirectory) )
    # f = open( "{s:}/oneMoreCompany.pkl".format(fm.resultDirectory) , "wb" )
    # pickle.dump( oneMoreCompany, f )
    # f.close()
    # f = open( "{s:}/oneMoreCompany.pkl".format(fm.sharedDirectory) , "wb" )
    # pickle.dump( oneMoreCompany, f )
    # f.close()
    

# checkErrorCorp()


def main2ErrorCheck():
    #TODO oneMore 필요 유무 체크하기
    f = open( "{:s}/dontknowReasonErrorCompany.pkl".format( fm.resultDirectory ) , "rb" )
    oneMoreCompany = pickle.load( f )
    f.close()

    exceptList = []

    global resultDF
    for corp in corp_list.corps:
        if corp._info['stock_code'] != None :
            if corp._info['stock_code'] not in oneMoreCompany:
                continue

            if corp._info['stock_code'] in exceptList:
                continue

            print( 'Start Analytics [{:s}]{:s}'.format( corp._info['stock_code'] , corp._info['corp_name']) )
            try:
                try:
                    fs = corp.extract_fs(bgn_de='20160101')
                except Exception:
                    continue

                fs_bs = fs.show('bs')
                fs_is = fs.show('cis')
                fs_is = fs.show('is') if fs_is is None or len(fs_bs.columns) != len(fs_is.columns) else fs_is
                fs_is = fs.show('cf') if fs_is is None or len(fs_bs.columns) != len(fs_is.columns) else fs_is
                if fs_is is None or len(fs_bs.columns) != len(fs_is.columns):
                    print('No FS_IS [{:s}]{:s}'.format( corp._info['stock_code'] , corp._info['corp_name']) )
                    continue
                one_company( fs, fs_bs, fs_is , corp._info['corp_code'],  corp._info['stock_code'] ,  corp._info['corp_name'] )
            except dart.errors.NoDataReceived:
                print( 'No Analytics [{:s}]{:s}'.format( corp._info['stock_code'] , corp._info['corp_name']) )
            except dart.errors.NotFoundConsolidated:
                print( 'No Analytics [{:s}]{:s}'.format( corp._info['stock_code'] , corp._info['corp_name']) )
            

main2ErrorCheck()