# -*- coding: utf-8 -*-
# Copyright (c) 2016 Jens Lorrmann


class InvalidTradePairException(Exception):
    """ Exception raised when an invalid pair is passed. """
    pass


class InvalidTradeTypeException(Exception):
    """ Exception raise when invalid trade type is passed. """
    pass


class InvalidTradeAmountException(Exception):
    """ Exception raised if trade amount is too much or too little. """
    pass


class APIResponseError(Exception):
    """ Exception raise if the API replies with an HTTP code
    not in the 2xx range. """
    pass


class InvalidNonceException(Exception):
    def __init__(self, method, expectedNonce, actualNonce):
        Exception.__init__(self)
        self.method = method
        self.expectedNonce = expectedNonce
        self.actualNonce = actualNonce

    def __str__(self):
        return "Expected a nonce greater than %d" % self.expectedNonce


class InvalidSortOrderException(Exception):
    ''' Exception thrown when an invalid sort order is passed '''
    pass

