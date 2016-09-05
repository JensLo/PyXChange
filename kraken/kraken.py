# -*- coding: utf-8 -*-
# Copyright (c) 2016 Jens Lorrmann

from connection import Connection
from exchange import BaseExchange
from keyhandler import AbstractKeyHandler

import hashlib
import hmac
import urllib
import base64
import time


class KrakenKeyHandler(AbstractKeyHandler):
    '''
    Kraken KeyHandler
    '''
        
    def authRequest(self, key, url, params={} ):
        
        secret = self.getSecret( key )
        params['nonce'] = self.getNextNonce( key )
        
        message = url + hashlib.sha256( str( params['nonce'] ) +
                                            urllib.urlencode( params ) 
                                            ).digest()
                                           
        signature = hmac.new( base64.b64decode( secret ), message, 
                             hashlib.sha512 )
        header = {
            'API-Key': key,
            'API-Sign': base64.b64encode( signature.digest() )
        }
    
        return header, params
        
    def _resetNonce(self, key):
        self.setNextNonce(key, int(1000*time.time()))
        

class KrakenExchange(BaseExchange):
    '''
    Kraken Exchange
    '''

    
    NAME            = "Kraken"
    DOMAIN          = "api.kraken.com"
    API_URL         = "https://api.kraken.com/"
    HISTORICAL_DATA = True
    MARGIN_TRADING  = True
    LENDING         = False
    
    def _setupConnection(self):
        self.connection = Connection( self )
    
    
    def publicQuery(self, command, **params):
        """
        Generates the URL and the params
        """
        url = "/0/public/" + command
        return self.connection.makeRequest(url, params )
    
    def privateQuery(self, command, **params):
        """
        Send the order to the brokerage.
        """
        url = "/0/private/" + command
        headers, params = self.keyhandler.authRequest(self.key, url, params)
        return self.connection.makeRequest(url, params, headers )
       
        
    def _pair(self):
        """
        Send the order to the brokerage.
        """
        pass
        
        
    def _getfees(self):
        """
        Send the order to the brokerage.
        """
        pass
        
        
    def _getassets(self):
        """
        Send the order to the brokerage.
        """
        pass
        

    def _getminmaxorders(self):
        """
        Send the order to the brokerage.
        """
        pass
      
      
    def getTicker(self, pair):
        """Retrieve the ticker for the given pair.  Returns a Ticker instance."""
        pass
        

    def getOrderBook(self, pair):
        """Retrieve the orderbook for the given pair.  Returns a tuple (asks, bids);
        each of these is a list of (price, volume) tuples."""    
        pass


    def getTradeHistory(self, pair):
        """Retrieve the trade history for the given pair.  Returns a list of
        Trade instances.  If count is not None, it should be an integer, and
        specifies the number of items from the trade history that will be
        processed and returned."""
        pass


    def getTickHistory(self, pair, start=None, stop=None):
        """Retrieve the ticker history for the given pair.  Returns a list of
        Ticker instances.  If count is not None, it should be an integer, and
        specifies the number of items from the trade history that will be
        processed and returned."""
        pass


class OrderBookItem(object):
    __slots__ = ("pair", "type", "value", "amount", "date")

    def __init__(self, **kwargs):
        for s in Ticker.__slots__:
            setattr(self, s, kwargs.get(s))

        self.date = datetime.datetime.fromtimestamp(self.date)

    def __getstate__(self):
        return dict((k, getattr(self, k)) for k in Ticker.__slots__)

    def __setstate__(self, state):
        for k, v in state.items():
            setattr(self, k, v)

class OHLCV(object):
    __slots__ = ( "pair", "open", "high", "low", "close", "volume", "avg", 
                  "updated", "date" )

    def __init__(self, **kwargs):
        for s in Ticker.__slots__:
            setattr(self, s, kwargs.get(s))

        self.updated = datetime.datetime.fromtimestamp(self.updated)
        self.date = datetime.datetime.fromtimestamp(self.date)

    def __getstate__(self):
        return dict((k, getattr(self, k)) for k in Ticker.__slots__)

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
