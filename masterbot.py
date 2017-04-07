# -*- coding:utf-8 -*-

import re

import mastermind
import ai

MAX_PRINT_POSSIBILITIES = 75

HELP_FREE_GAME = ("Veuillez entrer soit 'poss' ou 'nbposs' pour connaitre les "
                  "possibilités restantes, soit 'indice' pour connaitre le "
                  "meilleur coup possible, soit <code> pour proposer une "
                  "réponse, soit 'reset' pour revenir à zéro, soit 'stats' ou "
                  "'nostats' pour activer ou désactiver l'affichage des stats "
                  "en fin de partie.")

WELCOME = 'Bonjour !'

DEFAULT_MAX_VALUE = 7
DEFAULT_NUM_DIGITS = 4
DEFAULT_NUM_TRIES = 6


class MasterBot(object):
    """Gamemaster to play Mastermind on IRC."""

    def __init__(self):
        """Initializes the instances of the game and the AI."""
        self.game = mastermind.Game(
            max_value=DEFAULT_MAX_VALUE, num_digits=DEFAULT_NUM_DIGITS,
            num_tries=DEFAULT_NUM_TRIES)
        self.bot = ai.AI(
            max_value=DEFAULT_MAX_VALUE, num_digits=DEFAULT_NUM_DIGITS)
        self.enable_rating = True

    # Functions that get called on events thanks to the IRCBot instance to which
    # we are subscribed to.

    def on_join(self, irc):
        """Greets newcomers."""
        irc.SendMessage(WELCOME)
        irc.SendMessage(HELP_FREE_GAME)

    def on_pubmsg(self, irc):
        """Called when a new public message is posted."""
        self._ParseInputAndUpdate(irc)

    def _SwitchMaxValueAndNumDigits(self, irc, message):
        """Updates the game instance and the AI with new parameters."""
        try:
            _, max_value_str, num_digits_str = message.split(' ')
            max_value = int(max_value_str)
            num_digits = int(num_digits_str)
            if self.game.ChangeValueAndDigits(max_value, num_digits):
                self.bot.ChangeValueAndDigits(max_value, num_digits)
                irc.SendMessage('Partie annulée et variables changées !')
            else:
                irc.SendMessage('Trop de possibilités ou variables erronées !')
        except:
            irc.SendMessage('Parse Error :(')
            pass

    def _SwitchNumTries(self, irc, message):
        """Updates the game instance with the requested number of tries."""
        try:
            _, num_tries_str = message.split(' ')
            num_tries = int(num_tries_str)
            self.game.ChangeNumTries(num_tries)
            self.bot.Reset()
            irc.SendMessage("Partie annulée et nombre d'essais changés!")
        except:
            irc.SendMessage('Parse Error :(')
            pass

    def _PrintRemainingPossibilities(self, irc):
        """Displays the remaining possible codes, summarizing if needed."""
        possibilities_str = ' '.join(
            self.bot.GetRemainingPossibilities()[:MAX_PRINT_POSSIBILITIES])
        if self.bot.GetNbRemainingPossibilities() > MAX_PRINT_POSSIBILITIES:
            irc.SendMessage(
                'Il reste {} possibilités. Voici les {} premières: {}'.format(
                    self.bot.GetNbRemainingPossibilities(),
                    MAX_PRINT_POSSIBILITIES, possibilities_str))
        else:
            irc.SendMessage(
                'Il reste {} possibilité(s): {}'.format(
                    self.bot.GetNbRemainingPossibilities(), possibilities_str))

    def _Attempt(self, irc, code):
        """Sends an attempt to the game, displaying info if the game ends."""
        attempt = self.game.ProposeCode(code)
        self.bot.Update(code, attempt.black, attempt.white)
        ratings = None
        if attempt.has_won:
            irc.SendMessage('Tu as gagné ! Il te restait {} essai(s).'.format(
                attempt.remaining_tries))
            ratings = self.bot.Reset()
        else:
            irc.SendMessage('Noirs: {} Blancs: {} Essais restants: {}'.format(
                attempt.black, attempt.white, attempt.remaining_tries))
            if attempt.has_lost:
                irc.SendMessage(
                    'Tu as perdu... Le code était: {}'. format(attempt.target))
                ratings = self.bot.Reset()
        if self.enable_rating and ratings:
            for rating in ratings:
                irc.SendMessage(
                    'Meilleur pire cas: {}% ({}), Pire cas: {}%, '
                    'Supprimées: {}%'.format(
                        rating.best_worst_removed_percentage,
                        rating.best_code,
                        rating.worst_removed_percentage,
                        rating.actual_removed_percentage))

    def _ParseInputAndUpdate(self, irc):
        """Switch-type function to know what to do depending on the message."""
        message = irc.GetMessage()
        if message.startswith('param'):
            self._SwitchMaxValueAndNumDigits(irc, message)
        elif message.startswith('essais'):
            self._SwitchNumTries(irc, message)
        elif message == 'reset':
            self.game.Reset()
            self.bot.Reset()
            irc.SendMessage('Partie annulée!')
        elif message == 'stats':
            self.enable_rating = True
            irc.SendMessage('Vous pourrez voir vos stats en fin de partie!')
        elif message == 'nostats':
            self.enable_rating = False
            irc.SendMessage(
                'Vos stats ne seront plus montrées en fin de partie!')
        elif message == 'nbposs':
            irc.SendMessage('Il reste {} possibilité(s).'.format(
                            self.bot.GetNbRemainingPossibilities()))
        elif message == 'poss':
            self._PrintRemainingPossibilities(irc)
        elif message == 'indice':
            irc.SendMessage('Meilleur coup: ' + self.bot.GetAdvice())
        elif message == 'aide':
            irc.SendMessage(HELP_FREE_GAME)
        elif (re.match(r'^[1-9]+$', message) and
              self.game.IsValidAttempt(message)):
            self._Attempt(irc, message)
