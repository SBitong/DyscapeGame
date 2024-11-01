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

        self.gameStateManager = GameStateManager('seventh-level')
        self.mainMenu = MainMenu(self.screen, self.gameStateManager)
        self.seventhLevel = SeventhLevel(self.screen, self.gameStateManager)  # Add LavaLabyrinth level here
        self.states = {
            'main-menu': self.mainMenu,
            'seventh-level': self.seventhLevel  # New LavaLabyrinth state
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
        self.font = pygame.font.Font(font_path, 35)

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


class SeventhLevel:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager

        # Initialize the TTS engine

        # Word and syllable data for Lava Labyrinth
        self.word_list = [
            {"word": "volcano", "syllables": ["vol", "ca", "no"], "audio": "vol, cay, no", "image": "graphics/volcano.png"},
            {"word": "basketball", "syllables": ["bas", "ket", "ball"], "audio": "bas, ket, ball", "image": "graphics/basketball.png"},
            {"word": "lava", "syllables": ["la", "va"], "audio": "la, vah", "image": "graphics/lava.png"},
            {"word": "envelope", "syllables": ["en", "ve", "lope"], "audio": "ehn, veh, lope", "image": "graphics/envelope.png"},
            {"word": "tornado", "syllables": ["tor", "na", "do"], "audio": "tor, nay, dough", "image": "graphics/tornado.png"},
            {"word": "dragonfly", "syllables": ["dra", "gon", "fly"], "audio": "drah, gon, fly", "image": "graphics/dragonfly.png"},
            {"word": "dentist", "syllables": ["den", "tist"], "audio": "den, tist", "image": "graphics/dentist.png"},
            {"word": "microphone", "syllables": ["mi", "cro", "phone"], "audio": "mai, crow, phone", "image": "graphics/microphone.png"},
            {"word": "octopus", "syllables": ["oc", "to", "pus"], "audio": "aak, tow, puhs", "image": "graphics/octopus.png"},
            {"word": "radio", "syllables": ["ra", "dio"], "audio": "ray, deeyow", "image": "graphics/radio.png"},
        ]
        self.current_word_data = None
        self.correct_syllables = []
        self.current_syllable_selection = []
        self.syllable_buttons = []
        self.lives = 3  # Initialize lives
        self.correct_answers_count = 0  # Counter for correct answers
        self.last_word = None  # Keep track of the last word
        self.win = False

        self.font = pygame.font.SysFont('Arial', 40)
        self.button_font = pygame.font.SysFont('Arial', 25)

        # Load background (Lava Labyrinth background)
        background_image_path = os.path.join('graphics', 'lava_labyrinth.jpg')
        self.background_image = pygame.image.load(background_image_path).convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image,
                                                       (self.display.get_width(), self.display.get_height()))

        # Load heart image for lives
        self.heart_image = pygame.image.load(os.path.join('graphics', 'heart.png')).convert_alpha()
        self.heart_image = pygame.transform.scale(self.heart_image, (80, 50))

        # Load audio logo image
        self.audio_logo = pygame.image.load(os.path.join('graphics', 'audio-logo.png')).convert_alpha()
        self.audio_logo = pygame.transform.scale(self.audio_logo, (75, 75))  # Resize the logo if needed
        self.audio_button_rect = self.audio_logo.get_rect(center=(self.display.get_width() // 2, 300))  # Centered at the top

        self.start_time = None
        self.lava_flow_time_limit = 20  # 20-second lava flow timer
        self.load_new_word()

        # Define Submit and Reset button positions and dimensions
        self.submit_button_rect = pygame.Rect(self.display.get_width() // 2 + 60, self.display.get_height() // 2 + 200 ,
                                              120, 50)  # Moved to the left
        self.reset_button_rect = pygame.Rect(self.display.get_width() // 2 - 180, self.display.get_height() // 2 + 200,
                                             120, 50)  # Remains on the right

        self.overlay_color = None
        self.overlay_start_time = None

    def load_new_word(self):
        print("Load new word...")
        new_word_data = random.choice(self.word_list)
        while new_word_data == self.last_word:
            new_word_data = random.choice(self.word_list)

        self.current_word_data = new_word_data
        self.current_word_image = pygame.image.load(self.current_word_data["image"]).convert_alpha()
        self.current_word_image = pygame.transform.scale(self.current_word_image, (150, 150))

        self.correct_syllables = self.current_word_data["syllables"]
        self.last_word = self.current_word_data

        incorrect_syllables = ["ba", "do", "re", "mi", "fa", "sol", "la", "ti"]
        choices = self.correct_syllables + random.sample(incorrect_syllables, 2)
        random.shuffle(choices)

        self.create_syllable_buttons(choices)
        self.current_syllable_selection = []
        self.start_time = time.time()

    def create_syllable_buttons(self, choices):
        self.syllable_buttons = []
        button_width, button_height = 100, 50
        total_width = len(choices) * (button_width + 20)
        x_start = (self.display.get_width() - total_width) // 2

        for i, syllable in enumerate(choices):
            x_position = x_start + i * (button_width + 20)
            y_position = self.display.get_height() // 2 + 50
            button_rect = pygame.Rect(x_position, y_position, button_width, button_height)
            self.syllable_buttons.append({"rect": button_rect, "syllable": syllable})

    def check_answer(self):
        print(f"Player's selection : {self.current_syllable_selection}")
        print(f"Correct syllables: {self.correct_syllables}")
        return self.current_syllable_selection == self.correct_syllables

    def show_end_screen(self):
        font_path = os.path.join('fonts', 'ARIAL.TTF')
        self.endscreen_font = pygame.font.Font(font_path, 20)
        self.display.fill((0, 0, 0))

        message_y_position = 150
        if self.win:
            message_text = self.endscreen_font.render("You win!", True, (255, 255, 255))
            message_rect = message_text.get_rect(center=(self.display.get_width() // 2, message_y_position))
            self.display.blit(message_text, message_rect)

            next_level_button = pygame.Rect(self.display.get_width() // 2 - 100, 250, 200, 50)
            restart_level_button = pygame.Rect(self.display.get_width() // 2 - 100, 320, 200, 50)
            main_menu_button = pygame.Rect(self.display.get_width() // 2 - 100, 390, 200, 50)

            pygame.draw.rect(self.display, (0, 0, 255), next_level_button)
            pygame.draw.rect(self.display, (0, 128, 0), restart_level_button)
            pygame.draw.rect(self.display, (128, 0, 0), main_menu_button)

            next_level_text = self.endscreen_font.render("Next Level", True, (255, 255, 255))
            restart_level_text = self.endscreen_font.render("Restart Level", True, (255, 255, 255))
            main_menu_text = self.endscreen_font.render("Main Menu", True, (255, 255, 255))

            next_level_rect = next_level_text.get_rect(center=next_level_button.center)
            restart_level_rect = restart_level_text.get_rect(center=restart_level_button.center)
            main_menu_rect = main_menu_text.get_rect(center=main_menu_button.center)

            self.display.blit(next_level_text, next_level_rect)
            self.display.blit(restart_level_text, restart_level_rect)
            self.display.blit(main_menu_text, main_menu_rect)

            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if next_level_button.collidepoint(event.pos):
                            self.gameStateManager.set_state('next-level')
                            running = False
                        elif restart_level_button.collidepoint(event.pos):
                            self.restart_level()
                            running = False
                        elif main_menu_button.collidepoint(event.pos):
                            self.gameStateManager.set_state('main-menu')
                            running = False

                pygame.display.update ()
                pygame.time.Clock().tick(60)
        else:
            message_text = self.endscreen_font.render("You lose!", True, (255, 255, 255))
            message_rect = message_text.get_rect(center=(self.display.get_width() // 2, message_y_position))
            self.display.blit(message_text, message_rect)

            restart_level_button = pygame.Rect(self.display.get_width() // 2 - 100, 250, 200, 50)
            main_menu_button = pygame.Rect(self.display.get_width() // 2 - 100, 320, 200, 50)

            pygame.draw.rect(self.display, (0, 128, 0), restart_level_button)
            pygame.draw.rect(self.display, (128, 0, 0), main_menu_button)

            restart_level_text = self.endscreen_font.render("Restart Level", True, (255, 255, 255))
            main_menu_text = self.endscreen_font.render("Main Menu", True, (255, 255, 255))

            restart_level_rect = restart_level_text.get_rect(center=restart_level_button.center)
            main_menu_rect = main_menu_text.get_rect(center=main_menu_button.center)

            self.display.blit(restart_level_text, restart_level_rect)
            self.display.blit(main_menu_text, main_menu_rect)

            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if restart_level_button.collidepoint(event.pos):
                            self.restart_level()
                            running = False
                        elif main_menu_button.collidepoint(event.pos):
                            self.gameStateManager.set_state('main-menu')
                            running = False

                pygame.display.update()
                pygame.time.Clock().tick(60)

    def restart_level(self):
        """Reset the level and restart."""
        self.lives = 3  # Reset lives
        self.correct_answers_count = 0  # Reset correct answers count
        self.current_syllable_selection = []  # Reset syllable selection
        self.load_new_word()  # Load a new word

    def run(self):
        running = True
        while running:
            elapsed_time = time.time() - self.start_time
            remaining_time = max(0, self.lava_flow_time_limit - elapsed_time)

            # Calculate minutes and seconds
            minutes = int(remaining_time // 60)
            seconds = int(remaining_time % 60)

            self.display.blit(self.background_image, (0, 0))

            # Render the message text
            message_text = self.font.render("Segment the syllables of this word:", True, (255, 255, 255))
            # Position the message above the word image
            message_x = self.display.get_width() // 2 - message_text.get_width() // 2
            message_y = 30  # Adjust the Y position as needed
            self.display.blit(message_text, (message_x, message_y))

            # Display the current word image
            self.display.blit(self.current_word_image,
                              (self.display.get_width() // 2 - self.current_word_image.get_width() // 2, 100))

            for button_data in self.syllable_buttons:
                rect = button_data["rect"]
                syllable = button_data["syllable"]
                pygame.draw.rect(self.display, (200, 0, 0), rect)
                syllable_text = self.button_font.render(syllable, True, (255, 255, 255))
                self.display.blit(syllable_text, (rect.x + 10, rect.y + 10))

            selection_text = self.font.render(f"Your selection: {'-'.join(self.current_syllable_selection)}", True,
                                              (255, 255, 255))
            self.display.blit(selection_text, (self.display.get_width() // 2 - selection_text.get_width() // 2, 350))

            for i in range(self.lives):
                self.display.blit(self.heart_image, (10 + i * 60, 10))

            # Display the timer in the format 0:00
            timer_text = self.font.render(f"Time: {minutes}:{seconds:02d}", True, (255, 255, 255))
            self.display.blit(timer_text, (10, 70))  # Display time below the lives

            self.display.blit(self.audio_logo, self.audio_button_rect)

            submit_button_text = self.button_font.render("SUBMIT", True, (0, 0, 0))
            reset_button_text = self.button_font.render("RESET", True, (0, 0, 0))

            pygame.draw.rect(self.display, (254, 223, 0), self.submit_button_rect)
            pygame.draw.rect(self.display, (254, 223, 0), self.reset_button_rect)

            submit_button_rect = submit_button_text.get_rect(center=self.submit_button_rect.center)
            reset_button_rect = reset_button_text.get_rect(center=self.reset_button_rect.center)

            self.display.blit(submit_button_text, submit_button_rect)
            self.display.blit(reset_button_text, reset_button_rect)

            if self.overlay_color is not None:
                overlay_surface = pygame.Surface((self.display.get_width(), self.display.get_height()))
                overlay_surface.set_alpha(75)
                overlay_surface.fill(self.overlay_color)
                self.display.blit(overlay_surface, (0, 0))
                if time.time() - self.overlay_start_time > 0.25:
                    self.overlay_color = None

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for button_data in self.syllable_buttons:
                        if button_data["rect"].collidepoint(event.pos):
                            syllable = button_data["syllable"]
                            self.current_syllable_selection.append(syllable)
                    if self.audio_button_rect.collidepoint(event.pos):
                        engine.say(self.current_word_data["audio"])
                        engine.runAndWait()
                    elif self.submit_button_rect.collidepoint(event.pos):
                        if len(self.current_syllable_selection) >= len(self.correct_syllables):
                            if self.check_answer():
                                print("Correct! You unlocked the gate.")
                                self.correct_answers_count += 1
                                self.overlay_color = (0, 255, 0)
                                self.overlay_start_time = time.time()
                                if self.correct_answers_count >= 15:
                                    print("Congratulations! You completed the level.")
                                    self.win = True
                                    self.show_end_screen()
                                    running = False
                                else:
                                    self.load_new_word()
                            else:
                                print("Incorrect segmentation!")
                                self.current_syllable_selection = []
                                if self.lives <= 0:
                                    print("You lost all your lives! Game over.")
                                    self.show_end_screen()
                                    running = False
                    elif self.reset_button_rect.collidepoint(event.pos):
                        self.current_syllable_selection = []

            if remaining_time <= 0:
                print("Lava erupted! You failed.")
                self.lives -= 1
                self.overlay_color = (255, 0, 0)
                self.overlay_start_time = time.time()
                self.load_new_word()
                self.current_syllable_selection = []
                if self.lives <= 0:
                    print("You lost all your lives! Game over.")
                    self.show_end_screen()
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
