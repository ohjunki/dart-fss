# -*- coding: utf-8 -*-
import re
from typing import Union, List
from dart_fss.utils import Singleton, Spinner
from dart_fss.api.filings import get_corp_code
from dart_fss.api.market import get_stock_market_list
from dart_fss.corp.corp import Corp
from dart_fss.corp.corp import CorpFromFile
import pickle
import os


def get_corp_list(loadFromFile = False):
    """ DART 공시된 회사 리스트 반환

    Returns
    -------
    CorpList
        회사 리스트
    """
    return CorpList(False,loadFromFile)


def market_type_checker(market: Union[str, list]) -> List[str]:
    """ Market Type Checker

    Parameters
    ----------
    market: str or list of str
        Market type -> Y: 유가증권시장, K: 코스닥, N: 코넥스, E: 기타
    Returns
    -------
    list of str
        Market type 리스트
    """
    # str 타입인 경우 list 로 변경
    if isinstance(market, str):
        market = [x for x in market]
    # 대문자로 변경
    market = [x.upper() for x in market]

    # market type 체크
    for m in market:
        if m not in ['Y', 'K', 'N', 'E']:
            raise ValueError('Invalid market type')
    return market


corpListDirectoryPath = os.getcwd()+"/corpList"
class CorpList(object, metaclass=Singleton):
    def __init__(self, profile=False, loadFromFile=False):
        self.loadFromFile = loadFromFile
        """ CorpList 초기화

        Parameters
        ----------
        profile: bool
            Corp Class 반환시 Profile 자동 로딩 여부
        """
        self._corps = None
        self._corp_codes = dict()
        self._corp_names = []
        self._corp_cls_list = []
        self._corp_product = []
        self._corp_sector = []
        self._sectors = []

        self._stock_codes = dict()
        self._stock_market = dict()
        self._profile = profile

        if self._corps is None:
            self.load(profile=self._profile)

    def saveAllCops(self):
        corpInfoDic = {}
        for corp in self._corps:
            corpInfoDic[corp.corp_code] = corp.to_dict()
        f = open( corpListDirectoryPath+"/allDic", "wb" )   
        pickle.dump( corpInfoDic , f )
        f.close()

        f = open( corpListDirectoryPath+"/_stock_market", "wb" )  
        pickle.dump( self._stock_market , f )
        f.close() 

    def loadCorpsFromFiles(self):
        f = open( corpListDirectoryPath+"/allDic", "rb")
        dic = pickle.load(f)
        f.close()
        corp_list = []
        for key in dic.keys():
            corp_list.append(CorpFromFile(dic[key]))
        return corp_list

    def load(self, profile=False):
        """ 회사 정보 로딩

        Parameters
        ----------
        profile: bool, optional
            상세정보 로딩 여부
        """
        # Loading Stock Market Information
        spinner = Spinner('Loading Stock Market Information')
        spinner.start()
        if self.loadFromFile :
            f = open( corpListDirectoryPath+"/_stock_market", "rb")
            self._stock_market = pickle.load(f)
            f.close()
        else:
            for k in ['Y', 'K']:
                data = get_stock_market_list(k, False)
                self._stock_market = {**self._stock_market, **data}
        spinner.stop()

        spinner = Spinner('Loading Companies in OpenDART')
        spinner.start()
        sectors = set()

        if self.loadFromFile:
            self._corps = [x for x in self.loadCorpsFromFiles()]
        else:
            self._corps = [Corp(**x, profile=profile) for x in get_corp_code()]

        for idx, x in enumerate(self._corps):
            self._corp_codes[x.corp_code] = idx
            self._corp_names.append(x.corp_name)
            stock_code = x.stock_code
            # Market type check
            corp_cls = 'E'
            product = None
            sector = None
            if stock_code is not None:
                try:
                    info = self._stock_market[stock_code]
                    corp_cls = info['corp_cls']
                    product = info['product']
                    sector = info['sector']
                    sectors.add(sector)
                    self._stock_codes[stock_code] = idx
                    # Update information
                    x.update(info)
                except KeyError:
                    pass
            self._corp_cls_list.append(corp_cls)
            self._corp_product.append(product)
            self._corp_sector.append(sector)
        self._sectors = sorted(list(sectors))
        spinner.stop()

    @property
    def corps(self):
        """ 모든 상장된 종목(회사)를 반환한다 """
        if self._corps is None:
            self.load(profile=self._profile)
        return self._corps

    def find_by_corp_code(self, corp_code):
        """ DART에서 사용하는 회사 코드를 이용한 찾기

        Parameters
        ----------
        corp_code: str
            공시대상회사의 고유번호(8자리)

        Returns
        -------
        Corp
            회사 정보를 담고 있는 클래스
        """
        corps = self.corps
        idx = self._corp_codes.get(corp_code)
        return corps[idx] if idx is not None else None

    def find_by_corp_name(self, corp_name, exactly=False, market='YKNE'):
        """ 회사 명칭을 이용한 검색

        Parameters
        ----------
        corp_name: str
            공시대상회사의 고유번호(8자리)
        exactly: bool, optional
            corp_name과 정확히 일치 여부(default: False)
        market: str or list of str, optional
            'Y': 코스피, 'K': 코스닥, 'N': 코넥스, 'E': 기타
        Returns
        -------
        list of Corp
            회사 정보를 담고 있는 클래스 리스트
        """
        corps = self.corps
        res = []
        if exactly is True:
            corp_name = '^' + corp_name + '$'
        regex = re.compile(corp_name)

        # market 타입 체크 및 list로 변경
        market = market_type_checker(market)

        for idx, corp_name in enumerate(self._corp_names):
            if regex.search(corp_name) is not None:
                if self._corp_cls_list[idx] in market:
                    res.append(corps[idx])
        return res if len(res) > 0 else None

    def find_by_product(self, product, market='YKN'):
        """ 취급 상품으로 검색(코스피, 코스닥, 코넥스만 지원)

        Parameters
        ----------
        product: str
            상품
        market: str or list of str, optional
            'Y': 코스피, 'K': 코스닥, 'N': 코넥스, 'E': 기타
        Returns
        -------
        list of Corp
            회사 정보를 담고 있는 클래스 리스트
        """
        corps = self.corps
        res = []

        regex = re.compile(product)

        # market 타입 체크 및 list로 변경
        market = market_type_checker(market)
        if 'E' in market:
            raise ValueError('ETC Market is not supported')

        for idx, product in enumerate(self._corp_product):
            if product and regex.search(product) is not None:
                if self._corp_cls_list[idx] in market:
                    res.append(corps[idx])
        return res if len(res) > 0 else None

    def find_by_sector(self, sector, market='YKN'):
        """ 산업 섹터로 검색(코스피, 코스닥, 코넥스만 지원)

        Parameters
        ----------
        sector: str
            산업 섹
        market: str or list of str, optional
            'Y': 코스피, 'K': 코스닥, 'N': 코넥스, 'E': 기타
        Returns
        -------
        list of Corp
            회사 정보를 담고 있는 클래스 리스트
        """
        corps = self.corps
        res = []

        regex = re.compile(sector)

        # market 타입 체크 및 list로 변경
        market = market_type_checker(market)
        if 'E' in market:
            raise ValueError('ETC Market is not supported')

        for idx, sector in enumerate(self._corp_sector):
            if sector and regex.search(sector) is not None:
                if self._corp_cls_list[idx] in market:
                    res.append(corps[idx])
        return res if len(res) > 0 else None

    @property
    def sectors(self):
        return self._sectors

    def find_by_stock_code(self, stock_code):
        """ 주식 종목 코드를 이용한 찾기

        Parameters
        ----------
        stock_code: str
            주식 종목 코드(6자리)

        Returns
        -------
        Corp
            회사 정보를 담고 있는 클래스
        """
        corps = self.corps
        idx = self._stock_codes.get(stock_code)
        return corps[idx] if idx is not None else None

    def __repr__(self):
        corps = self.corps
        return 'Number of companies: {}'.format(len(corps))

    def __getitem__(self, item):
        corps = self.corps
        return corps[item]

    def __len__(self):
        corps = self.corps
        return len(corps)