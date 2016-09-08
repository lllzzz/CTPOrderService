#CTPOrderService

本系统为订单服务，为CTPService的配套服务，本服务对模型侧进行下单的简化封装，使模型侧不用关心具体的订单细节，专注模型逻辑。

当前本系统预定义的下单方式有如下几种：
*    强平单，即IOC市价单，平仓必成
*    实时开仓，下单模式为FAK，没成交不做进一步处理
*    实时平仓，FAK平仓，如果没成交，则向更多交易成本方向增加一个最小波动再次尝试FAK，尝试若干次以后（配置），IOC进行平仓，也就是说，采用这种方式平仓，一定会平掉。
*    预挂单，这种下单方式采用普通单下单，如果当时没有成交则进入排队状态，下单时可以指定撤单条件，当前的方式为通过监听tick信号进行处理。

其他方式可以逐步添加，这部分代码在src/orders/下，继承Base类，实现run，process方法即可，可参看其他OrderXXX的实现。


###使用说明
命令均在bin目录下

***./check.py*** 检查系统中应用的module是否存在

***./orderService start/stop appKey***  用于启动/关闭服务，其中appKey可以用来标示模型侧的ID，也就是说每个模型，或者每套模型参数对应一个appKey，从而对应本服务的一个实例。

***./orderService status*** 用户查看当前服务

另外将文件crontab下的命令复制到系统crontab中，其中的命令是用来统计下单的情况，这部分功能依赖CTPService中的订单详情，设计上也将本系统与CTPService的数据库放在了一起。

###配置说明
系统依赖Redis与Mysql服务，所以在配置中需要添加相关配置项。

####Sys
env环境配置项，当前只支持dev开发环境与online线上环境
close_trytimes，实时单平仓尝试次数，大于这个数时直接IOC强平，保证平仓成功

####Redis
对于本系统内使用Redis的情况，系统默认选择db = 1，不能配置，建议将redis_dev与redis_online中的db配置为1以外的其他值。

本系统需要依赖行情数据，所以需要监听tick频道，根据MS服务的设计，需要配置listen_tick配置项，格式为 ***tick_合约ID***；依赖模型侧下单命令，需要配置listen_model，格式为 ***model_order_appKey***，同事需要监听基础服务的订单反馈，所以配置listen_trade，格式 ***trade_rsp_%s***。

下单命令的广播为send_order，根据TS定义，格式为 ***trade***；给模型侧的反馈，send_order_rsp，格式为 ***order_rsp_appKey***。

####Mysql
Mysql中配置了K线系统的数据库，用以初始化K线数据。

####min_tick
配置合约价格的最小波动，这个没在CTP接口中找到，所以先手动配置，有待优化。

####交互格式
与CTPService的交互参考CTPService的定义。下面给出与模型侧的定义格式。

#####下单
    // IOC
    {
        type: 3,
        mid: 100, // 模型侧该笔交易的ID
        iid: 'hc1701',
        isBuy: 1,
        total: 2,
    }

    // 实时开仓
    {
        type: 1,
        mid: 100,
        iid: 'hc1701',
        price: 1002,
        isBuy: 1,
        total: 2,
    }

    // 实时平仓
    {
        type: 2,
        mid: 100,
        iid: 'hc1701',
        price: 10002,
        isBuy: 0,
        total: 2,
    }

    // 预挂单，撤单行为说明：在订单没成的情况下，如果当前最新价超出
    // cancelPriceH与cancelPriceL定义的范围之外，则进入撤单准备阶段，
    // 对于开仓，如果当前最新价超过目标价±cancelRange的范围之外，则
    // 取消订单，对于平仓，如果超过对手价±cancelRange的范围之外，则
    // 撤单。如果当前时间超过cancelTime，同样进行撤单。
    //
    // 以买开为例：当前价100，我们90下单买入，cancelRange为2，cancelPriceL为90，
    // cancelPriceH为105，则如果当前价达到90没成，则进入撤单判断，系统会读取
    // tick信号，当tick信号在88~92之外时，撤单。同样的如果当前价达到105，当然不
    // 会成，而最新的tick加也必然在88~92之外，所以会立刻撤单。对于平仓，只是将
    // 撤单准备阶段的用当前价判断，换为对手价判断。
    {
        mid: 100,
        iid: 'hc1701',
        price: 10008,
        isBuy: 1,
        isOpen: 1,
        total: 2,
        cancelRange: 2,
        cancelPriceH: 10008,
        cancelPriceL: 10002,
        cancelTime: 20160809_10:20:29,
    }

#####反馈
    {
        mid: 100,
        successVol: 2, // 成功的交易数
    }

