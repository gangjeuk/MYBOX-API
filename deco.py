import functools
import time
import json
import os
from logging import DEBUG
from log import set_logger

'''
Decorators

Function List:

clock: Benchmark time usage of the function

write_json: Write json file of 'Response class' in requests package --> this is for mybox.py module

deprecated: Notice whether function is deprecated or not 
'''

logger = set_logger(None)

def clock(func):
    # can check running time of function
    # you can control the printing option by logging level
    @functools.wraps(func)
    def clocked(*args, **kwargs):
        t0 = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - t0
        name = func.__name__
        arg_lst = []
        if args:
            arg_lst.append(', '.join(repr(arg) for arg in args))
        if kwargs:
            pairs = ['%s=%r' % (k, w) for k, w in sorted(kwargs.items())]
            arg_lst.append(', '.join(pairs))
        arg_str = ', '.join(arg_lst)
        print('[%0.8fs] %s(%s) => %r ' % (elapsed, name, arg_str, result))
        return result

    @functools.wraps(func)
    def no_clocked(*args, **kwargs):
        return func(*args, **kwargs)

    return clocked if DEBUG == logger.level else no_clocked


def write_json(func):
    # write output of API call function as json format
    @functools.wraps(func)
    def _write_json(*args, **kwargs):
        result = func(*args, **kwargs)
        func_name = func.__code__.co_name
        pathname = './output/' + func_name + '.json'
        with open(pathname, 'w') as file:
            json.dump(result.json(), file)

        return result
    return _write_json

def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        logger.warning("Call to deprecated function {}.".format(func.__name__))
        return func(*args, **kwargs)
    return new_func
