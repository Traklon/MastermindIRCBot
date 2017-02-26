import collections
import random

import utils


NUM_TOTAL_POSSIBILITIES_THRESHOLD = 2401


# Returns the result of an attempt.
AttemptResult = collections.namedtuple(
    'AttemptResult', ['has_won', 'has_lost', 'black', 'white', 'target'])


class Game(object):
    """Contains a game of Mastermind."""

    def __init__(self, max_value, num_digits, num_tries):
        """Initializes the parameters."""
        self.max_value = max_value
        self.num_digits = num_digits
        self.num_tries = num_tries
        self.Reset()

    def Reset(self):
        """Cleaner function to start the game than calling __init__."""
        self.remaining_tries = self.num_tries
        self.target = self._GenerateTarget()

    def GetNbRemainingTries(self):
        """Returns the numbers of remaining tries."""
        return self.remaining_tries

    def ChangeValueAndDigits(self, max_value, num_digits):
        """Changes the max_value and num_digits parameters and resets."""
        # Limit the size of the solution space.
        # TODO: Re-evaluate if we make IA or the precomputation optional because
        # it's the bottleneck.
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
        if code == self.target:
            self.Reset()
            return AttemptResult(
                has_won=True, has_lost=False, black=self.num_digits, white=0,
                target=None)

        # The code was incorrect, so we compute and return the proximity.
        black, white = utils.ComputeProximity(
            self.max_value, self.num_digits, self.target, code)
        self.remaining_tries -= 1
        has_lost = not bool(self.remaining_tries)
        target = None
        if has_lost:
            # Only return the target if the game is over.
            target = self.target
            self.Reset()
        return AttemptResult(
            has_won=False, has_lost=has_lost, black=black, white=white,
            target=target)
