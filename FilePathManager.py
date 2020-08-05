from datetime import date
import os

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

goodCorpListDirectoryPath= '{:s}/GoodCorpList'.format( rootStepDirectory )
ensure_dir(goodCorpListDirectoryPath)

sharedDirectory = '{:s}/SharedDirectory'.format( rootDirectory )
ensure_dir(sharedDirectory)