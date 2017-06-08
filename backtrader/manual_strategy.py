#coding=utf-8
#author=godpgf
import numpy as np
import pandas as pd
from .strategy import Strategy
from .simulator import Simulator


class ChargeItem(object):
    def __init__(self, date, code, size, is_close = False):
        #交易日期
        self.date = date
        #交易股票码
        self.code = code
        #交易数量(负数表示卖出，正数表示买入)
        self.size = size
        #是否是在收盘时交易
        self.is_close = is_close


class ChargeAccount(object):
    def __init__(self):
        #ChargeItem列表
        self.charge_list = list()
        #股票数据
        self.data_dict = dict()
        #市场数据
        self.market_data = None

    #必须按照时间顺序交易
    def add_charge(self, date, code, size, is_close = False):
        self.charge_list.append(ChargeItem(date, code, size, is_close))

    def get_all_codes(self):
        codes = set()
        for ci in self.charge_list:
            if ci.code not in codes:
                codes.add(ci.code)
        return codes

    #加入股票数据
    def add_data(self, code, dataframe):
        self.data_dict[code] = dataframe

    #加入市场数据
    def add_market_data(self, dataframe):
        self.market_data = dataframe

    #模拟回测
    def back_trade(self):
        #测试市场收益-----------------------------------
        mark_cerebro = Simulator()
        mark_cerebro.addstrategy(BenchmarkStrategy)
        mark_cerebro.adddata(self.market_data)
        mark_cerebro.setcash(100000.0)
        mark_cerebro.run()
        #得到市场收益率
        mark_ratio = np.array(mark_cerebro.statistics.cash)
        mark_ratio = (mark_ratio - mark_ratio[0]) / mark_ratio[0]
        mark_ratio = pd.DataFrame(mark_ratio, np.array(mark_cerebro.statistics.date), columns=["rate"])

        #测试策略收益------------------------------------
        cerebro = Simulator()
        cerebro.addstrategy(ManualStrategy)
        #第一个股票必须是市场
        cerebro.adddata(self.market_data)
        cerebro.code2id = dict()
        index = 1
        for key, value in self.data_dict.items():
            cerebro.adddata(value)
            cerebro.code2id[key] = index
            index += 1
        cerebro.charge_list = self.charge_list
        #设置100万保证钱够用
        cerebro.setcash(1000000.0)
        cerebro.run()
        #得到策略收益率
        ratio = np.array(cerebro.statistics.cash)
        balance = np.array(cerebro.statistics.balance)
        #去掉压根从来没有使用的钱，去计算收益率
        ratio -= np.min(balance)
        ratio = (ratio - ratio[0]) / ratio[0]
        ratio = pd.DataFrame(ratio, np.array(cerebro.statistics.date), columns=["rate"])

        return mark_ratio, ratio


class BenchmarkStrategy(Strategy):
    def __init__(self, simulate):
        Strategy.__init__(self,simulate)
        self.is_buy = False

    def next(self):
        if self.is_buy is False:
            self.is_buy = True
            self.order = self.buy()


class ManualStrategy(Strategy):
    def __init__(self, simulate):
        Strategy.__init__(self,simulate)
        simulate.charge_index = 0

    def next(self):
        if self.simulator.charge_index >= len(self.simulate.charge_list):
            return
        assert self.simulator.date <= self.get_cur_charge().date
        if self.simulator.date < self.get_cur_charge().date:
            return

        while self.simulator.charge_index < len(self.simulate.charge_list) and self.simulator.date == self.get_cur_charge().date:
            self.do_cur_charge()
            self.simulator.charge_index += 1

    def get_cur_charge(self):
        return self.simulate.charge_list[self.simulator.charge_index]

    def do_cur_charge(self):
        ci = self.get_cur_charge()
        data = self.simulate.datas[self.simulate.data_dict[ci.code]]
        if ci.size > 0:
            self.buy(data, ci.size, data.close[0] if ci.is_close else data.open[0])
        elif ci.size < 0:
            self.sell(data, -ci.size, data.close[0] if ci.is_close else data.open[0])