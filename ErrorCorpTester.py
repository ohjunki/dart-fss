import dart_fss as dart
from dart_fss.corp.corp import Corp
import FilePathManager as fm
import pickle
from pandas import DataFrame
import pandas as pd
import os
import MainFlow

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
        MainFlow.extractCompanyValueFromAnalyist( fs_bs, fs_is, corp_code, stock_code, name )

    # f = open( "{s:}/oneMoreCompany.pkl".format(fm.resultDirectory) , "wb" )
    # pickle.dump( oneMoreCompany, f )
    # f.close()
    # f = open( "{s:}/oneMoreCompany.pkl".format(fm.sharedDirectory) , "wb" )
    # pickle.dump( oneMoreCompany, f )
    # f.close()
    
checkErrorCorp()
