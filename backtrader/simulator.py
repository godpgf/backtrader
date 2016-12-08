#coding=utf-8
#author=godpgf
from .statistics import Statistics
from  functools import partial

class IndexDate(object):

    def __init__(self, date, offset = 0):
        self.date = date.values
        self.offset = offset

    def __getitem__(self, item):
        if isinstance(item, slice):
            return self.date[slice(item.start + self.offset, item.stop + self.offset, item.step)]
        if self.offset + item >= len(self.date):
            return None
        return self.date[self.offset+item]

    def getcurdate(self):
        if self.offset >= len(self.date):
            return None
        return self.date[self.offset]

    def next(self):
        self.offset += 1

class Index(object):

    def __init__(self, date, index):
        self.date = date
        self.index = index

    def __getitem__(self, item):
        if isinstance(item,slice):
            return self.index[slice(item.start + self.date.offset, item.stop + self.date.offset, item.step)]
        else:
            return self.index[item+self.date.offset]

class Order(object):

    def __init__(self, data, size, price):
        self.data = data
        self.offset = data.date.offset
        self.price = price
        self.size = size

class Simulator(object):

    def __init__(self, trading_time = None):
        #所有交易时间
        self.trading_time = trading_time
        #所有策略
        self.strats = []
        #所有股票数据
        self.datas = []
        #当前模拟日期
        self.date = None
        #记录所有订单
        self.orders = []
        #所有资金
        self.cash = 0.0
        #统计
        self.statistics = Statistics(self)

    def is_training(self, data):
        return self.date == data.date.getcurdate() and data.volume[0] > 0

    def setcash(self, cash):
        self.cash = cash

    def getcash(self):
        return self.cash

    def getvalue(self):
        cash = 0
        for order in self.orders:
            cash += order.data.close[0] * order.size
        return self.cash + cash

    def addstrategy(self, strategy):
        self.strats.append(strategy)



    def adddata(self, data):
        self.datas.append(data)
        date = IndexDate(data.index)
        data.date = date
        for c in data.columns:
            setattr(data, c.lower(), Index(date, data[c].values))
        #data.open = Index(date, data.Open.values)
        #data.close = Index(date, data.Close.values)
        #data.high = Index(date, data.High.values)
        #data.low = Index(date, data.Low.values)
        #data.volume = Index(date, data.Volume.values)

    def buy(self, data = None, size = None, price = None):
        if data is None:
            data = self.datas[0]

        if self.is_training(data):
            if price is None:
                price = data.close[0]
            if size is None:
                size = self.getcash() // price
            self.cash -= size * price
            order = Order(data, size, price)
            self.orders.append(order)
            return order
        else:
            return None

    def sell(self, data = None, size = None, price = None):
        if data is None:
            data = self.datas[0]

        if self.is_training(data) is False:
            return False
        is_sell = False
        if price is None:
            price = data.close[0]
        for order in self.orders:
            if order.data is data:
                if size is None:
                    self.cash += price * order.size
                    order.size = 0
                    is_sell = True
                else:
                    if size == 0:
                        break;
                    else:
                        min_size = min(order.size, size)
                        self.cash += min_size * price
                        size -= min_size
                        order.size -= min_size
                        is_sell = True

        orders = []
        for order in self.orders:
            if order.size > 0:
                orders.append(order)
        self.orders = orders
        return is_sell

    def refresh_current_date(self):
        self.date = None
        for data in self.datas:
            if self.date is None:
                self.date = data.date[0]
            else:
                self.date = min(data.date[0],self.date)

    def run(self):
        #初始化最小日期
        self.refresh_current_date()

        strats = []
        for s in self.strats:
            strats.append(s(self))

        while self.date is not None:
            self.statistics.next()
            for s in strats:
                s.next()

            #下一天
            for data in self.datas:
                if data.date.getcurdate() == self.date:
                    data.date.next()

            self.refresh_current_date()



