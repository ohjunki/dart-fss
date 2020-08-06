import FilePathManager as fm
import pickle
from pandas import DataFrame
import pandas as pd
import os
import MainFlow

def startGoodCorpListTest():
    count = 0
    goodCorpList = set()
    fileName = os.listdir( fm.goodCorpListInSharedDirectory )[0]
    for fileName in os.listdir( fm.goodCorpListInSharedDirectory ):
        resultDF : DataFrame = pd.read_pickle( '{:s}/{:s}'.format(fm.goodCorpListInSharedDirectory,fileName) )
        goodCorpList = goodCorpList.union( resultDF[ resultDF.columns[1] ] )

    MainFlow.startDartAnalytics(list(goodCorpList),'073110')
    
startGoodCorpListTest()

# MainFlow.startOneCompany('044340')