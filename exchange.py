# -*- coding: utf-8 -*-
# Copyright (c) 2016 Jens Lorrmann


from __future__ import print_function

from abc import ABCMeta, abstractmethod
from common import AbstractAttribute
from keyhandler import AbstractKeyHandler

import datetime
import decimal


class BaseExchange(object):
    """
    Provides an abstract base class to handle all broker information.
    """

    __metaclass__   = ABCMeta
    NAME            = AbstractAttribute("The broker's name.")
    DOMAIN          = AbstractAttribute("The broker's domain.")   
    API_URL         = AbstractAttribute("The broker's api adress.")  
    HISTORICAL_DATA = AbstractAttribute("The broker's api adress.")
    MARGIN_TRADING  = AbstractAttribute("The broker's api adress.")
    LENDING         = AbstractAttribute("The broker's api adress.")
    HEADER          = {"Content-type": "application/x-www-form-urlencoded"}
    
    def __init__( self, key, keyhandler, ):
        self.key = key
        self.keyhandler = keyhandler
        if not isinstance(self.keyhandler, AbstractKeyHandler):
            raise TypeError("The handler argument must be a"
                            " keyhandler.AbstractKeyHandler, such as"
                            " keyhandler.KeyHandler")

        # We depend on the key handler for the secret
        self.secret = self.keyhandler.getSecret( self.key )
        self._setupConnection()
        
    @abstractmethod
    def _setupConnection(self):
        """
        Generates the URL and the params
        """
        pass
        
        
    @abstractmethod
    def publicQuery(self, command, **params):
        """
        Generates the URL and the params
        """
        pass
        
    
    @abstractmethod
    def privateQuery(self, command, **params):
        """
        Send the order to the brokerage.
        """
        pass
        
        
    @abstractmethod
    def _pair(self):
        """
        Send the order to the brokerage.
        """
        pass
        
        
    @abstractmethod
    def _getfees(self):
        """
        Send the order to the brokerage.
        """
        pass
        
        
    @abstractmethod
    def _getassets(self):
        """
        Send the order to the brokerage.
        """
        pass
    
        
    @abstractmethod
    def _getminmaxorders(self):
        """
        Send the order to the brokerage.
        """
        pass
      
      
    @abstractmethod
    def getTicker(self, pair):
        """Retrieve the ticker for the given pair.  Returns a Ticker instance."""
        pass
        

    @abstractmethod
    def getOrderBook(self, pair):
        """Retrieve the orderbook for the given pair.  Returns a tuple (asks, bids);
        each of these is a list of (price, volume) tuples."""    
        pass


    @abstractmethod
    def getTradeHistory(self, pair):
        """Retrieve the trade history for the given pair.  Returns a list of
        Trade instances.  If count is not None, it should be an integer, and
        specifies the number of items from the trade history that will be
        processed and returned."""
        pass
    

    @abstractmethod
    def getTickHistory(self, pair, start=None, stop=None):
        """Retrieve the ticker history for the given pair.  Returns a list of
        Ticker instances.  If count is not None, it should be an integer, and
        specifies the number of items from the trade history that will be
        processed and returned."""
        pass


class OrderBookItem(object):
    __slots__ = ("pair", "type", "value", "amount", "date")

    def __init__(self, **kwargs):
        for s in OrderBookItem.__slots__:
            setattr(self, s, kwargs.get(s))

        self.date = datetime.datetime.fromtimestamp(self.date)

    def __getstate__(self):
        return dict((k, getattr(self, k)) for k in OrderBookItem.__slots__)

    def __setstate__(self, state):
        for k, v in state.items():
            setattr(self, k, v)

class OHLCV(object):
    __slots__ = ( "pair", "open", "high", "low", "close", "volume", "avg", 
                  "updated", "date" )

    def __init__(self, **kwargs):
        for s in OHLCV.__slots__:
            setattr(self, s, kwargs.get(s))

        self.updated = datetime.datetime.fromtimestamp(self.updated)
        self.date = datetime.datetime.fromtimestamp(self.date)

    def __getstate__(self):
        return dict((k, getattr(self, k)) for k in OHLCV.__slots__)

    def __setstate__(self, state):
        for k, v in state.items():
            setattr(self, k, v)

class Trade(object):
    __slots__ = ("pair", "trade_type", "price", "tid", "amount", "date")

    def __init__(self, **kwargs):
        for s in Trade.__slots__:
            setattr(self, s, kwargs.get(s))

        if type(self.date) in (int, float, decimal.Decimal):
            self.date = datetime.datetime.fromtimestamp(self.date)
        elif type(self.date) in (str, unicode):
            if "." in self.date:
                self.date = datetime.datetime.strptime(self.date,
                                                       "%Y-%m-%d %H:%M:%S.%f")
            else:
                self.date = datetime.datetime.strptime(self.date,
                                                       "%Y-%m-%d %H:%M:%S")

    def __getstate__(self):
        return dict((k, getattr(self, k)) for k in Trade.__slots__)

    def __setstate__(self, state):
        for k, v in state.items():
            setattr(self, k, v)


