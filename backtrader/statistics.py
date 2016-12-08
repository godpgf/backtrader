#coding=utf-8
#author=godpgf

class Statistics(object):

    def __init__(self, simulator):
        self.cash = []
        self.date = []
        self.simulator = simulator

    def next(self):
        self.cash.append(self.simulator.getvalue())
        self.date.append(self.simulator.date)