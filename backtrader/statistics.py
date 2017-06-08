#coding=utf-8
#author=godpgf

class Statistics(object):

    def __init__(self, simulator):
        #总现金
        self.cash = []
        #余额
        self.balance = []
        #日期
        self.date = []
        self.simulator = simulator

    def next(self):
        self.cash.append(self.simulator.getvalue())
        self.balance.append(self.simulator.cash)
        self.date.append(self.simulator.date)