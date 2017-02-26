import collections

import utils


# Holds a rating to assess how good a given attempt at finding the target was.
Rating = collections.namedtuple('Rating', [
    'best_worst_removed_percentage',
    'best_code',
    'worst_removed_percentage',
    'actual_removed_percentage'
])


class AI(object):
    """AI for Mastermind using Knuth's minimax algorithm.

    See the description of the algorithm:
    http://www.cs.uni.edu/~wallingf/teaching/cs3530/resources/knuth-mastermind.pdf
    """

    def __init__(self, max_value, num_digits):
        """Initializes the AI."""
        self.max_value = max_value
        self.num_digits = num_digits
        self.ratings = []
        self.current_advice = None
        self.Reset()

    def Reset(self):
        """Cleaner function to reset the AI than calling __init__."""
        # At the beginning, all the codes are possible.
        self.remaining_codes = set(
            utils.GetAllCodes(self.max_value, self.num_digits))

        # Memoization so we don't waste time calling GetAdvice several times.
        self._RefreshCurrentAdvice()

        # Returns the player's performance, and reset the ones of the old game.
        ratings = self.ratings
        self.ratings = []
        return ratings

    def ChangeValueAndDigits(self, max_value, num_digits):
        """Updates to the changes made to the game."""
        self.max_value = max_value
        self.num_digits = num_digits
        self.Reset()

    def GetRemainingPossibilities(self):
        """Returns the sorted list of remaining possibilities."""
        return sorted(self.remaining_codes)

    def GetNbRemainingPossibilities(self):
        """Returns the number of remaining possible codes."""
        return len(self.remaining_codes)

    def _GetWorstCase(self, code):
        """Returns the number of remaining possible codes in the worst case."""
        return max(len(possibilities.intersection(self.remaining_codes))
                   for possibilities in utils.GetPossibilities(
                       self.max_value, self.num_digits, code).values())

    def GetAdvice(self):
        """Returns the best code to try following Knuth's minimax algorithm."""
        # If we already know the value, let's not recompute it.
        if self.current_advice:
            return self.current_advice

        min_max_possibilities = None
        min_codes = []

        # Iterate through all codes to know which one has the best worst case.
        # Note that the best code might have been invalidated through previous
        # tries, so we don't only iterate on the remaining possible codes.
        for code in utils.GetAllCodes(self.max_value, self.num_digits):
            max_possibilities = self._GetWorstCase(code)
            if (min_max_possibilities is None or
                    max_possibilities < min_max_possibilities):
                min_max_possibilities = max_possibilities
                min_codes = [code]
            elif max_possibilities == min_max_possibilities:
                min_codes.append(code)

        # If there is a tie, we select the smallest number not yet invalidated.
        intersection = self.remaining_codes.intersection(min_codes)
        return min(intersection) if intersection else min(min_codes)

    def _RefreshCurrentAdvice(self):
        """Force the refresh on the current advice."""
        self.current_advice = None
        self.current_advice = self.GetAdvice()

    def Update(self, code, black, white):
        """Updates the set of remaining possible codes and the ratings."""
        def RemovedPercentage(nb_new_remaining_possibilities):
            return int(100 * (1 - nb_new_remaining_possibilities / float(
               self.GetNbRemainingPossibilities())))

        best_worst_removed_percentage = RemovedPercentage(
            self._GetWorstCase(self.current_advice))
        worst_removed_percentage = RemovedPercentage(
            self._GetWorstCase(code))

        possibilities_with_last_attempt = utils.GetPossibilities(
            self.max_value, self.num_digits, code)[(black, white)]
        updated_remaining_codes = self.remaining_codes.intersection(
            possibilities_with_last_attempt)

        actual_removed_percentage = RemovedPercentage(
            len(updated_remaining_codes))

        # Actually update internal state.
        self.ratings.append(
            Rating(best_worst_removed_percentage, self.GetAdvice(),
                   worst_removed_percentage, actual_removed_percentage))
        self.remaining_codes = updated_remaining_codes
        self._RefreshCurrentAdvice()
