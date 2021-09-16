import sys
from time import sleep
import pygame

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien


# contains the functionality to make the game
class AlienInvasion:
    """ Overall class to manage game assets and behavior."""

    def __init__(self):
        """Initialize the game, and create game resources"""
        pygame.init()
        # Initialize the background setting that Pygame
        # needs to run properly
        self.settings = Settings()

        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        # Creates a display window, with the tuple that define the dimensions.
        # We attribute the display to self screen so it can be available in all methods in the class
        # It returns the entire game window
        pygame.display.set_caption("Alien Invasion")

        # Create an instance to store game statistics,
        # and create a scoreboard
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        # we create a group of bullets in alien invasion to store
        # all live bullets shouted when the user press space bar
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        # Make the play button with label 'START'
        self.play_button = Button(self, "START")

    def _create_fleet(self):
        """Create the fleet of aliens"""
        # Make an alien, we create one instance of alien, and we add it to the group,
        # also find the number of aliens per row
        alien = Alien(self)
        # The first alien created is not part of the fleet but help to place
        # the other aliens once created to know its width and height
        alien_width, alien_height = alien.rect.size
        # We have two margin: the available space is then
        # the screen width minus two alien width
        available_space_x = self.settings.screen_width - (2 * alien_width)
        # spacing between two aliens
        number_aliens_x = available_space_x // (2 * alien_width)
        # Determine the number of rows of aliens that fit on the screen
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)

        for row_number in range(number_rows):
            # Create the first row of aliens.
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        # Create an alien and place it in the row
        # easier to put it in a method to add new rows after
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien_height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _check_alien_bottom(self):
        """Check if any aliens have reached the bottom of the screen"""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Treat this the same way as the ship got hit
                self._ship_hit()
                break

    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _update_aliens(self):
        """Check if the fleet is at an edge
        Update the positions of aliens in the fleet"""
        self._check_fleet_edges()
        self.aliens.update()

        # Look for alien-ship collisions
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
        # look for aliens hitting the bottom of the screen
        self._check_alien_bottom()

    def run_game(self):
        # the game is controlled here
        """Start the main loop for the game."""
        while True:
            self._check_events()

            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()

            self._update_screen()

    def _check_events(self):
        # loops continually
        # Watch for keyboard and mouse events
        """respond to keypress and mouse events"""
        for event in pygame.event.get():
            # Event is an action that the player does while playing
            # such as pressing a key or moving the mouse
            if event.type == pygame.QUIT:
                sys.exit()
            # MOUSEBUTTONDOWN -> if the player click anywhere on the screen
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # to restrict the event when click on the button
                # the function get pos return the position x and y
                # of the mouse click.
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
            # Pressing a key -> KEYDOWN event
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)

            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)

    def _check_play_button(self, mouse_pos):
        """Start a new game when the player click play"""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            # Reset the game settings
            self.settings.initialize_dynamic_settings()
            # Reset the game statistics.
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            # Get rid of any remaining aliens and bullets.
            self.aliens.empty()
            self.bullets.empty()
            # Create a new fleet and center the ship
            self._create_fleet()
            self.ship.center_ship()
            # Hide the mouse cursor when the game start
            pygame.mouse.set_visible(False)

    def _check_keydown_events(self, event):
        # What key is pressed ? right arrow
        if event.key == pygame.K_RIGHT:
            # Move the ship to the right one pixel at a time  - on the x axis
            # see the ship class that set the ship in motion if true (update method)
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        # event to quit the game when you press 'esc'
        elif event.key == pygame.K_ESCAPE:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group"""
        # Limit the player to shoot three bullets at a time to encourage
        # accuracy at shooting :)
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        """update position of the bullets and get rid of the old bullets."""
        # update bullet position
        self.bullets.update()

        # Get rid of the bullets that have disappeared.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        print(len(self.bullets))
        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        # Check for any bullets that have hit aliens
        # if bullets and aliens collide in place:  True,True tells
        # python to erase the aliens and bullet that collide
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)

        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
                self.sb.prep_score()
                self.sb.check_high_score()

        if not self.aliens:
            # if the alien group is empty (group = False)
            # Destroy existing bullets and create new fleet
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            # Increase level.
            self.stats.level += 1
            self.sb.prep_level()

    def _ship_hit(self):
        """ Respond to the ship being hit by an alien"""
        if self.stats.ships_left > 0:
            # Decrement ships_left, and update scoreboard.
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            # Get rid of any remaining aliens and bullets
            self.aliens.empty()
            self.bullets.empty()
            # Create a new fleet and center the ship
            self._create_fleet()
            self.ship.center_ship()
            # Pause.
            sleep(0.5)
        else:
            self.stats.game_active = False
            # Makes the mouse's cursor reappear when the ship is hit
            pygame.mouse.set_visible(True)

    def _update_screen(self):
        """Update images on the screen, and flip to the new screen"""
        # redraw the screen during each pass through the loop,
        # and fill the screen with the color defined
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        # Make the most recently drawn screen visible.
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()

        self.aliens.draw(self.screen)

        # Draw the score information
        self.sb.show_score()

        # Draw the play button if the game is active
        if not self.stats.game_active:
            self.play_button.draw_button()

        pygame.display.flip()
        # The call make the more recent drawn screen visible,
        # in this case an empty screen. when we move in the game along
        # the most recent screen hide the old one


if __name__ == '__main__':
    # Make a game instance, run the game
    ai = AlienInvasion()
    ai.run_game()
