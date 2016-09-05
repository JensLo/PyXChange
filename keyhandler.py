# Copyright (c) 2013-2015 Alan McIntyre


from abc import ABCMeta, abstractmethod
from xcptions import InvalidNonceException
import inspect, os


class KeyData(object):
    def __init__(self, secret, nonce):
        self.secret = secret
        self.nonce = nonce

    # BTC-e's API caps nonces' values
    MAX_NONCE_VALUE = 42949672940000000

    def setNonce(self, newNonce):
        if newNonce <= 0:
            raise InvalidNonceException('Nonces must be positive')
        if newNonce <= self.nonce:
            raise InvalidNonceException('Nonces must be strictly increasing')
        if newNonce > self.MAX_NONCE_VALUE:
            raise InvalidNonceException('Nonces cannot be greater than %d' %
                                        self.MAX_NONCE_VALUE)

        self.nonce = newNonce

        return self.nonce

    def incrementNonce(self):
        if self.nonce >= self.MAX_NONCE_VALUE:
            raise InvalidNonceException('Cannot increment nonce, already at'
                                        ' maximum value')

        self.nonce += 1

        return self.nonce


class AbstractKeyHandler(object):
    '''AbstractKeyHandler handles the tedious task of managing nonces
    associated with BTC-e API key/secret pairs.
    The getNextNonce method is threadsafe, all others need not be.'''
    
    __metaclass__   = ABCMeta
    
    def __init__(self, resaveOnDeletion=True):
        '''The given file is assumed to be a text file with three lines
        (key, secret, nonce) per entry.'''
        if not resaveOnDeletion:
            warnings.warn("The resaveOnDeletion argument to KeyHandler will"
                          " default to True in future versions.")
                         
        self.resaveOnDeletion = resaveOnDeletion
        
        _curfname = inspect.getfile(self.__class__)
        _fpath = os.path.dirname(os.path.abspath(_curfname))
        self.filename = _fpath + "/" + 'key_file'
        self._keys = {}
        self._loadKeys()

    @property
    def keys(self):
        return self._keys.keys()

    def getKeys(self):
        return self.keys

    def _loadKeys(self):
        if self.filename is not None:
            self._parse()

    def _updateDatastore(self):
        if self.resaveOnDeletion and self.filename is not None:
            self._save()
            
    def _save(self):
        _curfname = inspect.getfile(inspect.currentframe())
        _fpath = os.path.dirname(os.path.abspath(_curfname))
        with open(self.filename, 'wt') as file:
            for k, data in self._keys.iteritems():
                file.write("%s\n%s\n%d\n" % (k, data.secret, data.nonce))

    def _parse(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'rt') as input_file:
                while True:
                    key = input_file.readline().strip()
                    if not key:
                        break
                    secret = input_file.readline().strip()
                    nonce = int(input_file.readline().strip())
                    self.addKey(key, secret, nonce)
        
    @abstractmethod
    def authRequest(self, key):
        raise NotImplementedError("Should implement authRequest()")

    def __del__(self):
        self.close()

    def close(self):
        self._updateDatastore()

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        self.close()

    def addKey(self, key, secret, next_nonce):
        self._keys[key] = KeyData(secret, next_nonce)
        return self

    def getNextNonce(self, key):
        return self.getKey(key).incrementNonce()

    def getSecret(self, key):
        return self.getKey(key).secret

    def setNextNonce(self, key, nextNonce):
        return self.getKey(key).setNonce(nextNonce)

    def getKey(self, key):
        data = self._keys.get(key)
        if data is None:
            raise KeyError("Key not found: %r" % key)

        return data
