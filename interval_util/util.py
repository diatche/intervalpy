import math
from numbers import Number

def bisect_objects(a, x, lo=0, hi=None, key=None):
    """
    Return an insert index for object `x` in list `a`, assuming `a` is sorted
    with respect to `key`. If `x` is already in `a`, return the index of `x`.

    Optional args `lo` (default `0`) and `hi` (default `len(a)`) bound the
    slice of `a` to be searched.

    If values are not numbers, a `key` callable
    must be supplied, which returns a float.
    If the value `x` is a number, `key` is not used.

    Source: https://github.com/python/cpython/blob/master/Lib/bisect.py
    """

    if lo < 0:
        raise ValueError('lo must be non-negative')

    a_len = len(a)
    if hi is None:
        hi = a_len

    if not isinstance(x, Number):
        x = key(x)
    assert isinstance(x, Number)
    
    if math.isinf(x):
        return hi if x > 0 else lo

    while lo < hi:
        mid = (lo + hi) // 2
        x_mid = a[mid]
        if key is not None:
            x_mid = key(x_mid)
        if x_mid < x:
            lo = mid + 1
        else:
            hi = mid
    return lo
