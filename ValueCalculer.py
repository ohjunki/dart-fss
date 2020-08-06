"""
    code : 회사코드
    name : 회사이름
    liabilities_risk_ratio : 유동부채의 위험 배수
    totalStockCount : 현재 총 주식수
    df : 매년 회사 가치가 기록되는 DataFrame
    goal_rate_of_return : ?? 다시봐야할듯!!
"""

import FilePathManager as fm
import pandas as pd
from decimal import *
import os
import pickle

class Model(object):
    def __init__(self, liabilities_risk_ratio = 1.2, goal_rate_of_return=0.06 ):
        self.liabilities_risk_ratio = liabilities_risk_ratio
        self.goal_rate_of_return = goal_rate_of_return
    """
        손익계산서에서 추출하는 데이터 리스트이다.
        또한 각 항목이 여러 이름으로 불릴 수 있기 떄문에 계산될 수 있는 항목리스트를 가지고 있다.
    """
    def getISDataColumns( self ):
        return {
            '영업이익' : { 
                '영업이익(손실)' : 0 ,
                '영업이익' : 0,
                '영업손실' : 0
            }
        }
    """
        대조대차표에서 추출하는 데이터 리스트이다.
        또한 각 항목이 여러 이름으로 불릴 수 있기 떄문에 계산될 수 있는 항목리스트를 가지고 있다.
    """
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
        return [ '유동자산', '투자자산', '유동부채', '비유동부채', '영업이익', '회사가치' ]

    """
        가장최근 분기부터 4년치의 가치를 분석
        4년치의 가치 성장평균을 최근분기가치에 더해서 계산한다. 더할때 비율은 n개년/4 ---- 4개년보다 적을 경우 비율감소
        미래가치와 현재가치의 평균을 최종가치로 평가한다.
        미래, 현재, 평균의 각각 수익률을 계산한다.
    """
    def calculateCompanyValue( self, df, company ):
        for column in df.columns:
            data = df.loc[ : , column]
            value = data['유동자산'] + data['투자자산'] - data['유동부채']*Decimal(self.liabilities_risk_ratio) - data['비유동부채']
            if data['영업이익'] > 0 :
                value += data['영업이익']*Decimal(0.6)/Decimal(self.goal_rate_of_return)
            df.loc['회사가치' , [column]] = value

        # TODO- columns SORT
        self._info = {}
        for column in df.columns:
            self._info[column] = Decimal(df.loc[ '회사가치', column ])
        
        valueDiffSum = Decimal(0)
        for index in range(1, min( 4, len(df.columns)-1 ) ):
            valueDiffSum += Decimal( df.loc[ '회사가치', df.columns[index] ] - df.loc[ '회사가치', df.columns[index-1] ] )
        
        if valueDiffSum != 0 :
            valueDiffSum /= Decimal(3)

        self.currentValue = Decimal(df.loc[ '회사가치', df.columns[0] ])
        self.feautureValue = self.currentValue + valueDiffSum
        self.avgValue = ( self.feautureValue + Decimal(df.loc[ '회사가치', df.columns[0] ]) ) / Decimal(2)
        self.currentReturnRatio = Decimal(100)*(( self.currentValue - company.recentTotalStockPrice ) / company.recentTotalStockPrice )
        self.featureReturnRatio = Decimal(100)*(( self.feautureValue - company.recentTotalStockPrice ) / company.recentTotalStockPrice)
        self.avgReturnRatio = Decimal(100)*(( self.avgValue - company.recentTotalStockPrice ) / company.recentTotalStockPrice)
        self.vb_cur_sp = self.currentValue / company.totalStockCount
        self.vb_fea_sp = self.feautureValue / company.totalStockCount
        self.vb_avg_sp = self.avgValue / company.totalStockCount
        self.writeToInfo()
        return df
        
    def writeToInfo( self ):
        self._info['현재가치'] = self.currentValue
        self._info['미래가치'] = self.feautureValue
        self._info['평균가치'] = self.avgValue
        self._info['현재수익률'] = self.currentReturnRatio
        self._info['미래수익률'] = self.featureReturnRatio
        self._info['평균수익률'] = self.avgReturnRatio
        self._info['예상현재주가'] = self.vb_cur_sp
        self._info['예상미래주가'] = self.vb_fea_sp
        self._info['예상평균주가'] = self.vb_avg_sp

    def isValuableCompany( self ):
        return self.avgReturnRatio > Decimal(30)

    def to_Dict_info( self ):
        return self._info