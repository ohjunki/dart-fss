from datetime import date
import os
import pickle

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

rootDirectory = "CorpDatas"
ensure_dir(rootDirectory)

#### rootDirectory must exist ####
tryStep = '{:s}[3]'.format( str(date.today()) )
rootStepDirectory = "{:s}/{:s}".format(rootDirectory, tryStep)
ensure_dir(rootStepDirectory)

corpListDartDataDirectory= '{:s}/CorpListDartData'.format( rootDirectory )
ensure_dir(corpListDartDataDirectory)

#### rootStepDirectory must exist ####
resultDirectory= '{:s}/Result'.format( rootStepDirectory )
ensure_dir(resultDirectory)

errorCompDir= '{:s}/ErrorComp'.format( rootStepDirectory )
ensure_dir(errorCompDir)
errorCompYearDir= '{:s}/ErrorComp/Year'.format( rootStepDirectory )
ensure_dir(errorCompYearDir)
errorCompQuarterDir= '{:s}/ErrorComp/Quarter'.format( rootStepDirectory )
ensure_dir(errorCompQuarterDir)

goodCorpListDirectoryPath= '{:s}/GoodCorpList'.format( rootStepDirectory )
ensure_dir(goodCorpListDirectoryPath)

sharedDirectory = '{:s}/SharedDirectory'.format( rootDirectory )
ensure_dir(sharedDirectory)

goodCorpListInSharedDirectory = '{:s}/SharedDirectory/GoodCorpList'.format( rootDirectory )
ensure_dir(goodCorpListInSharedDirectory)

def loadFS( code , stockCode , name , path ):
    try:
        f = open( '{:s}/{:s}_{:s}_{:s}_fs_bs.pkl'.format( path, code , stockCode , name ) , "rb" )
        fs_bs = pickle.load( f )
        f.close()
        f = open( '{:s}/{:s}_{:s}_{:s}_fs_is.pkl'.format( path, code , stockCode , name ) , "rb" )
        fs_is = pickle.load( f )
        f.close()
        return fs_bs, fs_is
    except Exception as e:
        print( str(e))
        return None, None

def saveFS( code , stockCode , name, fs_bs, fs_is , path ):
    fs_bs.to_pickle( '{:s}/{:s}_{:s}_{:s}_fs_bs.pkl'.format( path, code , stockCode , name ) )
    fs_is.to_pickle( '{:s}/{:s}_{:s}_{:s}_fs_is.pkl'.format( path, code , stockCode , name ) )
