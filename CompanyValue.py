
"""
    code : 회사코드
    name : 회사이름
    liabilities_risk_ratio : 유동부채의 위험 배수
    stockprice : 현재 주가
    totalStockCount : 현재 총 주식수
    df : 매년 회사 가치가 기록되는 DataFrame
    goal_rate_of_return : ?? 다시봐야할듯!!
"""

import FilePathManager as fm
import pandas as pd
import stockprice
from decimal import *
import os
import pickle

class Company(object):
    def __init__(self, code, stock_code, name, liabilities_risk_ratio = 1.2, goal_rate_of_return=0.06 ):
        super().__init__()
        self.isErrorCorp = False
        self.code = code
        self.stock_code = stock_code
        self.name = name
        self.liabilities_risk_ratio = liabilities_risk_ratio
        self.goal_rate_of_return = goal_rate_of_return
        self.df = pd.DataFrame()
        self.info = {}
        try:
            self.totalStockCount = stockprice.get_total_stock_count( stock_code )
            self.recentTotalStockPrice = stockprice.get_recent_open_total_stock_price( stock_code )
        except Exception:
            self.isErrorCorp = True

        if not self.isErrorCorp and self.recentTotalStockPrice == 0:
            self.isErrorCorp = True
        
        if not self.isErrorCorp :
            self._info = {
                '이름' : self.name,
                '종목코드' : self.stock_code ,
                '시가총액' : self.recentTotalStockPrice,
                '총 주식 수' : self.totalStockCount,
                '부채 리스크율' : self.liabilities_risk_ratio,
                '선호 수익률' : self.goal_rate_of_return
            }

    def appendNewDateInfo( self, df ):
        self.df = pd.concat([self.df, df], axis=1)

    def saveResult( self ):
        prvfix_filePath = "{:s}/{:s}_{:s}".format(fm.goodCorpListDirectoryPath, self.name, self.stock_code )
        self.df.to_excel( prvfix_filePath+".xlsx" )
        f = open( prvfix_filePath+".pkl", "wb" )
        pickle.dump( self , f )
        f.close()

    def loadResult( self ):
        targetFileName = None
        for fileName in os.listdir( fm.goodCorpListDirectoryPath ):
            if fileName.find( self.name+"_"+self.code ) != -1 :
                targetFileName = fileName
                break
        if targetFileName == None:
            return None

        f = open( "{:s}/{:s}".format( fm.goodCorpListDirectoryPath, targetFileName) , "rb" )   
        dic = pickle.load(f)
        f.close()

    def to_Dict_info( self ):
        return self._info