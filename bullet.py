import pygame

from pygame.sprite import Sprite
# By using sprite from pygame, you can group related elements in your game,
# and act on all the grouped elements at once


class Bullet(Sprite):
    """A class to manage bullets fired from the ship"""

    def __init__(self, ai_game):
        """Create a bullet object at the ship's current position"""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.color = self.settings.bullet_color

        # Create a bullet rect at (0,0) and then set correct position
        # The bullet is created from scratch using Rect(). It is not based on an image
        # we need the the y and x position , the top left corner of the rect,
        # and the width and height  of the rect
        self.rect = pygame.Rect(0, 0, self.settings.bullet_width, self.settings.bullet_height)
        # make the bullet emerge from the top of the ship
        self.rect.midtop = ai_game.ship.rect.midtop
        # Store the bullet's position as a decimal value.
        self.y = float(self.rect.y)

    def update(self):
        """ Move the bullet up the screen"""
        # update the decimal position of the bullet
        self.y -= self.settings.bullet_speed
        # update the rect position
        self.rect.y = self.y

    def draw_bullet(self):
        """ Draw the bullet to the screen"""
        pygame.draw.rect(self.screen, self.color, self.rect)
        # draw.rect() function fill the part of the screen defined by the bullet



