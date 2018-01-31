# coding=utf-8
from __future__ import print_function, absolute_import, unicode_literals
from gm.api import *
import numpy as np
'''
本策略根据计算滚动的.过去的30个1min的bar的均值正负2个标准差得到布林线
并在最新价差上穿上轨来做空价差,下穿下轨来做多价差
并在回归至上下轨水平内的时候平仓
回测数据为:SHFE.rb1801和SHFE.hc1801的1min数据
回测时间为:2017-09-01 08:00:00到2017-10-01 16:00:00
'''
def init(context):
    # 进行套利的品种
    context.goods = ['SHFE.rb1801', 'SHFE.hc1801']
    # 订阅行情
    subscribe(symbols=context.goods, frequency='60s', count=31, wait_group=True)
def on_bar(context, bars):
    # 获取两个品种的时间序列
    data_rb = context.data(symbol=context.goods[0], frequency='60s', count=31, fields='close')
    close_rb = data_rb.values
    data_hc = context.data(symbol=context.goods[1], frequency='60s', count=31, fields='close')
    close_hc = data_hc.values
    # 计算价差
    spread = close_rb[:-1] - close_hc[:-1]
    # 计算布林带的上下轨
    up = np.mean(spread) + 2 * np.std(spread)
    down = np.mean(spread) - 2 * np.std(spread)
    # 计算最新价差
    spread_now = close_rb[-1] - close_hc[-1]
    # 无交易时若价差上(下)穿布林带上(下)轨则做空(多)价差
    position_rb_long = context.account().position(symbol=context.goods[0], side=PositionSide_Long)
    position_rb_short = context.account().position(symbol=context.goods[0], side=PositionSide_Short)
    if not position_rb_long and not position_rb_short:
        if spread_now > up:
            order_target_volume(symbol=context.goods[0], volume=1, order_type=OrderType_Market,
                                position_side=PositionSide_Short)
            print(context.goods[0], '以市价单开空仓一手')
            order_target_volume(symbol=context.goods[1], volume=1, order_type=OrderType_Market,
                                position_side=PositionSide_Long)
            print(context.goods[1], '以市价单开多仓一手')
        if spread_now < down:
            order_target_volume(symbol=context.goods[0], volume=1, order_type=OrderType_Market,
                                position_side=PositionSide_Long)
            print(context.goods[0], '以市价单开多仓一手')
            order_target_volume(symbol=context.goods[1], volume=1, order_type=OrderType_Market,
                                position_side=PositionSide_Short)
            print(context.goods[1], '以市价单开空仓一手')
    # 价差回归时平仓
    elif position_rb_short:
        if spread_now <= up:
            order_close_all()
            print('价格回归,平所有仓位')
            # 跌破下轨反向开仓
        if spread_now < down:
            order_target_volume(symbol=context.goods[0], volume=1, order_type=OrderType_Market,
                                position_side=PositionSide_Long)
            print(context.goods[0], '以市价单开多仓一手')
            order_target_volume(symbol=context.goods[1], volume=1, order_type=OrderType_Market,
                                position_side=PositionSide_Short)
            print(context.goods[1], '以市价单开空仓一手')
    elif position_rb_long:
        if spread_now >= down:
            order_close_all()
            print('价格回归,平所有仓位')
            # 涨破上轨反向开仓
        if spread_now > up:
            order_target_volume(symbol=context.goods[0], volume=1, order_type=OrderType_Market,
                                position_side=PositionSide_Short)
            print(context.goods[0], '以市价单开空仓一手')
            order_target_volume(symbol=context.goods[1], volume=1, order_type=OrderType_Market,
                                position_side=PositionSide_Long)
            print(context.goods[1], '以市价单开多仓一手')
if __name__ == '__main__':
    '''
    strategy_id策略ID,由系统生成
    filename文件名,请与本文件名保持一致
    mode实时模式:MODE_LIVE回测模式:MODE_BACKTEST
    token绑定计算机的ID,可在系统设置-密钥管理中生成
    backtest_start_time回测开始时间
    backtest_end_time回测结束时间
    backtest_adjust股票复权方式不复权:ADJUST_NONE前复权:ADJUST_PREV后复权:ADJUST_POST
    backtest_initial_cash回测初始资金
    backtest_commission_ratio回测佣金比例
    backtest_slippage_ratio回测滑点比例
    '''
    run(strategy_id='strategy_id',
        filename='main.py',
        mode=MODE_BACKTEST,
        token='token_id',
        backtest_start_time='2017-09-01 08:00:00',
        backtest_end_time='2017-10-01 16:00:00',
        backtest_adjust=ADJUST_PREV,
        backtest_initial_cash=500000,
        backtest_commission_ratio=0.0001,
        backtest_slippage_ratio=0.0001)