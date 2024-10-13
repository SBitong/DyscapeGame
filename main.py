import pygame
import sys
import os
import random
import pyttsx3
from settings import *
import time

# Initialize Pygame
pygame.init()
engine = pyttsx3.init()


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("DyscapeTheGame")

        self.gameStateManager = GameStateManager('main-menu')
        self.mainMenu = MainMenu(self.screen, self.gameStateManager)
        self.lavaLabyrinth = LavaLabyrinth(self.screen, self.gameStateManager)  # Add LavaLabyrinth level here
        self.states = {
            'main-menu': self.mainMenu,
            'lava-labyrinth': self.lavaLabyrinth  # New LavaLabyrinth state
        }

        self.clock = pygame.time.Clock()

    def run(self):
        while True:
            # Event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Run the current state
            self.states[self.gameStateManager.get_state()].run()

            # Update the display
            pygame.display.update()

            # Cap the frame rate
            self.clock.tick(FPS)


class MainMenu:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager

        # Load the Arial font
        font_path = os.path.join('fonts', 'ARIAL.TTF')
        self.font = pygame.font.Font(font_path, 40)

        # Load hover sound effect
        hover_sound_path = os.path.join('audio',
                                        'mouse_hover_effect_01.mp3')  # Replace with the path to your hover sound
        self.hover_sound = pygame.mixer.Sound(hover_sound_path)
        self.start_button_hovered = False
        self.option_button_hovered = False
        self.exit_button_hovered = False
        self.second_level_button_hovered = False  # For the Lava Labyrinth level

        # Load the game music
        music_path = os.path.join('audio', '01 Hei Shao.mp3')
        self.main_menu_bgm = pygame.mixer.Sound(music_path)
        self.main_menu_bgm_isplaying = False

        # Load ambient nature sound
        ambient_path = os.path.join('audio', 'bird_chirping.mp3')  # Ensure the correct path
        self.ambient_sound = pygame.mixer.Sound(ambient_path)
        self.ambient_sound_isplaying = False

        # Load the main-menu background and adjust to fit on display
        background_image_path = os.path.join('graphics', 'main-menu-background-1.jpg')
        self.background_image = pygame.image.load(background_image_path).convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image,
                                                       (self.display.get_width(), self.display.get_height()))

        # Load the game logo
        game_logo_path = os.path.join('graphics', 'DYSCAPE-LOGO2.png')
        self.game_logo = pygame.image.load(game_logo_path).convert_alpha()
        self.logo_width, self.logo_height = self.game_logo.get_size()

        # Start Button properties
        self.startbutton_color = (255, 200, 0)
        self.startbutton_hover_color = (255, 170, 0)
        self.startbutton_text = "Start"
        self.startbutton_rect = pygame.Rect((self.display.get_width() // 2 - 150, 400), (300, 80))

        # Lava Labyrinth Button properties
        self.lava_button_color = (255, 200, 0)
        self.lava_button_hover_color = (255, 170, 0)
        self.lava_button_text = "Lava Labyrinth"
        self.lava_button_rect = pygame.Rect((self.display.get_width() // 2 - 150, 500), (300, 80))

        # Exit Button properties
        self.exitbutton_color = (255, 200, 0)
        self.exitbutton_hover_color = (255, 170, 0)
        self.exitbutton_text = "Exit Game"
        self.exitbutton_rect = pygame.Rect(((self.display.get_width() // 2) - (250 // 2), 600), (250, 70))

    def stop_sounds(self):
        self.main_menu_bgm.stop()
        self.ambient_sound.stop()
        self.main_menu_bgm_isplaying = False
        self.ambient_sound_isplaying = False

    def run(self):
        if not self.main_menu_bgm_isplaying:
            self.main_menu_bgm.play(-1)
            self.main_menu_bgm_isplaying = True

        if not self.ambient_sound_isplaying:
            self.ambient_sound.play(-1)
            self.ambient_sound_isplaying = True

        self.display.blit(self.background_image, (0, 0))
        self.display.blit(self.game_logo, ((WIDTH // 2) - (self.logo_width // 2), 90))

        mouse_pos = pygame.mouse.get_pos()

        # Start Button hover and click logic
        if self.startbutton_rect.collidepoint(mouse_pos):
            start_button_color = self.startbutton_hover_color
        else:
            start_button_color = self.startbutton_color

        self.draw_button(self.startbutton_text, self.font, self.startbutton_rect, start_button_color)

        # Lava Labyrinth Button hover and click logic
        if self.lava_button_rect.collidepoint(mouse_pos):
            lava_button_color = self.lava_button_hover_color
        else:
            lava_button_color = self.lava_button_color

        self.draw_button(self.lava_button_text, self.font, self.lava_button_rect, lava_button_color)

        # Exit Button hover and click logic
        if self.exitbutton_rect.collidepoint(mouse_pos):
            exit_button_color = self.exitbutton_hover_color
        else:
            exit_button_color = self.exitbutton_color

        self.draw_button(self.exitbutton_text, self.font, self.exitbutton_rect, exit_button_color)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.startbutton_rect.collidepoint(event.pos):
                    self.stop_sounds()
                    self.gameStateManager.set_state('first-level')
                elif self.lava_button_rect.collidepoint(event.pos):
                    self.stop_sounds()
                    self.gameStateManager.set_state('lava-labyrinth')  # Switch to Lava Labyrinth
                elif self.exitbutton_rect.collidepoint(event.pos):
                    self.stop_sounds()
                    pygame.quit()
                    sys.exit()

    def draw_button(self, text, font, rect, color, border_radius=20):
        pygame.draw.rect(self.display, color, rect, border_radius=border_radius)
        text_surface = font.render(text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=rect.center)
        self.display.blit(text_surface, text_rect)


class LavaLabyrinth:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager

        # Word and syllable data for Lava Labyrinth
        self.word_list = [
            {"word": "volcano", "syllables": ["vol", "ca", "no"]},
            {"word": "eruption", "syllables": ["e", "rup", "tion"]},
            {"word": "lava", "syllables": ["la", "va"]},
            {"word": "labyrinth", "syllables": ["la", "by", "rinth"]}
        ]
        self.current_word_data = None
        self.correct_syllables = []
        self.current_syllable_selection = []
        self.syllable_buttons = []

        self.font = pygame.font.SysFont('Arial', 40)
        self.button_font = pygame.font.SysFont('Arial', 30)

        # Load background (Lava Labyrinth background)
        background_image_path = os.path.join('graphics', 'lava_labyrinth.jpg')  # Your lava labyrinth background
        self.background_image = pygame.image.load(background_image_path).convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image,
                                                       (self.display.get_width(), self.display.get_height()))

        self.start_time = None
        self.lava_flow_time_limit = 10  # 10-second lava flow timer
        self.load_new_word()

    def load_new_word(self):
        """Load a new word with its syllables."""
        self.current_word_data = random.choice(self.word_list)
        self.correct_syllables = self.current_word_data["syllables"]
        random.shuffle(self.correct_syllables)  # Shuffle syllables for the player
        self.create_syllable_buttons()
        self.current_syllable_selection = []
        self.start_time = time.time()

    def create_syllable_buttons(self):
        """Create buttons for each syllable."""
        self.syllable_buttons = []
        button_width, button_height = 100, 50
        total_width = len(self.correct_syllables) * (button_width + 20)
        x_start = (self.display.get_width() - total_width) // 2

        for i, syllable in enumerate(self.correct_syllables):
            x_position = x_start + i * (button_width + 20)
            y_position = self.display.get_height() // 2 + 50
            button_rect = pygame.Rect(x_position, y_position, button_width, button_height)
            self.syllable_buttons.append({"rect": button_rect, "syllable": syllable})

    def check_answer(self):
        """Check if the player's syllable selection is correct."""
        return self.current_syllable_selection == self.current_word_data["syllables"]

    def run(self):
        running = True
        while running:
            elapsed_time = time.time() - self.start_time
            remaining_time = max(0, self.lava_flow_time_limit - elapsed_time)

            # Draw the background image
            self.display.blit(self.background_image, (0, 0))

            # Display the word to be segmented
            word_text = self.font.render(f"Segment the word: {self.current_word_data['word']}", True, (255, 255, 255))
            self.display.blit(word_text, (self.display.get_width() // 2 - word_text.get_width() // 2, 50))

            # Display the countdown timer
            timer_text = self.font.render(f"Time: {remaining_time:.1f}", True, (255, 255, 255))
            self.display.blit(timer_text, (self.display.get_width() - 150, 10))

            # Display the syllable buttons
            for button_data in self.syllable_buttons:
                rect = button_data["rect"]
                syllable = button_data["syllable"]
                pygame.draw.rect(self.display, (200, 0, 0), rect)
                syllable_text = self.button_font.render(syllable, True, (255, 255, 255))
                self.display.blit(syllable_text, (rect.x + 10, rect.y + 10))

            # Display player's syllable selection
            selection_text = self.font.render(f"Your selection: {'-'.join(self.current_syllable_selection)}", True,
                                              (255, 255, 255))
            self.display.blit(selection_text, (self.display.get_width() // 2 - selection_text.get_width() // 2, 150))

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for button_data in self.syllable_buttons:
                        if button_data["rect"].collidepoint(event.pos):
                            syllable = button_data["syllable"]
                            self.current_syllable_selection.append(syllable)

            # Check if player has selected all syllables
            if len(self.current_syllable_selection) == len(self.correct_syllables):
                if self.check_answer():
                    print("Correct! You unlocked the gate.")
                    self.load_new_word()  # Load next word
                else:
                    print("Incorrect segmentation!")
                    self.current_syllable_selection = []  # Reset selection

            # Check if timer runs out (lava eruption)
            if remaining_time <= 0:
                print("Lava erupted! You failed.")
                self.gameStateManager.set_state('game-over')  # Set to game-over state
                running = False

            pygame.display.update()
            pygame.time.Clock().tick(60)


class GameStateManager:
    def __init__(self, currentState):
        self.currentState = currentState

    def get_state(self):
        return self.currentState

    def set_state(self, state):
        self.currentState = state


if __name__ == "__main__":
    game = Game()
    game.run()
