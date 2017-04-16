"""Bot that creates a game of Mastermind."""

import collections
import random

import utils


NUM_TOTAL_POSSIBILITIES_THRESHOLD = 2401


# Returns the result of an attempt.
AttemptResult = collections.namedtuple(
    'AttemptResult',
    ['has_won', 'has_lost', 'black', 'white', 'remaining_tries', 'target'])


class Game(object):
    """Contains a game of Mastermind."""

    def __init__(self, max_value, num_digits, num_tries):
        """Initializes the parameters."""
        self.max_value = max_value
        self.num_digits = num_digits
        self.num_tries = num_tries
        self.Reset()

    def Reset(self):
        """Starts another game."""
        self.remaining_tries = self.num_tries
        self.target = self._GenerateTarget()

    def IsValidAttempt(self, code):
        """Checks if the attempt makes sense with the actual parameters."""
        if len(code) != self.num_digits:
            return False
        for digit in code:
            if int(digit) > self.max_value:
                return False
        return True

    def ChangeValueAndDigits(self, max_value, num_digits):
        """Changes the max_value and num_digits parameters and resets."""
        # Make sure the values make sense.
        if max_value <= 0 or num_digits <= 0:
            return False
        # Limit the size of the solution space.
        # TODO: Re-evaluate if we make the IA or the precomputation optional
        # they're the bottlenecks.
        if max_value ** num_digits > NUM_TOTAL_POSSIBILITIES_THRESHOLD:
            return False
        self.max_value = max_value
        self.num_digits = num_digits
        self.Reset()
        return True

    def ChangeNumTries(self, num_tries):
        """Changes the num_tries parameter and resets."""
        self.num_tries = num_tries
        self.Reset()

    def _GenerateTarget(self):
        """Generates the target code."""
        return random.choice(utils.GetAllCodes(self.max_value, self.num_digits))

    def ProposeCode(self, code):
        """Returns the proximity to target and update the number of tries."""
        # Keep track if the game is finished or not.
        game_over = False
        self.remaining_tries -= 1
        if code == self.target:
            attempt_result = AttemptResult(
                has_won=True, has_lost=False, black=self.num_digits, white=0,
                remaining_tries=self.remaining_tries, target=None)
            game_over = True
        else:
            # The code was incorrect, so we compute and return the proximity.
            black, white = utils.ComputeProximity(
                self.max_value, self.num_digits, self.target, code)
            game_over = not self.remaining_tries
            # Only return the target if the game is over.
            target = self.target if game_over else None
            attempt_result = AttemptResult(
                has_won=False, has_lost=game_over, black=black, white=white,
                remaining_tries=self.remaining_tries, target=target)

        # If the game is over, reset to prepare for the next one.
        if game_over:
            self.Reset()

        return attempt_result
