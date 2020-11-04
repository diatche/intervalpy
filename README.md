# intervalpy

![Tests](https://github.com/diatche/intervalpy/workflows/Tests/badge.svg)

An interval set utility library.

# Installation

With [poetry](https://python-poetry.org):

```bash
poetry add intervalpy
```

Or with pip:

```
pip3 install intervalpy
```

# Usage

Have a look at the [documentation](https://diatche.github.io/intervalpy/).

Basic usage:

```python
from interval_util import Interval

digits = Interval(0, 10, end_open=True)
ten_and_up = digits.get_gt()
positive_numbers = digits.get_gte()
assert ten_and_up.is_subset_of(positive_numbers)

assert positive_numbers.intersection(Interval.lt(10)) == digits
```
