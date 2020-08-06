
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

class ValueDataFrameModel(object):
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

dataModel = ValueDataFrameModel()
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

    def getISDataColumns( self ):
        return dataModel.getISDataColumns()

    def getBSDataColumns( self):
        return dataModel.getBSDataColumns()

    def getDFindex( self ):
        return dataModel.getDFindex()

    def appendNewDateInfo( self, df ):
        self.df = pd.concat([self.df, df], axis=1)

    """
        가장최근 분기부터 4년치의 가치를 분석
        4년치의 가치 성장평균을 최근분기가치에 더해서 계산한다. 더할때 비율은 n개년/4 ---- 4개년보다 적을 경우 비율감소
        미래가치와 현재가치의 평균을 최종가치로 평가한다.
        미래, 현재, 평균의 각각 수익률을 계산한다.
    """
    def calculateCompanyValue( self ):
        for column in self.df.columns:
            data = self.df.loc[ : , column]
            value = data['유동자산'] + data['투자자산'] - data['유동부채']*Decimal(self.liabilities_risk_ratio) - data['비유동부채']
            if data['영업이익'] > 0 :
                value += data['영업이익']*Decimal(0.6)/Decimal(self.goal_rate_of_return)
            self.df.loc['회사가치' , [column]] = value

        # TODO- columns SORT
        for column in self.df.columns:
            self._info[column] = Decimal(self.df.loc[ '회사가치', column ])
        
        valueDiffSum = Decimal(0)
        for index in range(1, min( 4, len(self.df.columns)-1 ) ):
            valueDiffSum += Decimal( self.df.loc[ '회사가치', self.df.columns[index] ] - self.df.loc[ '회사가치', self.df.columns[index-1] ] )
        
        if valueDiffSum != 0 :
            valueDiffSum /= Decimal(3)

        self.currentValue = Decimal(self.df.loc[ '회사가치', self.df.columns[0] ])
        self.feautureValue = self.currentValue + valueDiffSum
        self.avgValue = ( self.feautureValue + Decimal(self.df.loc[ '회사가치', self.df.columns[0] ]) ) / Decimal(2)
        self.currentReturnRatio = Decimal(100)*(( self.currentValue - self.recentTotalStockPrice ) / self.recentTotalStockPrice )
        self.featureReturnRatio = Decimal(100)*(( self.feautureValue - self.recentTotalStockPrice ) / self.recentTotalStockPrice)
        self.avgReturnRatio = Decimal(100)*(( self.avgValue - self.recentTotalStockPrice ) / self.recentTotalStockPrice)
        self.vb_cur_sp = self.currentValue / self.totalStockCount
        self.vb_fea_sp = self.feautureValue / self.totalStockCount
        self.vb_avg_sp = self.avgValue / self.totalStockCount

        self.writeToInfo()
        
    def writeToInfo( self ):
        self._info['currentValue'] = self.currentValue
        self._info['feautureValue'] = self.feautureValue
        self._info['avgValue'] = self.avgValue
        self._info['currentReturnRatio'] = self.currentReturnRatio
        self._info['featureReturnRatio'] = self.featureReturnRatio
        self._info['avgReturnRatio'] = self.avgReturnRatio
        self._info['vb_cur_sp'] = self.vb_cur_sp
        self._info['vb_fea_sp'] = self.vb_fea_sp
        self._info['vb_avg_sp'] = self.vb_avg_sp

        
    def isValuableCompany( self ):
        return self.avgReturnRatio > Decimal(30)

    def saveResult( self ):
        prvfix_filePath = "{:s}/[{:s}]{:s}_{:s}".format(fm.goodCorpListDirectoryPath, str(int(self.avgReturnRatio)), self.name, self.stock_code )
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