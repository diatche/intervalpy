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
from intervalpy import Interval

# Create a set [0, 10), i.e. a set satisfying: >= 0, < 10.
digits = Interval(0, 10, end_open=True)

# Get the set (10, ∞), i.e. a set satisfying: > 10
ten_and_up = digits.get_gt()

# Get the set [0, ∞), i.e. a set satisfying: >= 0
positive_numbers = digits.get_gte()

# Perform set comparison
assert ten_and_up.is_subset_of(positive_numbers)

# Equality is by value
assert positive_numbers.intersection(Interval.lt(10)) == digits
```
