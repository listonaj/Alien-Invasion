class GameStats:
    """ Track statistics for Alien Invasion."""

    def __init__(self, ai_game):
        """ Initialize statistics."""
        self.settings = ai_game.settings
        self.reset_stats()
        # start Alien Invasion in an inactive state
        # the game never end, so we add an inactive state
        # no way for the player to start without a play button
        self.game_active = False
        # High score should never be reset.
        self.high_score = 0

    def reset_stats(self):
        """ Initialize statistics that can change during the game."""
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1

