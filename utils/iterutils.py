from functools import partial
from itertools  import islice

def take(n, iterable):
    return list(islice(iterable, n))

def chunks(iterable, n):
    iterator = iter(partial(take, n, iter(iterable)), [])
    return iterator