#coding=utf-8
#author=godpgf

class Strategy(object):

    def __init__(self, simulate):
        self.simulate = simulate

    def next(self):
        pass

    def buy(self, data = None, size = None, price = None):
        return self.simulate.buy(data, size, price)

    def sell(self, data = None, size = None, price = None):
        return self.simulate.sell(data, size, price)

    def is_training(self, data):
        return self.simulate.is_training(data)

    def getcash(self):
        return self.simulate.getcash()