
"""
    code : 회사코드
    name : 회사이름
    liabilities_risk_ratio : 유동부채의 위험 배수
    stockprice : 현재 주가
    totalStockCount : 현재 총 주식수
    df : 매년 회사 가치가 기록되는 DataFrame
    goal_rate_of_return : ?? 다시봐야할듯!!
"""
import pandas as pd
import stockprice
from decimal import *

class CompanyValueAlgo1(object):
    def __init__(self, code, stock_code, name, liabilities_risk_ratio = 1.2, goal_rate_of_return=0.06 ):
        super().__init__()
        self.code = code
        self.stock_code = stock_code
        self.name = name
        self.liabilities_risk_ratio = liabilities_risk_ratio
        self.goal_rate_of_return = goal_rate_of_return

        self.stockprice = stockprice.get_close_stock_price_with_name( self.name )
        self.totalstockcount = stockprice.get_total_stock_count( stock_code )
        self.recentTotalStockPrice = stockprice.get_recent_open_total_stock_price( stock_code )
        self.df = pd.DataFrame()
        
        
    def getISDataColumns( self ):
        return {
            '당기순이익(손실)' : { '당기순이익(손실)' : 0 }
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
    
    def getExpectReturnRatio( self ):
        expectedCV = Decimal(self.df.loc[ '회사가치', self.df.columns[0] ]) + ( Decimal(self.df.loc[ '회사가치', self.df.columns[0] ] ) - Decimal(self.df.loc[ '회사가치', self.df.columns[1] ] ) )
        return Decimal(100)*(( expectedCV - self.recentTotalStockPrice ) / self.recentTotalStockPrice)


