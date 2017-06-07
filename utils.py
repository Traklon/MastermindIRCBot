"""Utils for the game of Mastermind."""

import collections
import functools
import itertools


@functools.lru_cache(maxsize=2401)  # Up to 7^4 values.
def _GetCount(max_value, num_digits, code):
    """Returns the count of each character from the code.

    For example, _GetCount(6, 4, '1231') returns [2, 1, 1, 0, 0, 0].
    """
    count = [0] * max_value
    for digit in code:
        count[int(digit) - 1] += 1
    return count


def ComputeProximity(max_value, num_digits, code_1, code_2):
    """Returns the proximity in terms of black and white pegs between two codes.

    For example, ComputeProximity(6, 4, '1123', '1233') returns (2, 1).
    This is because the first and last digits match, and because the position
    of the '2' differs.

    Note that there is not another white peg for the '3' in 3rd position of the
    second code because the only '3' of the first code is already matched at the
    correct position.

    The rules of Mastermind are surprisingly hard to explain!
    """
    black = len([1 for d1, d2 in zip(code_1, code_2) if d1 == d2])
    count_code_1 = _GetCount(max_value, num_digits, code_1)
    count_code_2 = _GetCount(max_value, num_digits, code_2)
    black_and_white = sum(
        min(c1, c2) for c1, c2 in zip(count_code_1, count_code_2))
    return black, black_and_white - black


@functools.lru_cache()
def GetAllCodes(max_value, num_digits):
    """Returns all possible codes for a given max_value and num_digits.

    The length of the returned list is max_value ** num_digits.
    """
    all_codes = itertools.product(range(1, max_value + 1), repeat=num_digits)
    return [''.join(str(digit) for digit in digits) for digits in all_codes]


@functools.lru_cache(maxsize=1)
def _GetPossibilitiesDict(max_value, num_digits):
    """Returns a dict matching a code and a proximity to all the matching codes.

    The matching is possibilities[code][(black, white)] = set(matching_codes).

    For example, with max_value = 2 and num_digits = 3:
        possibilities['111'][(2,0)] == set('112', '121', '211')

    This dict is used in several time-constraned routines, thus we memoize it.
    """
    possibilities = collections.defaultdict(
        lambda: collections.defaultdict(set))
    for code_1, code_2 in itertools.product(
          GetAllCodes(max_value, num_digits), repeat=2):
        if code_1 < code_2:
            proximity = ComputeProximity(max_value, num_digits, code_1, code_2)
            possibilities[code_1][proximity].add(code_2)
            possibilities[code_2][proximity].add(code_1)
    return possibilities


def GetPossibilities(max_value, num_digits, code):
    """Query the possibilities dict for given parameters and a given code."""
    return _GetPossibilitiesDict(max_value, num_digits)[code]
