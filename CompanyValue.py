
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


class CompanyValueAlgo1(object):
    def __init__(self, code, stock_code, name, liabilities_risk_ratio = 1.2, goal_rate_of_return=0.06 ):
        super().__init__()
        self.isErrorCorp = False
        self.code = code
        self.stock_code = stock_code
        self.name = name
        self.liabilities_risk_ratio = liabilities_risk_ratio
        self.goal_rate_of_return = goal_rate_of_return
        self.df = pd.DataFrame()
        try:
            self.stockprice = stockprice.get_close_stock_price_with_name( self.name )
            self.totalstockcount = stockprice.get_total_stock_count( stock_code )
            self.recentTotalStockPrice = stockprice.get_recent_open_total_stock_price( stock_code )
        except Exception:
            self.isErrorCorp = True

        if not self.isErrorCorp and self.recentTotalStockPrice == 0:
            self.isErrorCorp = True
        
        
    def getISDataColumns( self ):
        return {
            '당기순이익(손실)' : { 
                '당기순이익(손실)' : 0 ,
                '당기순손실' : 0
            }
        }
        # something
    def getBSDataColumns( self):
        return { 
            '유동자산' : { '유동자산' : 0  },
            '투자자산' : {
                '장기매도가능금융자산' : 0 ,
                '만기보유금융자산' : 0 ,
                '상각후원가금융자산' : 0 ,
                '기타포괄손익-공정가치금융자산' : 0 ,
                '당기손익-공정가치금융자산' : 0 ,
                '관계기업 및 공동기업 투자' : 0 ,
            },
            '유동부채' : { '유동부채' : 0 },
            '비유동부채' : { '비유동부채' : 0 },
        }
    def getDFindex( self ):
        return [ '유동자산', '투자자산', '유동부채', '비유동부채', '당기순이익(손실)', '회사가치' ]

    def appendNewDateInfo( self, df ):
        self.df = pd.concat([self.df, df], axis=1)


    def calculateCompanyValue( self ):
        for column in self.df.columns:
            data = self.df.loc[ : , column]
            value = data['유동자산'] + data['투자자산'] - data['유동부채']*Decimal(self.liabilities_risk_ratio) - data['비유동부채']
            if data['당기순이익(손실)'] > 0 :
                value += data['당기순이익(손실)']*Decimal(0.6)/Decimal(self.goal_rate_of_return)
            self.df.loc['회사가치'][column] = value

        self.cv2019 = self.df.loc[ '회사가치', self.df.columns[0] ]
        self.cv2018 = self.df.loc[ '회사가치', self.df.columns[1] ] if len(self.df.columns) > 2 else 0
        self.cv2017 = self.df.loc[ '회사가치', self.df.columns[2] ] if len(self.df.columns) > 3 else 0
        self.cv2016 = self.df.loc[ '회사가치', self.df.columns[3] ] if len(self.df.columns) > 4 else 0
        
        #increse = (( self.cv2019-self.cv2018 )*Decimal(3) + ( self.cv2018-self.cv2017 )*Decimal(2) + ( self.cv2017-self.cv2016 ) )/Decimal(6)
        self.cv2020 = self.cv2019 #+increse
        self.expectReturnRatio = Decimal(100)*(( self.cv2020 - self.recentTotalStockPrice ) / self.recentTotalStockPrice)
        self.df.append(pd.DataFrame( [ self.recentTotalStockPrice ] , index=['현재가치'] , columns=[self.df.columns[0]] ))
        self.df.append(pd.DataFrame( [ self.getExpectReturnRatio() ] , index=['예상수익률'] , columns=[self.df.columns[0]] ))
        
    def getExpectReturnRatio( self ):
        return self.expectReturnRatio

    def saveResult( self ):
        prvfix_filePath = "{:s}/[{:s}]{:s}_{:s}".format(fm.goodCorpListDirectoryPath, str(int(self.expectReturnRatio)), self.name, self.stock_code )
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
        return { 
            '이름' : self.name,
            '종목코드' : self.stock_code ,
            '수익률' : self.expectReturnRatio,
            '시가총액' : self.recentTotalStockPrice,
            'cv2020' : self.cv2020,
            'cv2019' : self.cv2019,
            'cv2018' : self.cv2018,
            'cv2017' : self.cv2017,
            'cv2016' : self.cv2016,
            '총 주식 수' : self.totalstockcount,
            '부채 리스크율' : self.liabilities_risk_ratio,
            '선호 수익률' : self.goal_rate_of_return,
        }