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

# Development

## Updating Documentation

The module [pdoc3](https://pdoc3.github.io/pdoc/) is used to automatically generate documentation. To update the documentation:

1. Install `pdoc3` if needed with `pip3 install pdoc3`.
2. Navigate to project root and install dependencies: `poetry install`.
3. Generate documetation files with: `pdoc3 -o docs --html durationpy`.
4. The new files will be in `docs/durationpy`. Move them to `docs/` and replace existing files.