class TradeAccountInfo(object):
    '''An instance of this class will be returned by
    a successful call to TradeAPI.getInfo.'''

    __slots__ =  ("date", "open_orders", "transaction_count", "info_rights", 
                  "withdraw_rights", "trade_rights")
    
    def __init__(self, info):
        funds = info.get(u'funds')
        for c in common.all_currencies:
            setattr(self, "balance_%s" % c, funds.get(unicode(c), 0))

        self.open_orders = info.get(u'open_orders')
        self.date = datetime.fromtimestamp(info.get(u'server_time'))

        self.transaction_count = info.get(u'transaction_count')
        rights = info.get(u'rights')
        self.info_rights = (rights.get(u'info') == 1)
        self.withdraw_rights = (rights.get(u'withdraw') == 1)
        self.trade_rights = (rights.get(u'trade') == 1)


class TransactionHistoryItem(object):
    '''A list of instances of this class will be returned by
    a successful call to TradeAPI.transHistory.'''
    
    __slots__ =  ("type", "amount", "currency", "desc", "status", "date")
    
    def __init__(self, transaction_id, info):
        self.transaction_id = transaction_id
        
        for n in TransactionHistoryItem.__slots__:
            setattr(self, n, info.get(n))
        self.date = datetime.fromtimestamp(self.date)


class TradeHistoryItem(object):
    '''A list of instances of this class will be returned by
    a successful call to TradeAPI.tradeHistory.'''

    __slots__ = ("pair", "type", "amount", "rate", "order_id", "is_your_order",
                 "date")
                 
    def __init__(self, transaction_id, info):
        self.transaction_id = transaction_id
        
        for n in TradeHistoryItem.__slots__:
            setattr(self, n, info.get(n))
        self.date = datetime.fromtimestamp(self.date)


class OrderItem(object):
    '''A list of instances of this class will be returned by
    a successful call to TradeAPI.activeOrders.'''
    
    __slots__ = ("pair", "type", "amount", "rate", "date", "status")
    
    def __init__(self, order_id, info):
        self.order_id = int(order_id)
        
        for n in OrderItem.__slots__:
            setattr(self, n, info.get(n))
        self.date = datetime.fromtimestamp(self.date)


class TradeResult(object):
    '''An instance of this class will be returned by
    a successful call to TradeAPI.trade.'''

    def __init__(self, info):
        self.received = info.get(u"received")
        self.remains = info.get(u"remains")
        self.order_id = info.get(u"order_id")
        funds = info.get(u'funds')
        for c in common.all_currencies:
            setattr(self, "balance_%s" % c, funds.get(unicode(c), 0))


class CancelOrderResult(object):
    '''An instance of this class will be returned by
    a successful call to TradeAPI.cancelOrder.'''

    def __init__(self, info):
        self.order_id = info.get(u"order_id")
        funds = info.get(u'funds')
        for c in common.all_currencies:
            setattr(self, "balance_%s" % c, funds.get(unicode(c), 0))

        
'''
    def _validatePair(self, pair):
        if pair not in self.all_pairs:
            if "_" in pair:
                a, b = pair.split("_", 1)
                swapped_pair = "%s_%s" % (b, a)
                if swapped_pair in self.all_pairs:
                    msg = "Unrecognized pair: %r (did you mean %s?)"
                    msg = msg % (pair, swapped_pair)
                    raise InvalidTradePairException(msg)
            raise InvalidTradePairException("Unrecognized pair: %r" % pair)


    def _validateOrder(pair, trade_type, rate, amount):
        validatePair(pair)
        if trade_type not in ("buy", "sell"):
            raise InvalidTradeTypeException("Unrecognized trade type: %r" % trade_type)
    
        minimum_amount = self.min_orders[pair]
        formatted_min_amount = formatCurrency(minimum_amount, pair)
        if amount < minimum_amount:
            msg = "Trade amount %r too small; should be >= %s" % \
                  (amount, formatted_min_amount)
            raise InvalidTradeAmountException(msg)
    
    
    def _truncateAmountDigits(value, digits):
        quantum = exps[digits]
        if type(value) is float:
            value = str(value)
        if type(value) is str:
            value = decimal.Decimal(value)
        return value.quantize(quantum)
    
    
    def _truncateAmount(value, pair):
        return truncateAmountDigits(value, self.max_digits[pair])
    
    
    def _formatCurrencyDigits(value, digits):
        s = str(truncateAmountDigits(value, digits))
        s = s.rstrip("0")
        if s[-1] == ".":
            s = "%s0" % s
    
        return s
    
    
    def _formatCurrency(value, pair):
        return formatCurrencyDigits(value, self.max_digits[pair])    
    
'''
