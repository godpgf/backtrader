# 股票买卖策略回测

####写一个买入卖出策略

```python
import backtrader as bt
import numpy as np
import pandas as pd


class AnnualizedStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.simulate.datas[0].date[0]
        print('%s, %s' % (dt, txt))

    def __init__(self, simulate):
        bt.Strategy.__init__(self,simulate)
        # 使用收盘作为数据
        self.dataclose = self.simulate.datas[0].close



    def next(self):
        # 模拟器每一天都会调用这个函数
        self.log('Close, %.2f' % self.dataclose[0])

        # 如果当前订单数量是0，表示没有买入任何股票
        if len(self.simulate.orders) == 0:

            # 今天的股价小于昨天
            if self.dataclose[0] < self.dataclose[-1]:
                    # 昨天的股价小于前天

                    if self.dataclose[-1] < self.dataclose[-2]:
                        # 买入股票
                        self.log('BUY CREATE, %.2f' % self.dataclose[0])
                        self.buy()
                        #买入股票池中第二只股票，100股
                        #self.buy(self.datas[1], 100)


        else:

            # 如果持有某只股票超过5天
            if self.simulate.datas[0].date.offset >= (self.simulate.orders[0].offset + 5):
                # 卖出股票
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.sell()
                # 买入股票池中第二只股票，50股
                #self.sell(self.simulate.datas[1],50)
```

####用模拟器执行这个策略
```python
cerebro = bt.Simulator()
#加入一个策略（可以添加多个）
cerebro.addstrategy(AnnualizedStrategy)
#在股票池中添加一条股票数据，类型是pandas.DataFrame
cerebro.adddata(dataframe)
#设置当前投入资金
cerebro.setcash(100000.0)
#运行模拟器
cerebro.run()
#模拟的所有的交易日期
cerebro.statistics.date
#每个交易日期你的资金
cerebro.statistics.cash
```

####手动运行这个策略
```python
#coding=utf-8
#author=godpgf

import backtrader as bt
import numpy as np
import pandas as pd

if __name__ == '__main__':
    from stquant.data_adapt.DB import DB
    from stquant.benchmark import get_benchmark_returns, get_mul_2_one
    from stquant.plot.quant_plot import QuantPlot
    db = DB("test",True)
    data = db.get_all_data()
    ca = bt.ChargeAccount()
    ca.add_market_data(data)
    ca.add_data('000001',data.copy())
    history_close = [None,None]
    is_init = False
    hold_day = 0
    for index, row in data.iterrows():
        if is_init is False:
            for i in range(len(history_close)):
                if history_close[i] is None:
                    history_close[i] = row['Close']
                    if i == 1:
                        is_init = True
                    break
        else:
            #没有买入
            if hold_day <= 0 and history_close[0] > history_close[1] and history_close[1] > row['Close']:
                ca.add_charge(np.datetime64(index),'000001',200, True)
                hold_day = 5
            elif hold_day > 0:
                hold_day -= 1
                if hold_day == 0:
                    ca.add_charge(np.datetime64(index),'000001',-200, True)
            history_close[0] = history_close[1]
            history_close[1] = row['Close']
    br, ar = ca.back_trade()
    QuantPlot.show_quant_result('easy_strategy', br['rate'], ar['rate'])
```



