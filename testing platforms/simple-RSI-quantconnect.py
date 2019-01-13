import numpy as np
from decimal import Decimal

### <summary>
### Basic RSI reversal strategy - testing quantconnect features
### </summary>
class BasicTemplateAlgorithm(QCAlgorithm):
    '''Basic template algorithm simply initializes the date range and cash'''

    def Initialize(self):
        self.SetStartDate(2010,10, 7)  #Set Start Date
        self.SetEndDate(2018,4,10)    #Set End Date
        self.SetCash(10000)           #Set Strategy Cash
        # Import symbol
        self.symbol = "EURUSD"
        self.forex = self.AddForex(self.symbol, Resolution.Daily, Market.FXCM)
        # Import quantifications
        self.rsi = self.RSI(self.symbol, 5, MovingAverageType.Simple)
        self.ema = self.EMA(self.symbol, 200)
        # Tracking properties
        self.price = None
        self.isOrderOpen = False
        self.isLong = False
        self.isShort = False
        self.stopShort = None
        self.stopLong = None
        # set the brokerage model
        self.SetBrokerageModel(BrokerageName.FxcmBrokerage)
        self.positionSize = int((self.Portfolio.Cash * 10)/100)

    def OnData(self, data):
        # Defensive strategy to avoid errors
        if not self.rsi.IsReady or not self.ema.IsReady:
            self.Error("not loaded")
            return
        
        self.price = data[self.symbol].Close
        self.opex_offset = self.price + round(Decimal(0.005),2)
        self.stopLoss = self.price + round(Decimal(0.0060),2)
        
        # Long orders
        if self.price < self.ema.Current.Value and self.rsi.Current.Value < 25:
            if not self.isOrderOpen:
                self.Debug("Open long")
                self.isOrderOpen = True
                self.isLong = True
                self.StopMarketOrder(self.symbol, self.positionSize, self.opex_offset)
                # Put a stop loss in place
                self.stopLong = self.StopMarketOrder(self.symbol, -self.positionSize, self.stopLoss)
        
        # Short orders
        if self.price > self.ema.Current.Value and self.rsi.Current.Value > 75:
            if not self.isOrderOpen:
                self.Debug("Open short")
                self.isOrderOpen = True
                self.isShort = True
                self.StopMarketOrder(self.symbol, -self.positionSize, self.opex_offset)
                # Put a stop loss in place
                self.stopShort = self.StopMarketOrder(self.symbol, self.positionSize, self.stopLoss)
        
        # Closing rules Long
        if self.isOrderOpen and self.isLong :
            if self.rsi.Current.Value > 55:
                self.Debug("Closing Long")
                self.MarketOrder(self.symbol, -self.positionSize)
                self.isLong = False
                self.isOrderOpen = False
                self.stopLong = None
        
        # Closing rules Short
        if self.isOrderOpen and self.isShort:
            if self.rsi.Current.Value < 45:
                self.MarketOrder(self.symbol, self.positionSize)
                self.isShort = False
                self.isOrderOpen = False
                self.StopShort = None