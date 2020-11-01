import math
import warnings
from numbers import Number
from collections.abc import Sequence
from .util import *


class Interval(Sequence):
    """
    Specifies an open, closed or mixed interval.
    """

    inf = math.inf

    @property
    def is_empty(self):
        return self.end == self.start and (self.end_open or self.start_open)

    @property
    def length(self):
        if self.is_empty:
            return 0.0
        return self.end - self.start

    @property
    def middle(self):
        return (self.end + self.start) / 2

    @property
    def is_negative_infinite(self):
        return self.start != self.end and math.isinf(self.start)

    @property
    def is_positive_infinite(self):
        return self.start != self.end and math.isinf(self.end)

    @property
    def is_infinite(self):
        return self.is_negative_infinite and self.is_positive_infinite

    @property
    def is_finite(self):
        return not self.is_negative_infinite and not self.is_positive_infinite

    @property
    def is_point(self):
        return not self.is_empty and self.start == self.end

    def __init__(self, start, end, start_open=False, end_open=False):
        if start is None and end is not None:
            start = -math.inf
        if end is None and start is not None:
            end = math.inf

        self.start = 0
        self.end = 0
        self.start_open = start_open
        self.end_open = end_open

        if end == start and (end_open or start_open):
            # Empty interval
            start = None
            end = None
        else:
            assert isinstance(self.start, Number)
            assert isinstance(self.end, Number)
            assert self.end >= self.start

        self.start = start
        self.end = end

        if self.start != self.end:
            if self.is_negative_infinite:
                self.start_open = True
            if self.is_positive_infinite:
                self.end_open = True

    def __bool__(self):
        return not self.is_empty

    def __len__(self):
        return 2 if not self.is_empty else 0

    def __getitem__(self, i):
        return self.start if i == 0 else self.end

    def __iter__(self):
        if self.is_empty:
            return iter([])
        return iter([self.start, self.end])

    def as_closed(self):
        if self.is_empty:
            return self
        return Interval(self.start, self.end, start_open=False, end_open=False)

    def as_open(self):
        if self.is_empty:
            return self
        return Interval(self.start, self.end, start_open=True, end_open=True)

    def as_closed_open(self):
        if self.is_empty:
            return self
        return Interval(self.start, self.end, start_open=False, end_open=True)

    def as_open_closed(self):
        if self.is_empty:
            return self
        return Interval(self.start, self.end, start_open=True, end_open=False)

    def map(self, f):
        return Interval(f(self.start), f(self.end), start_open=self.start_open, end_open=self.end_open)

    def round(self, method=round):
        if self.is_empty:
            return self
        start = method(self.start) if not self.is_negative_infinite else self.start
        end = method(self.end) if not self.is_positive_infinite else self.end
        return Interval(start, end, start_open=self.start_open, end_open=self.end_open)

    def contains(self, x, enforce_start=True, enforce_end=True):
        if x is None or self.is_empty:
            return False

        # Special infinite cases
        if self.is_negative_infinite and x == -math.inf:
            return True
        if self.is_positive_infinite and x == math.inf:
            return True

        if enforce_start:
            if x < self.start:
                return False
            elif self.start_open and x == self.start:
                return False
        if enforce_end:
            if x > self.end:
                return False
            elif self.start_open and x == self.start:
                return False
            elif self.end_open and x == self.end:
                return False
        return True

    def index_range(self, values, key=None):
        """
        Returns index range of values inside the interval
        as a tuple `(start index, end index)`, where
        the end index is exclusive.

        If no values are inside the interval, (0, 0)
        is returned.

        If values are not numbers, a `key` callable
        must be supplied, which returns a float.

        Assumes `values` are sorted.
        """
        if self.is_empty:
            return 0, 0
        values_len = len(values)
        if values_len == 0 or self.is_infinite:
            return 0, values_len

        i0 = max(0, bisect_objects(values, self.start, key=key) - 1)
        i1 = min(values_len, bisect_objects(values, self.end, key=key) + 1)

        if key is None:
            def key(x): return x

        while i0 != i1:
            x = key(values[i0])
            if x < self.start and not self.contains(x):
                i0 += 1
            else:
                break
        while i1 != 0 and i0 != i1:
            x = key(values[i1 - 1])
            if x > self.end and not self.contains(x):
                i1 -= 1
            else:
                break

        return i0, i1

    def filter(self, values, key=None):
        """
        Returns values inside the interval.

        If values are not numbers, a `key` callable
        must be supplied, which returns a float.

        Assumes `values` are sorted.
        """
        i0, i1 = self.index_range(values, key=key)
        return values[i0:i1]

    def is_superset_of(self, interval):
        if self.is_empty:
            return False

        u = self
        v = Interval.parse(interval)

        if v.is_empty:
            return True

        u0 = u.start
        u1 = u.end
        v0 = v.start
        v1 = v.end

        if u0 > v0:
            return False
        elif u0 == v0 and u.start_open and not v.start_open:
            return False

        if u1 < v1:
            return False
        elif u1 == v1 and u.end_open and not v.end_open:
            return False

        return True

    def is_subset_of(self, interval):
        return Interval.parse(interval).is_superset_of(self)

    def equals(self, interval):
        if interval is None:
            return False
        interval = Interval.parse(interval)
        if self.is_empty and interval.is_empty:
            return True
        return self.start == interval.start and self.end == interval.end and self.start_open == interval.start_open and self.end_open == interval.end_open

    def partition(self, xs, start_open=None, end_open=None):
        """
        `xs` are assumed to be in ascending order.
        """
        xs = list(filter(lambda x: self.contains(x), xs))
        len_xs = len(xs)
        if len_xs == 0:
            return [self]
        intervals = []
        i_last = len_xs - 1
        x_prev = None
        if end_open is not None:
            start_open = not end_open
        elif start_open is not None:
            end_open = not start_open
        else:
            start_open = False
            end_open = True
        for i in range(len_xs + 1):
            if i <= i_last:
                x = xs[i]
            if i == 0:
                d_start = self.start
                d_start_open = self.start_open
            else:
                d_start = x_prev
                d_start_open = start_open
            if i == len_xs:
                d_end = self.end
                d_end_open = self.end_open
            else:
                d_end = x
                d_end_open = end_open
            d = Interval(d_start, d_end, start_open=d_start_open,
                       end_open=d_end_open)
            if not d.is_empty:
                intervals.append(d)
            x_prev = x
        return intervals

    def copy(self):
        return Interval(self.start, self.end, start_open=self.start_open, end_open=self.end_open)

    def offset(self, offset):
        return Interval(self.start + offset, self.end + offset, start_open=self.start_open, end_open=self.end_open)
        
    def get_gte(self):
        """
        Return a interval from the start of this interval to positive infinity.
        If this interval is empty, return an empty interval.
        """
        if self.is_empty:
            return empty
        return Interval(self.start, math.inf, start_open=self.start_open, end_open=False)

    def get_lte(self):
        """
        Return a interval from the negative infinity to the end of this interval.
        If this interval is empty, return an empty interval.
        """
        if self.is_empty:
            return empty
        return Interval(-math.inf, self.end, start_open=False, end_open=self.end_open)

    def get_gt(self):
        """
        Return a interval from the end of this interval (non-inclusive) to positive infinity.
        If this interval is empty, return an empty interval.
        """
        if self.is_empty:
            return empty
        return Interval(self.end, math.inf, start_open=not self.end_open, end_open=False)

    def get_lt(self):
        """
        Return a interval from negative infinity to the start of this interval (non-inclusive).
        If this interval is empty, return an empty interval.
        """
        if self.is_empty:
            return empty
        return Interval(-math.inf, self.start, start_open=False, end_open=not self.start_open)
        
    def extended_to_positive_infinity(self):
        """
        Return a interval from the start of this interval to positive infinity.
        If this interval is empty, return an empty interval.

        *Deprecated, use get_gte() instead.*
        """
        warnings.warn('extended_to_positive_infinity() is deprecated, use get_gte() instead', DeprecationWarning)
        return self.get_gte()

    def extended_to_negative_infinity(self):
        """
        Return a interval from the negative infinity to the end of this interval.
        If this interval is empty, return an empty interval.

        *Deprecated, use get_lte() instead.*
        """
        warnings.warn('extended_to_negative_infinity() is deprecated, use get_lte() instead', DeprecationWarning)
        return self.get_lte()

    def rest_to_positive_infinity(self):
        """
        Return a interval from the end of this interval (non-inclusive) to positive infinity.
        If this interval is empty, return an empty interval.

        *Deprecated, use get_gt() instead.*
        """
        warnings.warn('rest_to_positive_infinity() is deprecated, use get_gt() instead', DeprecationWarning)
        return self.get_gt()

    def rest_to_negative_infinity(self):
        """
        Return a interval from negative infinity to the start of this interval (non-inclusive).
        If this interval is empty, return an empty interval.

        *Deprecated, use get_lt() instead.*
        """
        warnings.warn('rest_to_negative_infinity() is deprecated, use get_lt() instead', DeprecationWarning)
        return self.get_lt()

    def to_str(self, transformer=None, infinity_str=None, empty_str=None):
        if self.is_empty:
            return empty_str or '()'

        start_str = '(' if self.start_open else '['
        end_str = ')' if self.end_open else ']'

        start = self.start
        end = self.end

        if start == end:
            x = start
            if callable(transformer):
                x = transformer(x)
            return '{}{}{}'.format(start_str, x, end_str)

        if self.is_negative_infinite:
            start = '-' + (infinity_str or 'inf')
        elif callable(transformer):
            start = transformer(start)

        if self.is_positive_infinite:
            end = infinity_str or 'inf'
        elif callable(transformer):
            end = transformer(end)

        return '{}{}, {}{}'.format(start_str, start, end, end_str)

    def pad(self, *amount, start=None, end=None):
        default = amount[0] if len(amount) != 0 else None

        if self.is_negative_infinite:
            start = self.start
        else:
            start = self.start - (start or default or 0)

        if self.is_positive_infinite:
            end = self.end
        else:
            end = self.end + (end or default or 0)

        return Interval(start, end, start_open=self.start_open, end_open=self.end_open)

    @staticmethod
    def parse(d, default_inf=False):
        if d is None:
            if default_inf:
                return infinite
            else:
                raise Exception(f'Unable to parse interval: {d}')
        if type(d) == Interval or isinstance(d, Interval):
            return d
        elif isinstance(d, Number):
            return Interval.point(d)
        elif not bool(d):
            return empty
        elif isinstance(d, Sequence) and not isinstance(d, (str, bytes)):
            if len(d) == 2:
                return Interval(d[0], d[1])

        # TODO: parse interval strings such as: `[0, 4.5)`, `[0, +inf)`
        raise Exception(f'Unable to parse interval: {d}')

    @staticmethod
    def parse_many(ds):
        if type(ds) == Interval or isinstance(ds, Interval):
            return [ds]
        return list(map(Interval.parse, ds))

    @staticmethod
    def empty():
        return empty

    @staticmethod
    def infinite():
        return infinite

    @staticmethod
    def gt(x):
        return Interval(x, math.inf, start_open=True, end_open=True)

    @staticmethod
    def gte(x):
        return Interval(x, math.inf, start_open=False, end_open=True)

    @staticmethod
    def lt(x):
        return Interval(-math.inf, x, start_open=True, end_open=True)

    @staticmethod
    def lte(x):
        return Interval(-math.inf, x, start_open=True, end_open=False)

    @staticmethod
    def positive_infinite(x, open=False):
        """
        *Deprecated, use gt() or gte() instead.*
        """
        warnings.warn('positive_infinite() is deprecated, use gt() or gte() instead', DeprecationWarning)
        return Interval(x, math.inf, start_open=open, end_open=True)

    @staticmethod
    def negative_infinite(x, open=False):
        """
        *Deprecated, use t() or lte() instead.*
        """
        warnings.warn('negative_infinite() is deprecated, use lt() or lte() instead', DeprecationWarning)
        return Interval(-math.inf, x, start_open=True, end_open=open)

    @staticmethod
    def point(x):
        return Interval(x, x, start_open=False, end_open=False)

    @staticmethod
    def closed(start, end):
        return Interval(start, end, start_open=False, end_open=False)

    @staticmethod
    def open(start, end):
        return Interval(start, end, start_open=True, end_open=True)

    @staticmethod
    def closed_open(start, end):
        return Interval(start, end, start_open=False, end_open=True)

    @staticmethod
    def open_closed(start, end):
        return Interval(start, end, start_open=True, end_open=False)

    @staticmethod
    def union(intervals):
        intervals = Interval.parse_many(intervals)
        intervals = list(filter(lambda d: not d.is_empty, intervals))
        d_len = len(intervals)
        if d_len == 0:
            return empty
        elif d_len == 1:
            return intervals[0]
        start = min(intervals, key=lambda d: d.start).start
        end = max(intervals, key=lambda d: d.end).end
        # open if none are open
        start_open = not any(map(lambda d: not d.start_open, filter(
            lambda d: d.start == start, intervals)))
        end_open = not any(map(lambda d: not d.end_open,
                               filter(lambda d: d.end == end, intervals)))
        return Interval(start, end, start_open=start_open, end_open=end_open)

    @staticmethod
    def intersection(intervals):
        intervals = Interval.parse_many(intervals)
        for d in intervals:
            if d.is_empty:
                # intersection of any set with an empty set is an empty set
                return empty
        d_len = len(intervals)
        if d_len == 0:
            return empty
        elif d_len == 1:
            return intervals[0]
        start = max(intervals, key=lambda d: d.start).start
        end = min(intervals, key=lambda d: d.end).end
        if start > end:
            return empty
        # open if any is open
        start_open = any(map(lambda d: d.start_open, filter(
            lambda d: d.start == start, intervals)))
        end_open = any(map(lambda d: d.end_open, filter(
            lambda d: d.end == end, intervals)))
        return Interval(start, end, start_open=start_open, end_open=end_open)

    def intersects(self, interval):
        if self.is_empty:
            return False

        u = self
        v = Interval.parse(interval)

        if v.is_empty:
            return False

        u0 = u.start
        u1 = u.end
        v0 = v.start
        v1 = v.end

        if u0 <= v0:
            if u1 < v0:
                return False
            elif u1 == v0:
                return not u.end_open and not v.start_open
            else:
                return True

        if u0 >= v0:
            if v1 < u0:
                return False
            elif v1 == u0:
                return not v.end_open and not u.start_open
            else:
                return True

    def __repr__(self):
        try:
            return self.to_str()
        except Exception as e:
            return super().__repr__() + f'({e})'

    def __radd__(self, other):
        # sum() starts with 0 and then adds the first itme in the list to that.
        # So if the first item doesn’t know how to add itself to 0, Python fails.
        # But before it fails, Python tries to do a reversed add with the operators.
        return Interval.union([self, other])

    def __add__(self, other):
        return Interval.union([self, other])

    def __lt__(self, other):
        if self.is_empty:
            return False
        other = Interval.parse(other)
        if other.is_empty:
            return True
        if self.end < other.start:
            return True
        elif self.end == other.start and (self.end_open or other.start_open):
            return True
        return False

    def __le__(self, other):
        if self.is_empty:
            return False
        other = Interval.parse(other)
        if other.is_empty:
            return True
        if self.end < other.end:
            return True
        elif self.end == other.end and not (not self.end_open and other.end_open):
            return True
        return False

    def __eq__(self, other):
        return self.equals(other)

    def __ne__(self, other):
        return not self.equals(other)

    def __gt__(self, other):
        if self.is_empty:
            return False
        other = Interval.parse(other)
        if other.is_empty:
            return True
        if self.start > other.end:
            return True
        elif self.end == other.start and (self.start_open or other.end_open):
            return True
        return False

    def __ge__(self, other):
        if self.is_empty:
            return False
        other = Interval.parse(other)
        if other.is_empty:
            return True
        if self.start > other.start:
            return True
        elif self.start == other.start and not (not self.start_open and other.start_open):
            return True
        return False

    def __and__(self, other):
        return Interval.intersection([self, other])

    def __or__(self, other):
        return Interval.union([self, other])


empty = Interval(0, 0, start_open=True, end_open=True)
infinite = Interval(-math.inf, math.inf, start_open=True, end_open=True)
