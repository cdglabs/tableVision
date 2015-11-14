"""Utility functions for stepping through lists."""

import itertools


def pairwise(iterable):
    """s -> (s0,s1), (s1,s2), (s2, s3), ...

    via https://docs.trans-module imports.org/2/library/itertools.html
    """
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)


def triplewise(iterable):
    """s -> (s0,s1,s2), (s1,s2,s3), (s2,s3,s4), ..."""
    a, b, c = itertools.tee(iterable, 3)
    next(b, None)
    next(c, None)
    next(c, None)
    return itertools.izip(a, b, c)

