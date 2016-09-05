# -*- coding: utf-8 -*-
# Copyright (c) 2016 Jens Lorrmann

import decimal
import httplib
import json
import re
import os


decimal.getcontext().rounding = decimal.ROUND_DOWN
exps = [decimal.Decimal("1e-%d" % i) for i in range(16)]



class AbstractAttribute:
    """An abstract class attribute.

    Use this instead of an abstract property when you don't expect the
    attribute to be implemented by a property.

    """

    __isabstractmethod__ = True

    def __init__(self, doc=""):
        self.__doc__ = doc
    def __get__(self, obj, cls):
        return self