import pygame
import sys
import os
import random
import time
import pyttsx3
import threading
import pronouncing
import settings
from settings import *

# Initialize Pygame
pygame.init()
engine = pyttsx3.init()
rate = 150
engine.setProperty('rate', rate)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("DyscapeTheGame")

        self.gameStateManager = GameStateManager('seventh-level')
        self.mainMenu = MainMenu(self.screen, self.gameStateManager)
        self.options = Options(self.screen, self.gameStateManager)
        self.firstLevel = TheUnknownToad(self.screen, self.gameStateManager)
        self.secondLevel = LavaRush(self.screen, self.gameStateManager)
        self.thirdLevel = SylleLagoon(self.screen, self.gameStateManager)
        self.fourthLevel = TheBrokenBridge(self.screen, self.gameStateManager)
        self.fifthLevel = TheRhymeanGarden(self.screen, self.gameStateManager)
        self.sixthLevel = ForestOfNolite(self.screen, self.gameStateManager)
        self.seventhLevel = EchoingChambers(self.screen, self.gameStateManager)
        self.eighthlevel = EighthLevel(self.screen, self.gameStateManager)
        self.ninthlevel = NinthLevel(self.screen, self.gameStateManager)
        self.finallevel = FinalLevel(self.screen, self.gameStateManager)
        self.ending = Ending(self.screen, self.gameStateManager)
        self.states = {
            'main-menu': self.mainMenu,
            'options': self.options,
            'first-level': self.firstLevel,
            'second-level': self.secondLevel,
            'third-level': self.thirdLevel,
            'fourth-level': self.fourthLevel,
            'fifth-level': self.fifthLevel,
            'sixth-level': self.sixthLevel,
            'seventh-level': self.seventhLevel,
            'eighth-level': self.eighthlevel,
            'ninth-level': self.ninthlevel,
            'final-level': self.finallevel,
            'ending': self.ending
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
            pygame.display.flip()

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
        hover_sound_path = os.path.join('audio', 'mouse_hover_effect_01.mp3')  # Replace with the path to your hover sound
        self.hover_sound = pygame.mixer.Sound(hover_sound_path)
        self.start_button_hovered = False
        self.option_button_hovered = False
        self.exit_button_hovered = False

        # Load the game music
        music_path = os.path.join('audio','01 Hei Shao.mp3')
        self.main_menu_bgm = pygame.mixer.Sound(music_path)
        self.main_menu_bgm_isplaying = False

        # Load ambient nature sound
        ambient_path = os.path.join('audio', 'bird_chirping.mp3')  # Ensure the correct path
        self.ambient_sound = pygame.mixer.Sound(ambient_path)
        self.ambient_sound_isplaying = False

        # Load the main-menu background and adjust to fit on display
        background_image_path = os.path.join('graphics', 'main-menu-background-1.jpg')
        self.background_image = pygame.image.load(background_image_path).convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image,(self.display.get_width(), self.display.get_height()))

        # Load the game logo
        game_logo_path = os.path.join('graphics', 'DYSCAPE-LOGO2.png')
        self.game_logo = pygame.image.load(game_logo_path).convert_alpha()
        self.logo_width, self.logo_height = self.game_logo.get_size()

        # Load, extract, and multiply the leaves from the spring-leaf spritesheet
        springleaf_path = os.path.join('graphics','Spring-Leaf.png')
        self.springleaf_sprite = pygame.image.load(springleaf_path).convert_alpha()
        scale_factor = 3 #times two leaf size
        self.leaf_frames = self.extract_leaf_frames(self.springleaf_sprite, 5, scale_factor)
        self.leaves = [self.create_leaf() for x in range(40)]

        # Start Button properties
        self.startbutton_color = (255, 200, 0)
        self.startbutton_hover_color = (255, 170, 0)
        self.startbutton_text = "Start"
        self.startbutton_rect = pygame.Rect((self.display.get_width() // 2 - 150, 400), (300, 80))
        #self.startbutton_text = self.font.render('Start', True, (0, 0, 0))

        # Options Button properties
        self.optionbutton_color = (255, 200, 0)
        self.optionbutton_hover_color = (255, 170, 0)
        self.optionbutton_text = "Options"
        self.optionbutton_rect = pygame.Rect(((self.display.get_width() // 2) - (250 // 2), 500), (250, 70))

        # Exit Button properties
        self.exitbutton_color = (255, 200, 0)
        self.exitbutton_hover_color = (255, 170, 0)
        self.exitbutton_text = "Exit Game"
        self.exitbutton_rect = pygame.Rect(((self.display.get_width() // 2) - (250 // 2), 590), (250, 70))

    def stop_sounds(self):
        self.main_menu_bgm.stop()
        self.ambient_sound.stop()
        self.main_menu_bgm_isplaying = False
        self.ambient_sound_isplaying = False

    def draw_button(self, text, font, rect, color, border_radius = 20):
        # Create a surface for the button with per-pixel alpha
        button_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

        # Draw the rounded rectangle on this surface
        pygame.draw.rect(button_surface, color, button_surface.get_rect(), border_radius=border_radius)

        # Render the text and get its rect
        text_surface = font.render(text, True, (0, 0, 0))  # Black text color
        text_rect = text_surface.get_rect(center=(rect.width // 2, rect.height // 2))

        # Blit the text onto the button surface
        button_surface.blit(text_surface, text_rect)

        # Blit the button surface onto the main display
        self.display.blit(button_surface, rect.topleft)

    def extract_leaf_frames(self, sprite_sheet, num_frames, scale_factor):
        frames = []
        frame_width = sprite_sheet.get_width() // num_frames
        frame_height = sprite_sheet.get_height()
        for i in range(num_frames):
            frame = sprite_sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
            scaled_frame = pygame.transform.scale(frame, (int(frame_width * scale_factor), int(frame_height * scale_factor)))
            frames.append(scaled_frame)
        return frames

    def create_leaf(self):
        leaf = {
            "frame_index": 0,
            "x": random.randint(0, self.display.get_width()),
            "y": random.randint(-self.display.get_height(), 0),
            "speed": random.uniform(0.1, 0.4),
            "animation_speed": random.uniform(1, 2),
            "animation_timer": 0,
            "horizontal_speed": random.uniform(-0.5, -0.2)
        }
        return leaf

    def update_leaf(self, leaf):
        # Update the animation frame
        leaf["animation_timer"] += 1 / FPS
        if leaf["animation_timer"] >= leaf["animation_speed"]:
            leaf["animation_timer"] = 0
            leaf["frame_index"] = (leaf["frame_index"] + 1) % len(self.leaf_frames)

        # Move the leaf down and slightly to the left
        leaf["y"] += leaf["speed"]
        leaf["x"] += leaf["horizontal_speed"]

        if leaf["y"] > self.display.get_height():  # If the leaf goes off the screen, reset its position
            leaf["y"] = random.randint(-self.display.get_height(), 0)
            leaf["x"] = random.randint(0, self.display.get_width())

    def run(self):
        running = True
        while running:
            if not self.main_menu_bgm_isplaying:
                self.main_menu_bgm.play(-1)
                self.main_menu_bgm_isplaying = True

            if not self.ambient_sound_isplaying:
                self.ambient_sound.play(-1)
                self.ambient_sound_isplaying = True

            self.display.blit(self.background_image, (0, 0))
            self.display.blit(self.game_logo, ((WIDTH // 2) - (self.logo_width // 2), 90))

            mouse_pos = pygame.mouse.get_pos()

            # Handle button hover and clicks
            if self.startbutton_rect.collidepoint(mouse_pos):
                if not self.start_button_hovered:
                    self.hover_sound.play()
                    self.start_button_hovered = True
                start_button_color = self.startbutton_hover_color
            else:
                start_button_color = self.startbutton_color
                self.start_button_hovered = False

            self.draw_button(self.startbutton_text, self.font, self.startbutton_rect, start_button_color)

            if self.optionbutton_rect.collidepoint(mouse_pos):
                if not self.option_button_hovered:
                    self.hover_sound.play()
                    self.option_button_hovered = True
                option_button_color = self.optionbutton_hover_color
            else:
                option_button_color = self.optionbutton_color
                self.option_button_hovered = False

            self.draw_button(self.optionbutton_text, self.font, self.optionbutton_rect, option_button_color)

            if self.exitbutton_rect.collidepoint(mouse_pos):
                if not self.exit_button_hovered:
                    self.hover_sound.play()
                    self.exit_button_hovered = True
                exit_button_color = self.exitbutton_hover_color
            else:
                exit_button_color = self.exitbutton_color
                self.exit_button_hovered = False

            self.draw_button(self.exitbutton_text, self.font, self.exitbutton_rect, exit_button_color)

            # Update and draw leaves
            for leaf in self.leaves:
                self.update_leaf(leaf)
                self.display.blit(self.leaf_frames[leaf["frame_index"]], (leaf["x"], leaf["y"]))

            # Event Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if the start button is clicked
                    if self.startbutton_rect.collidepoint(event.pos):
                        self.stop_sounds()
                        self.gameStateManager.set_state('first-level')
                        engine.say("Start")
                        engine.runAndWait()
                        running = False  # Exit the loop to transition to the next state

                    elif self.optionbutton_rect.collidepoint(event.pos):
                        self.stop_sounds()
                        self.gameStateManager.set_state('options')
                        engine.say("Options")
                        engine.runAndWait()
                        running = False  # Exit the loop to transition to the next state

                    elif self.exitbutton_rect.collidepoint(event.pos):
                        self.stop_sounds()
                        pygame.quit()
                        sys.exit()

            pygame.display.update()

class Options:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager

        # Load the background image
        background_image_path = os.path.join('graphics', 'main-menu-background-1.jpg')
        self.background_image = pygame.image.load(background_image_path).convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image, (self.display.get_width(), self.display.get_height()))

        # Load the specified font
        self.font = pygame.font.SysFont(settings.FONT_NAME, settings.FONT_SIZE)

        # Volume slider properties
        self.slider_length = 300
        self.slider_height = 10
        self.slider_color = (200, 200, 200)
        self.knob_color = (255, 255, 255)
        self.knob_radius = 10

        # Center the volume slider
        self.slider_x = (self.display.get_width() - self.slider_length) // 2
        self.slider_y = self.display.get_height() // 3
        self.knob_position = self.slider_x + int(settings.MASTER_VOLUME * self.slider_length)

        # TTS toggle button properties
        self.tts_toggle_rect = pygame.Rect((self.display.get_width() - 150) // 2, self.slider_y + 100, 150, 50)
        self.tts_enabled = settings.TTS_ENABLED

        # Font selection properties
        self.fonts = ["Arial", "Courier", "Comic Sans MS", "Georgia", "Times New Roman"]
        self.current_font_index = self.fonts.index(settings.FONT_NAME) if settings.FONT_NAME in self.fonts else 0
        self.font_rect = pygame.Rect((self.display.get_width() - 300) // 2, self.tts_toggle_rect.y + 100, 300, 50)

    def run(self):
        running = True
        while running:
            self.display.blit(self.background_image, (0, 0))  # Draw the background image

            # Draw the volume slider
            pygame.draw.rect(self.display, self.slider_color, (self.slider_x, self.slider_y, self.slider_length, self.slider_height))
            pygame.draw.circle(self.display, self.knob_color, (self.knob_position, self.slider_y + self.slider_height // 2), self.knob_radius)

            # Display volume label
            volume_label = self.font.render("Master Volume", True, (255, 255, 255))
            volume_label_rect = volume_label.get_rect(center=(self.display.get_width() // 2, self.slider_y - 40))
            self.display.blit(volume_label, volume_label_rect)

            # Draw TTS toggle
            tts_text = self.font.render("TTS: On" if self.tts_enabled else "TTS: Off", True, (255, 255, 255))
            pygame.draw.rect(self.display, (0, 100, 0) if self.tts_enabled else (100, 0, 0), self.tts_toggle_rect)
            tts_text_rect = tts_text.get_rect(center=self.tts_toggle_rect.center)
            self.display.blit(tts_text, tts_text_rect)

            # Draw font selection
            font_text = self.font.render(f"Font: {self.fonts[self.current_font_index]}", True, (255, 255, 255))
            pygame.draw.rect(self.display, (100, 100, 100), self.font_rect)
            font_text_rect = font_text.get_rect(center=self.font_rect.center)
            self.display.blit(font_text, font_text_rect)

            # Event Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.is_mouse_on_slider(event.pos):
                        self.adjust_volume(event.pos)
                    elif self.tts_toggle_rect.collidepoint(event.pos):
                        self.toggle_tts()
                    elif self.font_rect.collidepoint(event.pos):
                        self.cycle_font()
                elif event.type == pygame.MOUSEMOTION:
                    if event.buttons[0] and self.is_mouse_on_slider(event.pos):
                        self.adjust_volume(event.pos)

            pygame.display.update()

            # Go back to the main menu
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                running = False
                self.save_settings()
                self.gameStateManager.set_state('main-menu')

    def is_mouse_on_slider(self, mouse_pos):
        return (self.slider_x <= mouse_pos[0] <= self.slider_x + self.slider_length and
                self.slider_y - self.knob_radius <= mouse_pos[1] <= self.slider_y + self.slider_height + self.knob_radius)

    def adjust_volume(self, mouse_pos):
        self.knob_position = max(self.slider_x, min(mouse_pos[0], self.slider_x + self.slider_length))
        settings.MASTER_VOLUME = (self.knob_position - self.slider_x) / self.slider_length
        pygame.mixer.music.set_volume(settings.MASTER_VOLUME)

    def toggle_tts(self):
        self.tts_enabled = not self.tts_enabled
        settings.TTS_ENABLED = self.tts_enabled

    def cycle_font(self):
        self.current_font_index = (self.current_font_index + 1) % len(self.fonts)
        settings.FONT_NAME = self.fonts[self.current_font_index]
        self.font = pygame.font.SysFont(settings.FONT_NAME, settings.FONT_SIZE)

    def save_settings(self):
        # Save the settings back to settings.py
        with open('settings.py', 'w') as f:
            f.write(f"MASTER_VOLUME = {settings.MASTER_VOLUME}\n")
            f.write(f"TTS_ENABLED = {settings.TTS_ENABLED}\n")
            f.write(f"FONT_NAME = '{settings.FONT_NAME}'\n")
            f.write(f"FONT_SIZE = {settings.FONT_SIZE}\n")

class TheUnknownToad:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager
        self.font = pygame.font.SysFont('Arial', 36)
        self.white = WHITE
        self.black = BLACK
        self.win = False
        self.gameOver = False
        pygame.mixer.init()

        self.continue_button = pygame.Rect(self.display.get_width() // 2 - 100, self.display.get_height() - 100, 200,
                                           50)
        self.countdown_font = pygame.font.Font(None, 100)
        self.is_restart = False  # Track if the game is a restart

        # Number of lives the player has
        self.lives = 3

        background_image_path = os.path.join('graphics','cave-background.png')
        self.background_image = pygame.image.load(background_image_path).convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image, (self.display.get_width(), self.display.get_height()))

        background_image_path_2 = os.path.join('graphics', 'dyscape-entrance-bg.png')
        self.background_image_2 = pygame.image.load(background_image_path_2).convert_alpha()
        self.background_image_2 = pygame.transform.scale(self.background_image_2,(self.display.get_width(), self.display.get_height()))

        # Questions with multiple choices and the correct answer
        self.qa_dict = {
            "The dog ran fast.": {
                "choices": ["2", "3", "4", "5"],
                "answer": "4"
            },
            "He eats lunch at his own house.": {
                "choices": ["5", "6", "7", "8"],
                "answer": "7"
            },
            "I will help you bake cake.": {
                "choices": ["6", "5", "8", "9"],
                "answer": "6"
            },
            "Cats like to play with yarn.": {
                "choices": ["6", "7", "8", "9"],
                "answer": "6"
            },
            "She swims in the cool lake.": {
                "choices": ["8", "7", "6", "5"],
                "answer": "6"
            },
            "They built the shed last week.": {
                "choices": ["2", "4", "6", "8"],
                "answer": "6"
            },
            "The sun will set in the west.": {
                "choices": ["6", "7", "8", "9"],
                "answer": "7"
            },
            "Birds fly high in the sky at night.": {
                "choices": ["9", "7", "5", "8"],
                "answer": "8"
            },
            "We jump and run in the yard.": {
                "choices": ["7", "8", "9", "10"],
                "answer": "7"
            },
            "He gave her a red rose.": {
                "choices": ["7", "6", "2", "3"],
                "answer": "6"
            },
        }

        self.questions = list(self.qa_dict.keys())  # List of questions
        self.choice_rects = []

        # Shuffle questions when the level starts
        self.shuffle_questions()

        # Use the imported word_colors dictionary


    def read_question_aloud(self, text):
        """Function to use pyttsx3 to read the text aloud."""
        engine.say(text)
        engine.runAndWait()

    def shuffle_questions(self):
        """Shuffles the questions and resets the current question index."""
        random.shuffle(self.questions)
        self.current_question_index = 0  # Reset index after shuffle

    def reset_level(self):
        """Resets the level by shuffling questions and resetting lives."""
        print("Restarting level...")  # Optional debug message
        self.lives = 3  # Reset lives to 3
        self.shuffle_questions()  # Shuffle the questions again
        self.is_restart = True

    def init_water_droplets(self, droplet_count=5):
        """Initialize water droplets with random positions and speeds."""
        self.droplets = []
        for _ in range(droplet_count):
            x = random.randint(0, self.display.get_width())
            y = random.randint(-100, self.display.get_height())  # Some droplets start above the screen
            width = random.randint(2, 3)  # Droplet width
            height = random.randint(8, 12)  # Droplet height to give it an elongated shape
            speed = random.uniform(10, 12)  # Faster falling speed for droplets
            color = (173, 216, 230)  # Light blue color for water droplets
            self.droplets.append([x, y, width, height, speed, color])

    def update_water_droplets(self):
        """Update the position of water droplets, resetting them if they go off-screen."""
        for droplet in self.droplets:
            droplet[1] += droplet[4]  # Move droplet down based on speed

            # If the droplet goes off the screen, reset it to a random position above the screen
            if droplet[1] > self.display.get_height():
                droplet[1] = random.uniform(-100, -10)  # Respawn above the screen
                droplet[0] = random.randint(0, self.display.get_width())

    def draw_water_droplets(self):
        """Draw the water droplets on the screen."""
        for droplet in self.droplets:
            pygame.draw.ellipse(self.display, droplet[5], (int(droplet[0]), int(droplet[1]), droplet[2], droplet[3]))

    def run_title_screen(self):
        title_text = "THE UNKNOWN TOAD"
        font_path_1 = os.path.join('fonts', 'ARIALBLACKITALIC.TTF')
        font_path_2 = os.path.join('fonts', 'ARIAL.TTF')
        title_font = pygame.font.Font(font_path_1, 50)  # Large font for the title
        button_font = pygame.font.Font(font_path_2, 20)

        button_color = (255, 255, 0)  # Yellow color for the button
        button_hover_color = (200, 200, 0)  # Darker yellow for hover effect
        button_rect = pygame.Rect((self.display.get_width() // 2 - 100, self.display.get_height() // 2 + 50),
                                  (200, 50))  # Button dimensions

        running = True
        while running:
            self.display.fill((0, 0, 0))  # Fill the screen with black

            # Render the title text
            title_surface = title_font.render(title_text, True, (255, 255, 255))  # White color for the title
            title_rect = title_surface.get_rect(
                center=(self.display.get_width() // 2, self.display.get_height() // 2 - 50))
            self.display.blit(title_surface, title_rect)  # Blit title text

            # Check if the mouse is over the button
            mouse_pos = pygame.mouse.get_pos()  # Get the mouse position
            if button_rect.collidepoint(mouse_pos):
                current_button_color = button_hover_color  # Use hover color
            else:
                current_button_color = button_color  # Use normal color

            # Draw the button with the current color
            pygame.draw.rect(self.display, current_button_color, button_rect)  # Draw button
            button_text = button_font.render("Continue", True, (0, 0, 0))  # Black text for the button
            button_text_rect = button_text.get_rect(center=button_rect.center)  # Center text in button
            self.display.blit(button_text, button_text_rect)  # Blit button text

            # Event handling for button click
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        if button_rect.collidepoint(mouse_pos):  # Check if mouse is over the button
                            running = False  # Exit the loop to move to the next screen

            pygame.display.flip()
            pygame.time.Clock().tick(60)  # Control the frame rate

    def run_dialogue_strip_1(self):
        self.dialogue_font = pygame.font.Font(None, 36)

        # Dialogue list (narrating the FourthLevel)
        self.dialogue_lines = [
            "Dyscape was once a bright and wonderful place, a world full of words, learning, and light.",  # 1
            "Its kingdom was amazingly ruled by a king. Its skies were vibrant, and the land was abundant \n and filled with knowledge.",
            # 2
            "Every citizen were living in prosper, and the community is thriving, showing the power of learning.",  # 3
            "But something bad was coming. An unknown being called Confusion infiltrated Dyscape.",  # 4
            "He destroyed the city, polluted the forest, and scrambled the landscapes.",  # 5
            "He hypnotized every citizen in the kingdom and stole their capability to sustain knowledge",  # 6
            "Under his will, Confusion took the king as his hostage and now resides in the tower",  # 7
            "Now, the world of Dyscape is engulfed in chaos, and it's only a  matter of time before the world \n will drown into darkness.", # 8
            " ",  # Pause
            "In an alternate world, there was a man who was camping in the woods near a lake.",  # 9
            "He was setting up his campfire when he heard a strange sound from the lake.",  # 10
            "He looked behind his back and saw a mysterious glow near the side of the lake.",  # 11
            "He went near the lake, and as soon as he was close, he heard a voice.",  # 12
            "'Help us, our world is in danger', the unknown voice said.",  # 13
            "He touched the water out of curiosity and suddenly, the water pulled him into the depths.",  # 14
            " ", # Pause
            "All at once, the water shot him up high and sent him into the strange and unfamiliar world", # 15
            "He starts shouting as he fell right on to the trees' branches, landed on the ground and fainted", # 16
            "( man shouting as he is falling )", # man shouting
            "( a loud bang... )", # load bang
            "( birds chirping in the forest ) ", # P17
            "After some time, he wakes up to a unknown creature staring at him.", # 18
            "He stood up, wipes his face as he tries to bring back his composure.", # 19
            "He looked again, and saw a magical owl with round glasses, a red hat, and a scarf in its neck.", # 20
            "The man looked confused as he remain clueless. This is how the story unfolds." # 21
        ]

        # Corresponding images for each dialogue line
        self.dialogue_images = [
            pygame.image.load(os.path.join('graphics', 'dyscape-1.png')).convert_alpha(),  # 1
            pygame.image.load(os.path.join('graphics', 'Dyscape-from-top.png')).convert_alpha(),  # 2
            pygame.image.load(os.path.join('graphics', 'inside-dyscape.png')).convert_alpha(),  # 3
            pygame.image.load(os.path.join('graphics', 'confusion-arrives.png')).convert_alpha(),  # 4
            pygame.image.load(os.path.join('graphics', 'dyscape-under-attack.png')).convert_alpha(),  # 5
            pygame.image.load(os.path.join('graphics', 'confusion-hypnotize.png')).convert_alpha(),  # 6
            pygame.image.load(os.path.join('graphics', 'king-strangle.png')).convert_alpha(),  # 7
            pygame.image.load(os.path.join('graphics', 'dyscape-in-chaos.png')).convert_alpha(),  # 8
            pygame.image.load(os.path.join('graphics', 'black-screen.png')).convert_alpha(),  # Pause
            pygame.image.load(os.path.join('graphics', 'character-camping.png')).convert_alpha(),  # 9
            pygame.image.load(os.path.join('graphics', 'strange-sound.png')).convert_alpha(),  # 10
            pygame.image.load(os.path.join('graphics', 'mysterious-glow.png')).convert_alpha(),  # 11
            pygame.image.load(os.path.join('graphics', 'glow-closeup.png')).convert_alpha(),  # 12
            pygame.image.load(os.path.join('graphics', 'the-glow-speaks.png')).convert_alpha(),  # 13
            pygame.image.load(os.path.join('graphics', 'glow-pulled-the-character.png')).convert_alpha(),  # 14
            pygame.image.load(os.path.join('graphics', 'black-screen.png')).convert_alpha(),  # Pause
            pygame.image.load(os.path.join('graphics', 'dyscape-entrance.png')).convert_alpha(),  # 15
            pygame.image.load(os.path.join('graphics', 'dyscape-entrance-2.png')).convert_alpha(), # 16
            pygame.image.load(os.path.join('graphics', 'black-screen.png')).convert_alpha(),  # man falling
            pygame.image.load(os.path.join('graphics', 'black-screen.png')).convert_alpha(),  # loud bang
            pygame.image.load(os.path.join('graphics', 'dyscape-entrance-3.png')).convert_alpha(), # 17
            pygame.image.load(os.path.join('graphics', 'dyscape-entrance-4.png')).convert_alpha(), # 18
            pygame.image.load(os.path.join('graphics', 'dyscape-entrance-5.png')).convert_alpha(), # 19
            pygame.image.load(os.path.join('graphics', 'dyscape-entrance-6.png')).convert_alpha(), # 20
            pygame.image.load(os.path.join('graphics', 'dyscape-entrance-7.png')).convert_alpha(), # 21
        ]

        # Corresponding narration files for each dialogue line
        self.dialogue_sounds = [
            pygame.mixer.Sound(os.path.join('audio', 'first-narrator-1.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'first-narrator-2.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'first-narrator-3.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'first-narrator-4.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'first-narrator-5.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'first-narrator-6.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'first-narrator-7.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'first-narrator-8.mp3')),
            pygame.mixer.Sound(os.path.join('audio', '500-milliseconds-of-silence.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'first-narrator-9.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'first-narrator-10.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'first-narrator-11.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'first-narrator-12.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'first-narrator-13.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'first-narrator-14.mp3')),
            pygame.mixer.Sound(os.path.join('audio', '500-milliseconds-of-silence.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'first-narrator-15.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'first-narrator-16.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'first-man-falling.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'first-loud-bang.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'first-narrator-17.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'first-narrator-18.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'first-narrator-19.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'first-narrator-20.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'first-narrator-21.mp3')),
        ]

        # Scale the images to fit the screen
        self.dialogue_images = [
            pygame.transform.scale(img, (self.display.get_width(), self.display.get_height() - 100)) for img in
            self.dialogue_images
        ]

        self.dialogue_index = 0
        running = True

        # Initialize the mixer for playing audio
        pygame.mixer.init()

        # Flag to check if narration is playing
        self.narration_playing = False

        def play_narration():
            """Play the narration for the current dialogue line."""
            self.narration_playing = True
            self.dialogue_sounds[self.dialogue_index].play()
            pygame.time.set_timer(pygame.USEREVENT,
                                  int(self.dialogue_sounds[self.dialogue_index].get_length() * 1000))

        # Play the first narration automatically
        play_narration()

        while running:
            self.display.fill((0, 0, 0))  # Black background for the dialogue screen

            # Display the corresponding image
            self.display.blit(self.dialogue_images[self.dialogue_index], (0, 0))

            # Create and display the dialogue box
            dialogue_box_rect = pygame.Rect(0, self.display.get_height() - 150, self.display.get_width(), 150)
            pygame.draw.rect(self.display, (0, 0, 0), dialogue_box_rect)

            # Render the current dialogue line
            dialogue_text = self.dialogue_font.render(self.dialogue_lines[self.dialogue_index], True,
                                                      (255, 255, 255))  # White font
            dialogue_rect = dialogue_text.get_rect(
                center=(self.display.get_width() // 2, self.display.get_height() - 75))
            self.display.blit(dialogue_text, dialogue_rect)

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    sys.exit()

                # Allow the player to skip the narration and move to the next slide with the spacebar
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.dialogue_sounds[self.dialogue_index].stop()  # Stop the current narration
                        self.narration_playing = False
                        self.dialogue_index += 1
                        if self.dialogue_index >= len(self.dialogue_lines):
                            running = False  # End the dialogue and start the game
                        else:
                            play_narration()  # Play the next narration

                # Check if narration finished
                if event.type == pygame.USEREVENT and self.narration_playing:
                    self.narration_playing = False
                    self.dialogue_index += 1
                    if self.dialogue_index >= len(self.dialogue_lines):
                        running = False  # End the dialogue and start the game
                    else:
                        play_narration()  # Play the next narration

            pygame.display.update()

    def load_spritesheet(self,filename, frame_width, frame_height, scale_factor):
        # Load the sprite sheet image
        spritesheet = pygame.image.load(os.path.join('graphics', filename)).convert_alpha()
        # Get the width and height of the entire sprite sheet
        sheet_width, sheet_height = spritesheet.get_size()

        # Create a list to hold individual frames
        frames = []
        for y in range(0, sheet_height, frame_height):
            for x in range(0, sheet_width, frame_width):
                # Extract each frame by using a sub-surface
                frame = spritesheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
                # Scale the frame to make it larger
                scaled_frame = pygame.transform.scale(frame, (
                int(frame_width * scale_factor), int(frame_height * scale_factor)))
                frames.append(scaled_frame)

        return frames

    def run_dialogue_strip_2(self):
        # Initialize pygame's mixer for audio (if needed)
        pygame.mixer.init()

        # Load the owl sprite sheet and extract frames for animation
        owl_frames = self.load_spritesheet('owl-flying.png', 48, 48, scale_factor=6)
        owl_frame_index = 0  # Start with the first frame of the animation
        owl_animation_speed = 5  # Change the frame every 5 frames of the game loop

        # Load character images (only one image for the player)
        char1_image = pygame.image.load(os.path.join('graphics', 'character-avatar.png'))
        char1_image = pygame.transform.scale(char1_image, (200, 200))

        dialogue_data = [
            {"name": "You", "text": "Ugh... What is this place? and who are you??", "image": char1_image},
            {"name": "Magical Owl", "text": "Hello there, adventurer! I believe you heard my call.",
             "audio": "owl-talking-1.mp3"},
            {"name": "You", "text": "Huh? What call?", "image": char1_image},
            {"name": "Magical Owl", "text": "The voice from the lake. I am the one who called on to you",
             "audio": "owl-talking-2.mp3"},
            {"name": "Magical Owl",
             "text": "By the way, my name is Lexi and I'm an owl. You are inside our world, Dyscape.",
             "audio": "owl-talking-3.mp3"},
            {"name": "Lexi the Owl", "text": "I called you because this world needs your help.",
             "audio": "owl-talking-4.mp3"},
            {"name": "Lexi the Owl", "text": "Someone invaded us. And he is trying to take over our world.",
             "audio": "owl-talking-5.mp3"},
            {"name": "You", "text": "Who's he? Sorry I am still confused about all this.", "image": char1_image},
            {"name": "Lexi the Owl",
             "text": "His name is Confusion. He suddenly attacked the central where the castle is.",
             "audio": "owl-talking-6.mp3"},
            {"name": "Lexi the Owl", "text": "He took the king as his hostage and he is now at the tower of...",
             "audio": "owl-talking-7.mp3"},
            {"name": "Lexi the Owl", "text": "tower of.. uh... what is the name of the tower? I forgot.",
             "audio": "owl-talking-8.mp3"},
            {"name": "You", "text": "Okay, okay. But look, why me, Lexi? I don't even have any superpowers.",
             "image": char1_image},
            {"name": "Lexi the Owl",
             "text": "Well, everyone here were infected by his hypnotism. So everyone here lost their ability to think.",
             "audio": "owl-talking-9.mp3"},
            {"name": "Lexi the Owl", "text": "Let's go, adventurer. We don't have much time left.",
             "audio": "owl-talking-10.mp3"},
            {"name": "You", "text": "Wait up! Okay Lexi, I'm coming with you", "image": char1_image},
            {"name": "You", "text": "But where are we going?", "image": char1_image},
            {"name": "Lexi the Owl", "text": "Listen here, we are entering Dyscape and there is only one PASSAGEWAY.",
             "audio": "owl-talking-11.mp3"},
            {"name": "Lexi the Owl",
             "text": "That passageway is guarded by a TOAD. Do as he wish and he will let you pass.",
             "audio": "owl-talking-12.mp3"},
            {"name": "Lexi the Owl",
             "text": "Me and that toad doesnt really get along. So you go on your own. Just follow this path",
             "audio": "owl-talking-13.mp3"},
            {"name": "Lexi the Owl", "text": "I'll meet you on the other side of the passageway. See you there!",
             "audio": "owl-talking-14.mp3"},
            {"name": "You", "text": "Hey! Hey!! Don't leave me alone.", "image": char1_image},
            {"name": "You", "text": "Ugh. Guess I have to do it on my own first.", "image": char1_image},
        ]

        # Preload audio files
        audio_files = {}
        for dialogue in dialogue_data:
            if "audio" in dialogue:
                audio_file = dialogue["audio"]
                audio_files[audio_file] = pygame.mixer.Sound(os.path.join("audio", audio_file))

        dialogue_box_height = 150  # Height of the dialogue box surface
        dialogue_font = pygame.font.Font(None, 32)  # Font for dialogue text
        name_font = pygame.font.Font(None, 36)  # Font for character names
        space_prompt_font = pygame.font.Font(None, 28)  # Font for "Press SPACE to continue"

        current_line = 0
        text_displayed = ""
        text_index = 0
        text_speed = 2  # Speed of text animation
        audio_played = False  # Flag to track if audio has been played for the current line
        current_sound = None  # Track the currently playing sound

        running = True
        clock = pygame.time.Clock()

        while running:
            self.display.blit(self.background_image_2, (0, 0))

            # Create the dialogue box at the bottom
            dialogue_box = pygame.Surface((self.display.get_width(), dialogue_box_height))
            dialogue_box.fill((255, 219, 172))  # Light background for the dialogue box
            dialogue_box_rect = dialogue_box.get_rect(topleft=(0, self.display.get_height() - dialogue_box_height))

            # Draw the brown border around the dialogue box
            border_color = (139, 69, 19)  # Brown color (RGB)
            border_thickness = 20  # Thickness of the border
            pygame.draw.rect(self.display, border_color, dialogue_box_rect.inflate(border_thickness, border_thickness),
                             border_thickness)

            # Get the current dialogue data
            current_dialogue = dialogue_data[current_line]
            character_name = current_dialogue["name"]
            character_text = current_dialogue["text"]
            antagonist = "Magical Owl"

            # Play the audio file if it exists and hasn't been played yet
            if "audio" in current_dialogue and not audio_played:
                audio_file = current_dialogue["audio"]
                if current_sound is not None:
                    current_sound.stop()  # Stop the currently playing sound if it exists
                current_sound = audio_files[audio_file]  # Get the new sound
                current_sound.play()  # Play the new audio
                audio_played = True  # Set the flag to True to prevent replaying the audio

            # Update owl animation (cycle through the frames)
            if character_name == antagonist or character_name == "Lexi the Owl":
                owl_frame_index = (owl_frame_index + 1) % (len(owl_frames) * owl_animation_speed)
                current_owl_frame = owl_frames[owl_frame_index // owl_animation_speed]
                self.display.blit(current_owl_frame, (950, self.display.get_height() - dialogue_box_height - 300))

            # Render the character image (player) if it's the player's turn
            else:
                self.display.blit(char1_image, (50, self.display.get_height() - dialogue_box_height - 200))

            # Render the character name inside the dialogue box (above the text)
            name_surface = name_font.render(character_name, True, BLACK)
            dialogue_box.blit(name_surface, (20, 10))  # Draw name near the top inside the dialogue box

            # Text animation (add one letter at a time)
            if text_index < len(character_text):
                text_index += text_speed  # Control how fast letters are added
                text_displayed = character_text[:text_index]
            else:
                text_displayed = character_text

            # Render the dialogue text below the name
            text_surface = dialogue_font.render(text_displayed, True, BLACK)
            dialogue_box.blit(text_surface, (20, 60))  # Draw the text inside the dialogue box below the name

            # Add "Press SPACE to continue." prompt at the bottom right
            if text_index >= len(character_text):  # Show prompt only if the text is fully displayed
                space_prompt_surface = space_prompt_font.render("Press SPACE to continue.", True, (100, 100, 100))
                dialogue_box.blit(space_prompt_surface,
                                  (dialogue_box.get_width() - space_prompt_surface.get_width() - 20,
                                   dialogue_box.get_height() - space_prompt_surface.get_height() - 10))

            # Draw the dialogue box on the screen with the brown border
            self.display.blit(dialogue_box, dialogue_box_rect.topleft)

            # Event handling for advancing the dialogue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:  # Only proceed on SPACE key
                        if text_index >= len(character_text):
                            # Move to the next line of dialogue if the text is fully displayed
                            current_line += 1
                            text_index = 0
                            text_displayed = ""
                            audio_played = False  # Reset the audio flag for the next line
                            if current_line >= len(dialogue_data):
                                running = False  # Exit dialogue when all lines are done

            pygame.display.flip()
            clock.tick(60)  # Control the frame rate

    def run_dialogue_strip(self):
        # Initialize pygame's mixer for audio
        pygame.mixer.init()

        self.init_water_droplets()  # Initialize water droplets when the level starts

        # Load character images (example placeholders)
        char1_image = pygame.image.load(os.path.join('graphics', 'character-avatar.png'))
        char2_image = pygame.image.load(os.path.join('graphics', 'frog-avatar.png'))

        # Resize character images (adjust size as needed)
        char1_image = pygame.transform.scale(char1_image, (200, 200))
        char2_image = pygame.transform.scale(char2_image, (300, 300))

        dialogue_data = [
            {"name": "Unknown Toad", "text": "Good Day, Traveler! May you have safe travels ahead of you!", "image": char2_image, "audio": "frog-dialogue-1.mp3"},
            {"name": "You", "text": "Is this the way to the center of Dyscape??", "image": char1_image},
            {"name": "Unknown Toad", "text": "...", "image": char2_image},
            {"name": "Unknown Toad", "text": "Yes.. but I am afraid that I may not let you pass.", "image": char2_image, "audio": "frog-dialogue-2.mp3"},
            {"name": "You", "text": "WHAT??!?", "image": char1_image},
            {"name": "You", "text": "WHY???", "image": char1_image},
            {"name": "Unknown Toad", "text": "I don't know you, mister. And I don't know what business you have inside the tower.", "image": char2_image, "audio": "frog-dialogue-3.mp3"},
            {"name": "You", "text": "(Tower? Could it be...?)", "image": char1_image},
            {"name": "Unknown Toad", "text": "It is my job to protect the path to the Tower of Dyslexio and the King.", "image": char2_image, "audio": "frog-dialogue-4.mp3"},
            {"name": "You", "text": "(THAT'S IT! It is the tower of Dyslexio. So that is the name that the owl was murmuring about..)", "image": char1_image},
            {"name": "You", "text": "Mister Toad, I respect your values but the world is in danger. Dyscape is in danger.", "image": char1_image},
            {"name": "Unknown Toad", "text": "Danger? What are you talking about?", "image": char2_image, "audio": "frog-dialogue-5.mp3"},
            {"name": "You", "text": "Confusion invaded our world and removed the clarity for texts.", "image": char1_image},
            {"name": "You", "text": "I was called to protect Dyscape and restore it to what it was before.", "image": char1_image},
            {"name": "You", "text": "Dyscape is on slowly dying. Confusion is here, and he is planning something evil.", "image": char1_image},
            {"name": "Unknown Toad", "text": "Hmmm, I see. Well, it can't be helped.", "image": char2_image, "audio": "frog-dialogue-6.mp3"},
            {"name": "Unknown Toad", "text": "Fine, I'll let you pass.", "image": char2_image, "audio": "frog-dialogue-7.mp3"},
            {"name": "You", "text": "YES!!", "image": char1_image},
            {"name": "Unknown Toad", "text": "But on one condition, you must answer all my questions.", "image": char2_image, "audio": "frog-dialogue-8.mp3"},
            {"name": "Unknown Toad", "text": "This will assure me that you are not an enemy to us, but a friend.", "image": char2_image, "audio": "frog-dialogue-9.mp3"},
            {"name": "Unknown Toad", "text": "Are you ready, traveler?", "image": char2_image, "audio": "frog-dialogue-10.mp3"},
            {"name": "You", "text": "I am ready, Mr. Toad!", "image": char1_image},
        ]

        dialogue_box_height = 150  # Height of the dialogue box surface
        dialogue_font = pygame.font.Font(None, 32)  # Font for dialogue text
        name_font = pygame.font.Font(None, 36)  # Font for character names
        space_prompt_font = pygame.font.Font(None, 28)  # Font for "Press SPACE to continue"

        current_line = 0
        text_displayed = ""
        text_index = 0
        text_speed = 2  # Speed of text animation
        audio_played = False  # Track if audio has been played for the current dialogue

        running = True
        clock = pygame.time.Clock()

        while running:
            self.display.blit(self.background_image, (0, 0))
            self.update_water_droplets()
            self.draw_water_droplets()

            # Create the dialogue box at the bottom
            dialogue_box = pygame.Surface((self.display.get_width(), dialogue_box_height))
            dialogue_box.fill((255, 219, 172))  # Light background for the dialogue box
            dialogue_box_rect = dialogue_box.get_rect(topleft=(0, self.display.get_height() - dialogue_box_height))

            # Draw the brown border around the dialogue box
            border_color = (139, 69, 19)  # Brown color (RGB)
            border_thickness = 20  # Thickness of the border
            pygame.draw.rect(self.display, border_color, dialogue_box_rect.inflate(border_thickness, border_thickness),
                             border_thickness)

            # Get the current dialogue data
            current_dialogue = dialogue_data[current_line]
            character_name = current_dialogue["name"]
            character_text = current_dialogue["text"]
            character_image = current_dialogue["image"]
            character_audio = current_dialogue.get("audio", None)  # Get audio if available, otherwise None
            antagonist = "Unknown Toad"

            # Play audio if it's the frog's turn and the audio hasn't been played yet
            if character_audio and not audio_played:
                pygame.mixer.music.load(os.path.join('audio', character_audio))  # Load the audio file
                pygame.mixer.music.play()  # Play the audio
                audio_played = True  # Ensure audio only plays once per dialogue line

            # Render the character image on the left or right side of the dialogue box
            if character_name == antagonist:
                self.display.blit(character_image, (950, self.display.get_height() - dialogue_box_height - 300))
            else:
                self.display.blit(character_image, (50, self.display.get_height() - dialogue_box_height - 200))

            # Render the character name inside the dialogue box (above the text)
            name_surface = name_font.render(character_name, True, self.black)
            dialogue_box.blit(name_surface, (20, 10))  # Draw name near the top inside the dialogue box

            # Text animation (add one letter at a time)
            if text_index < len(character_text):
                text_index += text_speed  # Control how fast letters are added
                text_displayed = character_text[:text_index]
            else:
                text_displayed = character_text

            # Render the dialogue text below the name
            text_surface = dialogue_font.render(text_displayed, True, self.black)
            dialogue_box.blit(text_surface, (20, 60))  # Draw the text inside the dialogue box below the name

            # Add "Press SPACE to continue." prompt at the bottom right
            if text_index >= len(character_text):  # Show prompt only if the text is fully displayed
                space_prompt_surface = space_prompt_font.render("Press SPACE to continue.", True, (100, 100, 100))
                dialogue_box.blit(space_prompt_surface,
                                  (dialogue_box.get_width() - space_prompt_surface.get_width() - 20,
                                   dialogue_box.get_height() - space_prompt_surface.get_height() - 10))

            # Draw the dialogue box on the screen with the brown border
            self.display.blit(dialogue_box, dialogue_box_rect.topleft)

            # Event handling for advancing the dialogue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:  # Only proceed on SPACE key
                        if text_index >= len(character_text):
                            # Move to the next line of dialogue if the text is fully displayed
                            current_line += 1
                            text_index = 0
                            text_displayed = ""
                            audio_played = False  # Reset audio flag for the next line
                            if current_line >= len(dialogue_data):
                                running = False  # Exit dialogue when all lines are done

            pygame.display.flip()
            clock.tick(60)  # Control the frame rate

    def show_how_to_play(self):
        """Displays the 'how to play' instructions with a start button."""
        # Load the how-to-play image and scale it
        how_to_play_image = pygame.image.load(os.path.join('graphics', 'how-to-play(unknown-toad).png')).convert_alpha()
        how_to_play_image = pygame.transform.scale(how_to_play_image, (1280, 720))  # Scale to 1280x720

        # Define the start button
        start_button_rect = pygame.Rect((self.display.get_width() // 2 - 100, 600), (200, 50))  # Centered button

        # Define colors
        normal_color = (255, 255, 0)  # Yellow
        hover_color = (200, 200, 0)  # Darker yellow

        running = True
        while running:
            self.display.fill((0, 0, 0))  # Fill the screen with black
            self.display.blit(how_to_play_image, (0, 0))  # Display the how-to-play image

            # Check if the mouse is over the button
            mouse_pos = pygame.mouse.get_pos()
            if start_button_rect.collidepoint(mouse_pos):
                button_color = hover_color  # Change to darker yellow on hover
            else:
                button_color = normal_color  # Normal yellow color

            # Draw the start button
            pygame.draw.rect(self.display, button_color, start_button_rect)  # Draw button with the appropriate color
            start_text = self.font.render("Start", True, (0, 0, 0))  # Black text
            start_text_rect = start_text.get_rect(center=start_button_rect.center)  # Center text in button
            self.display.blit(start_text, start_text_rect)  # Blit start text

            # Event handling for button click
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if start_button_rect.collidepoint(event.pos):  # Check if mouse is over the button
                        running = False  # Exit the loop to proceed to the next screen

            pygame.display.update()

    def start_countdown(self):
        """Displays a 3-2-1 countdown before the game starts."""
        for count in range(3, 0, -1):
            self.display.fill((0, 0, 0))  # Black background
            countdown_surface = self.countdown_font.render(str(count), True, (255, 255, 255))  # White countdown number
            self.display.blit(countdown_surface, (self.display.get_width() // 2 - countdown_surface.get_width() // 2,
                                                  self.display.get_height() // 2 - countdown_surface.get_height() // 2))
            pygame.display.update()
            pygame.time.wait(1000)  # Wait 1 second for each countdown step

        pass

    def draw_rounded_rect(self, surface, color, rect, corner_radius):
        pygame.draw.rect(surface, color, rect, border_radius=corner_radius)

    def show_end_screen(self):
        """Display the end screen based on win/lose state."""
        running = True
        while running:
            self.display.fill(self.black)  # Clear the screen
            if self.win:
                message = "You Win!"
                next_level_button = pygame.Rect(self.display.get_width() // 2 - 100, 300, 200, 50)
                restart_button = pygame.Rect(self.display.get_width() // 2 - 100, 370, 200, 50)
                main_menu_button = pygame.Rect(self.display.get_width() // 2 - 100, 440, 200, 50)
            else:
                message = "You lose."
                restart_button = pygame.Rect(self.display.get_width() // 2 - 100, 300, 200, 50)
                main_menu_button = pygame.Rect(self.display.get_width() // 2 - 100, 370, 200, 50)

            # Display the message
            font_path = os.path.join('fonts', 'ARIAL.TTF')
            font = pygame.font.Font(font_path, 20)
            message_surface = font.render(message, True, self.white)
            self.display.blit(message_surface, (self.display.get_width() // 2 - message_surface.get_width() // 2, 200))

            # Draw buttons
            if self.win:
                pygame.draw.rect(self.display, (0, 0, 255), next_level_button)  # Blue button
                next_level_text = self.font.render("Next Level", True, self.white)
                # Center the text in the button
                next_level_text_rect = next_level_text.get_rect(center=next_level_button.center)
                self.display.blit(next_level_text, next_level_text_rect.topleft)

            pygame.draw.rect(self.display, (0, 128, 0), restart_button)  # Green button
            restart_text = self.font.render("Restart", True, self.white)
            # Center the text in the button
            restart_text_rect = restart_text.get_rect(center=restart_button.center)
            self.display.blit(restart_text, restart_text_rect.topleft)

            pygame.draw.rect(self.display, (128, 0, 0), main_menu_button)  # Red button
            main_menu_text = self.font.render("Main Menu", True, self.white)
            # Center the text in the button
            main_menu_text_rect = main_menu_text.get_rect(center=main_menu_button.center)
            self.display.blit(main_menu_text, main_menu_text_rect.topleft)

            # Event handling for button clicks
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.win:
                        if next_level_button.collidepoint(event.pos):
                            # Go to the next level
                            self.gameStateManager.set_state('second-level')
                            running = False
                    if restart_button.collidepoint(event.pos):
                        # Restart the current level
                        self.reset_level()
                        running = False
                    if main_menu_button.collidepoint(event.pos):
                        # Go to the main menu
                        self.gameStateManager.set_state('main-menu')
                        running = False

            pygame.display.update()

    def run(self):
        heart_image = pygame.image.load(os.path.join('graphics', 'heart.png'))
        heart_image = pygame.transform.scale(heart_image, (80, 50))  # Scale heart image as needed

        # Load the paper scroll image
        scroll_image = pygame.image.load(os.path.join('graphics', 'paper-scroll.png'))
        scroll_width, scroll_height = 1000, 700  # Adjust these values as needed
        scroll_image = pygame.transform.scale(scroll_image, (scroll_width, scroll_height))

        # Load the audio button image
        audio_button_image = pygame.image.load(os.path.join('graphics', 'audio-logo-black.png'))
        audio_button_image = pygame.transform.scale(audio_button_image, (50, 50))  # Adjust size as needed

        correct_answer_sound = pygame.mixer.Sound(os.path.join('audio', 'correct-answer.mp3'))
        wrong_answer_sound = pygame.mixer.Sound(os.path.join('audio', 'wrong-answer.mp3'))

        # Set audio button position (centered below the question)
        audio_button_x = (self.display.get_width() - 50) // 2
        audio_button_y = 275  # Adjust this Y position to be right below the question

        green_overlay = pygame.Surface(self.display.get_size())
        green_overlay.set_alpha(50)  # Set transparency (0 fully transparent, 255 fully opaque)
        green_overlay.fill((0, 255, 0))  # Fill with green

        red_overlay = pygame.Surface(self.display.get_size())
        red_overlay.set_alpha(50)  # Set transparency (0 fully transparent, 255 fully opaque)
        red_overlay.fill((255, 0, 0))  # Fill with red

        show_green_overlay = False  # Flag to show the green overlay
        show_red_overlay = False  # Flag to show the red overlay
        overlay_start_time = 0  # Track the time when the overlay is shown
        overlay_duration = 450  # Overlay duration in milliseconds (1 second)

        # Center the scroll image
        scroll_x = (self.display.get_width() - scroll_width) // 2
        scroll_y = 10  # Y position for the scroll (adjust as needed)

        # Initialize pyttsx3 engine
        engine = pyttsx3.init()

        # Skip the animations if this is a restart
        if not self.is_restart:
            self.run_dialogue_strip_1()
            self.run_dialogue_strip_2()
            self.run_title_screen()
            self.run_dialogue_strip()
        else:
            self.is_restart = False  # Reset the flag

        self.show_how_to_play()
        self.start_countdown() # Initialize water droplets when the level starts

        running = True
        while running:
            self.display.blit(self.background_image, (0, 0))
            self.update_water_droplets()
            self.draw_water_droplets()

            # Display the number of hearts for lives
            for i in range(self.lives):
                self.display.blit(heart_image, (10 + i * 60, 10))  # Position hearts with spacing

            # Blit the scroll image in the center
            self.display.blit(scroll_image, (scroll_x, scroll_y))

            # Render the question
            question_text = "How many words are in the sentence?"
            question_surface = self.font.render(question_text, True, self.black)
            question_rect = question_surface.get_rect(center=(scroll_x + scroll_width // 2, 225))
            self.display.blit(question_surface, question_rect.topleft)

            # Render the audio button below the question
            self.display.blit(audio_button_image, (audio_button_x, audio_button_y))

            # Get the current sentence
            sentence = self.questions[self.current_question_index]

            # Render choices
            choices = self.qa_dict[sentence]["choices"]
            y_offset_choices = audio_button_y + 70  # Adjust for spacing below the audio button

            self.choice_rects = []
            for i, choice in enumerate(choices):
                choice_surface = self.font.render(choice, True, self.black)
                choice_width = choice_surface.get_width()
                choice_height = choice_surface.get_height()

                # Calculate x_offset to center the choices horizontally
                x_offset_choice = (self.display.get_width() - choice_width) // 2

                # Increase the left and right padding by adjusting the rectangle width
                padding = 200  # Adjust this value for more or less padding

                choice_rect = pygame.Rect(
                    x_offset_choice - padding // 2,  # Move the x position to account for padding
                    y_offset_choices + i * 60,  # Adjust vertical spacing
                    choice_width + padding,  # Increase the width by the padding amount
                    choice_height + 20  # Keep the top/bottom padding as it was
                )

                # Draw a rounded rectangle (button)
                self.draw_rounded_rect(self.display, (207, 160, 102), choice_rect, corner_radius=15)  # Light gray button

                # Center the choice text inside the rounded rectangle
                choice_text_rect = choice_surface.get_rect(center=choice_rect.center)
                self.display.blit(choice_surface, choice_text_rect.topleft)
                self.choice_rects.append(choice_rect)

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if pygame.Rect(audio_button_x, audio_button_y, 50, 50).collidepoint(mouse_pos):
                        # Speak the sentence using pyttsx3 when the audio button is clicked
                        engine.say(sentence)
                        engine.runAndWait()

                    for i, rect in enumerate(self.choice_rects):
                        if rect.collidepoint(mouse_pos):
                            selected_choice = choices[i]
                            correct_answer = self.qa_dict[sentence]["answer"]

                            if selected_choice == correct_answer:
                                # Correct answer logic
                                correct_answer_sound.play()
                                show_green_overlay = True
                                overlay_start_time = pygame.time.get_ticks()
                                self.current_question_index += 1
                            else:
                                # Wrong answer logic
                                wrong_answer_sound.play()
                                show_red_overlay = True
                                overlay_start_time = pygame.time.get_ticks()
                                self.lives -= 1
                                if self.lives <= 0:
                                    print("You lost!")
                                    self.win = False
                                    self.show_end_screen()
                                    running = False
                                    break

                            if self.current_question_index >= len(self.questions):
                                print("Level completed!")
                                self.win = True
                                self.show_end_screen()
                                running = False
                            break

            if show_green_overlay:
                current_time = pygame.time.get_ticks()
                self.display.blit(green_overlay, (0, 0))

                # Check if the overlay duration has passed and hide it after the time is up
                if current_time - overlay_start_time > overlay_duration:
                    show_green_overlay = False

            if show_red_overlay:
                current_time = pygame.time.get_ticks()
                self.display.blit(red_overlay, (0, 0))

                # Check if the overlay duration has passed and hide it after the time is up
                if current_time - overlay_start_time > overlay_duration:
                    show_red_overlay = False
            pygame.display.update()

class LavaRush:
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
        self.is_restart = False
        self.countdown_font = pygame.font.Font(None, 100)

        self.font = pygame.font.SysFont('Arial', 36)
        self.button_font = pygame.font.SysFont('Arial', 25)

        # Load background (Lava Labyrinth background)
        background_image_path = os.path.join('graphics', 'lava_labyrinth.jpg')
        self.background_image = pygame.image.load(background_image_path).convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image,
                                                       (self.display.get_width(), self.display.get_height()))

        background_image_path_2 = os.path.join('graphics', 'dyscape-entrance-bg-2.png')
        self.background_image_2 = pygame.image.load(background_image_path_2).convert_alpha()
        self.background_image_2 = pygame.transform.scale(self.background_image_2,
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

    def run_title_screen(self):
        title_text = "LAVA RUSH"
        font_path_1 = os.path.join('fonts', 'ARIALBLACKITALIC.TTF')
        font_path_2 = os.path.join('fonts', 'ARIAL.TTF')
        title_font = pygame.font.Font(font_path_1, 50)  # Large font for the title
        button_font = pygame.font.Font(font_path_2, 20)

        button_color = (255, 255, 0)  # Yellow color for the button
        button_hover_color = (200, 200, 0)  # Darker yellow for hover effect
        button_rect = pygame.Rect((self.display.get_width() // 2 - 100, self.display.get_height() // 2 + 50),
                                  (200, 50))  # Button dimensions

        running = True
        while running:
            self.display.fill((0, 0, 0))  # Fill the screen with black

            # Render the title text
            title_surface = title_font.render(title_text, True, (255, 255, 255))  # White color for the title
            title_rect = title_surface.get_rect(
                center=(self.display.get_width() // 2, self.display.get_height() // 2 - 50))
            self.display.blit(title_surface, title_rect)  # Blit title text

            # Check if the mouse is over the button
            mouse_pos = pygame.mouse.get_pos()  # Get the mouse position
            if button_rect.collidepoint(mouse_pos):
                current_button_color = button_hover_color  # Use hover color
            else:
                current_button_color = button_color  # Use normal color

            # Draw the button with the current color
            pygame.draw.rect(self.display, current_button_color, button_rect)  # Draw button
            button_text = button_font.render("Continue", True, (0, 0, 0))  # Black text for the button
            button_text_rect = button_text.get_rect(center=button_rect.center)  # Center text in button
            self.display.blit(button_text, button_text_rect)  # Blit button text

            # Event handling for button click
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        if button_rect.collidepoint(mouse_pos):  # Check if mouse is over the button
                            running = False  # Exit the loop to move to the next screen

            pygame.display.flip()
            pygame.time.Clock().tick(60)  # Control the frame rate

    def load_spritesheet(self,filename, frame_width, frame_height, scale_factor):
        # Load the sprite sheet image
        spritesheet = pygame.image.load(os.path.join('graphics', filename)).convert_alpha()
        # Get the width and height of the entire sprite sheet
        sheet_width, sheet_height = spritesheet.get_size()

        # Create a list to hold individual frames
        frames = []
        for y in range(0, sheet_height, frame_height):
            for x in range(0, sheet_width, frame_width):
                # Extract each frame by using a sub-surface
                frame = spritesheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
                # Scale the frame to make it larger
                scaled_frame = pygame.transform.scale(frame, (
                int(frame_width * scale_factor), int(frame_height * scale_factor)))
                frames.append(scaled_frame)

        return frames

    def run_dialogue_strip_1(self):
        # Initialize pygame's mixer for audio (if needed)
        pygame.mixer.init()

        # Load the owl sprite sheet and extract frames for animation
        owl_frames = self.load_spritesheet('owl-flying.png', 48, 48, scale_factor=6)
        owl_frame_index = 0  # Start with the first frame of the animation
        owl_animation_speed = 5  # Change the frame every 5 frames of the game loop

        # Load character images (only one image for the player)
        char1_image = pygame.image.load(os.path.join('graphics', 'character-avatar.png'))
        char1_image = pygame.transform.scale(char1_image, (200, 200))

        dialogue_data = [
            {"name": "Lexi the Owl", "text": "Hello there, adventurer! How was your interaction with the toad?", "audio": "owl-talking-15.mp3"},
            {"name": "You", "text": "That feels weird. An owl talking, a toad talking. All this still feels unreal to me.", "image": char1_image},
            {"name": "Lexi the Owl", "text": "You will get used to it. By the way, let us proceed now.", "audio": "owl-talking-16.mp3"},
            {"name": "Lexi the Owl", "text": "The journey is long so let us not waste any time.", "audio": "owl-talking-17.mp3"},
            {"name": "You", "text": "Where are we going next, Lexi?", "image": char1_image},
            {"name": "Lexi the Owl", "text": "We are going past an ERUPTING VOLCANO.", "audio": "owl-talking-18.mp3"},
            {"name": "You", "text": "A VOLCANO!??", "image": char1_image},
        ]

        # Preload audio files
        audio_files = {}
        for dialogue in dialogue_data:
            if "audio" in dialogue:
                audio_file = dialogue["audio"]
                audio_files[audio_file] = pygame.mixer.Sound(os.path.join("audio", audio_file))

        dialogue_box_height = 150  # Height of the dialogue box surface
        dialogue_font = pygame.font.Font(None, 32)  # Font for dialogue text
        name_font = pygame.font.Font(None, 36)  # Font for character names
        space_prompt_font = pygame.font.Font(None, 28)  # Font for "Press SPACE to continue"

        current_line = 0
        text_displayed = ""
        text_index = 0
        text_speed = 2  # Speed of text animation
        audio_played = False  # Flag to track if audio has been played for the current line
        current_sound = None  # Track the currently playing sound

        running = True
        clock = pygame.time.Clock()

        while running:
            self.display.blit(self.background_image_2, (0, 0))

            # Create the dialogue box at the bottom
            dialogue_box = pygame.Surface((self.display.get_width(), dialogue_box_height))
            dialogue_box.fill((255, 219, 172))  # Light background for the dialogue box
            dialogue_box_rect = dialogue_box.get_rect(topleft=(0, self.display.get_height() - dialogue_box_height))

            # Draw the brown border around the dialogue box
            border_color = (139, 69, 19)  # Brown color (RGB)
            border_thickness = 20  # Thickness of the border
            pygame.draw.rect(self.display, border_color, dialogue_box_rect.inflate(border_thickness, border_thickness),
                             border_thickness)

            # Get the current dialogue data
            current_dialogue = dialogue_data[current_line]
            character_name = current_dialogue["name"]
            character_text = current_dialogue["text"]
            antagonist = "Magical Owl"

            # Play the audio file if it exists and hasn't been played yet
            if "audio" in current_dialogue and not audio_played:
                audio_file = current_dialogue["audio"]
                if current_sound is not None:
                    current_sound.stop()  # Stop the currently playing sound if it exists
                current_sound = audio_files[audio_file]  # Get the new sound
                current_sound.play()  # Play the new audio
                audio_played = True  # Set the flag to True to prevent replaying the audio

            # Update owl animation (cycle through the frames)
            if character_name == antagonist or character_name == "Lexi the Owl":
                owl_frame_index = (owl_frame_index + 1) % (len(owl_frames) * owl_animation_speed)
                current_owl_frame = owl_frames[owl_frame_index // owl_animation_speed]
                self.display.blit(current_owl_frame, (950, self.display.get_height() - dialogue_box_height - 300))

            # Render the character image (player) if it's the player's turn
            else:
                self.display.blit(char1_image, (50, self.display.get_height() - dialogue_box_height - 200))

            # Render the character name inside the dialogue box (above the text)
            name_surface = name_font.render(character_name, True, BLACK)
            dialogue_box.blit(name_surface, (20, 10))  # Draw name near the top inside the dialogue box

            # Text animation (add one letter at a time)
            if text_index < len(character_text):
                text_index += text_speed  # Control how fast letters are added
                text_displayed = character_text[:text_index]
            else:
                text_displayed = character_text

            # Render the dialogue text below the name
            text_surface = dialogue_font.render(text_displayed, True, BLACK)
            dialogue_box.blit(text_surface, (20, 60))  # Draw the text inside the dialogue box below the name

            # Add "Press SPACE to continue." prompt at the bottom right
            if text_index >= len(character_text):  # Show prompt only if the text is fully displayed
                space_prompt_surface = space_prompt_font.render("Press SPACE to continue.", True, (100, 100, 100))
                dialogue_box.blit(space_prompt_surface,
                                  (dialogue_box.get_width() - space_prompt_surface.get_width() - 20,
                                   dialogue_box.get_height() - space_prompt_surface.get_height() - 10))

            # Draw the dialogue box on the screen with the brown border
            self.display.blit(dialogue_box, dialogue_box_rect.topleft)

            # Event handling for advancing the dialogue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:  # Only proceed on SPACE key
                        if text_index >= len(character_text):
                            # Move to the next line of dialogue if the text is fully displayed
                            current_line += 1
                            text_index = 0
                            text_displayed = ""
                            audio_played = False  # Reset the audio flag for the next line
                            if current_line >= len(dialogue_data):
                                running = False  # Exit dialogue when all lines are done

            pygame.display.flip()
            clock.tick(60)  # Control the frame rate

    def run_dialogue_strip_2(self):
        self.dialogue_font = pygame.font.Font(None, 36)

        # Dialogue list (narrating the FourthLevel)
        self.dialogue_lines = [
            "The adventurer and Lexi starts walking as they make their way to their next place.",
            "During the walk, they start talking about each other.",
            "As they share more about themselves, their friendship starts to blossom.",
            "After an hour, they could already see the erupting volcano from afar.",
            "Finally, they made their way to the entrance of the volcano.",
            "As they enter, they were welcomed by burning lava and the hot steam surrounding the volcano."
        ]

        # Corresponding images for each dialogue line
        self.dialogue_images = [
            pygame.image.load(os.path.join('graphics', 'travel-to-lava-rush-1.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'travel-to-lava-rush-3.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'travel-to-lava-rush-3.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'travel-to-lava-rush-2.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'travel-to-lava-rush-2.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'travel-to-lava-rush-4.png')).convert_alpha()
        ]

        # Corresponding narration files for each dialogue line
        self.dialogue_sounds = [
            pygame.mixer.Sound(os.path.join('audio', 'second-narrator-1.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'second-narrator-2.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'second-narrator-3.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'second-narrator-4.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'second-narrator-5.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'second-narrator-6.mp3'))
        ]

        # Scale the images to fit the screen
        self.dialogue_images = [
            pygame.transform.scale(img, (self.display.get_width(), self.display.get_height()-150)) for img in
            self.dialogue_images
        ]

        self.dialogue_index = 0
        running = True

        # Initialize the mixer for playing audio
        pygame.mixer.init()

        # Flag to check if narration is playing
        self.narration_playing = False

        def play_narration():
            """Play the narration for the current dialogue line."""
            self.narration_playing = True
            self.dialogue_sounds[self.dialogue_index].play()
            pygame.time.set_timer(pygame.USEREVENT, int(self.dialogue_sounds[self.dialogue_index].get_length() * 1000))

        # Play the first narration automatically
        play_narration()

        while running:
            self.display.fill((0, 0, 0))  # Black background for the dialogue screen

            # Display the corresponding image
            self.display.blit(self.dialogue_images[self.dialogue_index], (0, 0))

            # Create and display the dialogue box
            dialogue_box_rect = pygame.Rect(0, self.display.get_height() - 150, self.display.get_width(), 150)
            pygame.draw.rect(self.display, (0, 0, 0), dialogue_box_rect)

            # Render the current dialogue line
            dialogue_text = self.dialogue_font.render(self.dialogue_lines[self.dialogue_index], True,
                                                      (255, 255, 255))  # White font
            dialogue_rect = dialogue_text.get_rect(
                center=(self.display.get_width() // 2, self.display.get_height() - 75))
            self.display.blit(dialogue_text, dialogue_rect)

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    sys.exit()

                # Allow the player to skip the narration and move to the next slide with the spacebar
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.dialogue_sounds[self.dialogue_index].stop()  # Stop the current narration
                        self.narration_playing = False
                        self.dialogue_index += 1
                        if self.dialogue_index >= len(self.dialogue_lines):
                            running = False  # End the dialogue and start the game
                        else:
                            play_narration()  # Play the next narration

                # Check if narration finished
                if event.type == pygame.USEREVENT and self.narration_playing:
                    self.narration_playing = False
                    self.dialogue_index += 1
                    if self.dialogue_index >= len(self.dialogue_lines):
                        running = False  # End the dialogue and start the game
                    else:
                        play_narration()  # Play the next narration

            pygame.display.update()

    def run_dialogue_strip_3(self):
        # Initialize pygame's mixer for audio (if needed)
        pygame.mixer.init()

        # Load the owl sprite sheet and extract frames for animation
        owl_frames = self.load_spritesheet('owl-flying.png', 48, 48, scale_factor=6)
        owl_frame_index = 0  # Start with the first frame of the animation
        owl_animation_speed = 5  # Change the frame every 5 frames of the game loop

        # Load character images (only one image for the player)
        char1_image = pygame.image.load(os.path.join('graphics', 'character-avatar.png'))
        char1_image = pygame.transform.scale(char1_image, (200, 200))

        dialogue_data = [
            {"name": "Lexi the Owl", "text": "Here we are inside the volcano. It sure is hot in here.", "audio": "owl-talking-19.mp3"},
            {"name": "Lexi the Owl", "text": "We need to cross this scorching lava until we reach the EXIT.", "audio": "owl-talking-20.mp3"},
            {"name": "Lexi the Owl", "text": "There are PUZZLES that we may encounter along our path.", "audio": "owl-talking-21.mp3"},
            {"name": "You", "text": "Wews! This is my first time inside a volcano. I feel like i could pass out.", "image": char1_image},
            {"name": "Lexi the Owl", "text": "Me, too! And the only way we can survive this is to complete all its PUZZLES.", "audio": "owl-talking-22.mp3"},
            {"name": "Lexi the Owl", "text": "Are you ready to go, adventurer?", "audio": "owl-talking-23.mp3"},
            {"name": "You", "text": "Bring it on! There's no turning back now.", "image": char1_image},
        ]

        # Preload audio files
        audio_files = {}
        for dialogue in dialogue_data:
            if "audio" in dialogue:
                audio_file = dialogue["audio"]
                audio_files[audio_file] = pygame.mixer.Sound(os.path.join("audio", audio_file))

        dialogue_box_height = 150  # Height of the dialogue box surface
        dialogue_font = pygame.font.Font(None, 32)  # Font for dialogue text
        name_font = pygame.font.Font(None, 36)  # Font for character names
        space_prompt_font = pygame.font.Font(None, 28)  # Font for "Press SPACE to continue"

        current_line = 0
        text_displayed = ""
        text_index = 0
        text_speed = 2  # Speed of text animation
        audio_played = False  # Flag to track if audio has been played for the current line
        current_sound = None  # Track the currently playing sound

        running = True
        clock = pygame.time.Clock()

        while running:
            self.display.blit(self.background_image, (0, 0))

            # Create the dialogue box at the bottom
            dialogue_box = pygame.Surface((self.display.get_width(), dialogue_box_height))
            dialogue_box.fill((255, 219, 172))  # Light background for the dialogue box
            dialogue_box_rect = dialogue_box.get_rect(topleft=(0, self.display.get_height() - dialogue_box_height))

            # Draw the brown border around the dialogue box
            border_color = (139, 69, 19)  # Brown color (RGB)
            border_thickness = 20  # Thickness of the border
            pygame.draw.rect(self.display, border_color, dialogue_box_rect.inflate(border_thickness, border_thickness),
                             border_thickness)

            # Get the current dialogue data
            current_dialogue = dialogue_data[current_line]
            character_name = current_dialogue["name"]
            character_text = current_dialogue["text"]
            antagonist = "Magical Owl"

            # Play the audio file if it exists and hasn't been played yet
            if "audio" in current_dialogue and not audio_played:
                audio_file = current_dialogue["audio"]
                if current_sound is not None:
                    current_sound.stop()  # Stop the currently playing sound if it exists
                current_sound = audio_files[audio_file]  # Get the new sound
                current_sound.play()  # Play the new audio
                audio_played = True  # Set the flag to True to prevent replaying the audio

            # Update owl animation (cycle through the frames)
            if character_name == antagonist or character_name == "Lexi the Owl":
                owl_frame_index = (owl_frame_index + 1) % (len(owl_frames) * owl_animation_speed)
                current_owl_frame = owl_frames[owl_frame_index // owl_animation_speed]
                self.display.blit(current_owl_frame, (950, self.display.get_height() - dialogue_box_height - 300))

            # Render the character image (player) if it's the player's turn
            else:
                self.display.blit(char1_image, (50, self.display.get_height() - dialogue_box_height - 200))

            # Render the character name inside the dialogue box (above the text)
            name_surface = name_font.render(character_name, True, BLACK)
            dialogue_box.blit(name_surface, (20, 10))  # Draw name near the top inside the dialogue box

            # Text animation (add one letter at a time)
            if text_index < len(character_text):
                text_index += text_speed  # Control how fast letters are added
                text_displayed = character_text[:text_index]
            else:
                text_displayed = character_text

            # Render the dialogue text below the name
            text_surface = dialogue_font.render(text_displayed, True, BLACK)
            dialogue_box.blit(text_surface, (20, 60))  # Draw the text inside the dialogue box below the name

            # Add "Press SPACE to continue." prompt at the bottom right
            if text_index >= len(character_text):  # Show prompt only if the text is fully displayed
                space_prompt_surface = space_prompt_font.render("Press SPACE to continue.", True, (100, 100, 100))
                dialogue_box.blit(space_prompt_surface,
                                  (dialogue_box.get_width() - space_prompt_surface.get_width() - 20,
                                   dialogue_box.get_height() - space_prompt_surface.get_height() - 10))

            # Draw the dialogue box on the screen with the brown border
            self.display.blit(dialogue_box, dialogue_box_rect.topleft)

            # Event handling for advancing the dialogue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:  # Only proceed on SPACE key
                        if text_index >= len(character_text):
                            # Move to the next line of dialogue if the text is fully displayed
                            current_line += 1
                            text_index = 0
                            text_displayed = ""
                            audio_played = False  # Reset the audio flag for the next line
                            if current_line >= len(dialogue_data):
                                running = False  # Exit dialogue when all lines are done

            pygame.display.flip()
            clock.tick(60)  # Control the frame rate

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
                            self.gameStateManager.set_state('third-level')
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

    def show_how_to_play(self):
        """Displays the 'how to play' instructions with a start button."""
        # Load the how-to-play image and scale it
        how_to_play_image = pygame.image.load(os.path.join('graphics', 'how-to-play(lava-rush).png')).convert_alpha()
        how_to_play_image = pygame.transform.scale(how_to_play_image, (1280, 720))  # Scale to 1280x720

        # Define the start button
        start_button_rect = pygame.Rect((self.display.get_width() // 2 - 100, 600), (200, 50))  # Centered button

        # Define colors
        normal_color = (255, 255, 0)  # Yellow
        hover_color = (200, 200, 0)  # Darker yellow

        running = True
        while running:
            self.display.fill((0, 0, 0))  # Fill the screen with black
            self.display.blit(how_to_play_image, (0, 0))  # Display the how-to-play image

            # Check if the mouse is over the button
            mouse_pos = pygame.mouse.get_pos()
            if start_button_rect.collidepoint(mouse_pos):
                button_color = hover_color  # Change to darker yellow on hover
            else:
                button_color = normal_color  # Normal yellow color

            # Draw the start button
            pygame.draw.rect(self.display, button_color, start_button_rect)  # Draw button with the appropriate color
            start_text = self.font.render("Start", True, (0, 0, 0))  # Black text
            start_text_rect = start_text.get_rect(center=start_button_rect.center)  # Center text in button
            self.display.blit(start_text, start_text_rect)  # Blit start text

            # Event handling for button click
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if start_button_rect.collidepoint(event.pos):  # Check if mouse is over the button
                        running = False  # Exit the loop to proceed to the next screen

            pygame.display.update()

    def start_countdown(self):
        """Displays a 3-2-1 countdown before the game starts."""
        for count in range(3, 0, -1):
            self.display.fill((0, 0, 0))  # Black background
            countdown_surface = self.countdown_font.render(str(count), True, (255, 255, 255))  # White countdown number
            self.display.blit(countdown_surface, (self.display.get_width() // 2 - countdown_surface.get_width() // 2,
                                                  self.display.get_height() // 2 - countdown_surface.get_height() // 2))
            pygame.display.update()
            pygame.time.wait(1000)  # Wait 1 second for each countdown step

        pass

    def restart_level(self):
        """Reset the level and restart."""
        self.lives = 3  # Reset lives
        self.correct_answers_count = 0  # Reset correct answers count
        self.current_syllable_selection = []  # Reset syllable selection
        self.is_restart = True
        self.load_new_word()  # Load a new word

    def run(self):
        if not self.is_restart:
            self.run_dialogue_strip_1()
            self.run_title_screen()
            self.run_dialogue_strip_2()
            self.run_dialogue_strip_3()
        else:
            self.is_restart = False
        self.show_how_to_play()
        self.start_countdown()
        self.start_time = time.time()  # Start the timer immediately after the title animation
        running = True
        while running:
            elapsed_time = time.time() - self.start_time
            remaining_time = max(0.0, self.lava_flow_time_limit - elapsed_time)

            # Calculate minutes and seconds
            minutes = int(remaining_time // 60)
            seconds = int(remaining_time % 60)

            self.display.blit(self.background_image, (0, 0))

            # Render the message text
            message_text = self.font.render("Segment the syllables of this word:", True, (255, 255, 255))
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

            # Check if mouse is hovering over the buttons
            mouse_pos = pygame.mouse.get_pos()
            submit_button_color = (254, 223, 0) if not self.submit_button_rect.collidepoint(mouse_pos) else (
            200, 200, 0)
            reset_button_color = (254, 223, 0) if not self.reset_button_rect.collidepoint(mouse_pos) else (200, 200, 0)

            pygame.draw.rect(self.display, submit_button_color, self.submit_button_rect)
            pygame.draw.rect(self.display, reset_button_color, self.reset_button_rect)

            submit_button_text = self.button_font.render("SUBMIT", True, (0, 0, 0))
            reset_button_text = self.button_font.render("RESET", True, (0, 0, 0))

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

class SylleLagoon:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager
        self.lives = 3
        self.timer = 10.0  # 15 seconds timer for each word
        self.win = False
        self.is_restart = False
        self.countdown_font = pygame.font.Font(None, 100)
        self.font = pygame.font.SysFont('Arial', 36)
        self.words = [
            {"word": "TIGER",
             "question": "If you know this word, what is its last syllable?",
             "syllables": ["-ger", "-ny", "-dy", "-red"],
             "correct": "-ger",
             "image": "graphics/tiger.png"},
            {"word": "RABBIT",
             "question": "If you know this word, what is its last syllable?",
             "syllables": ["-ber", "-tion", "-er", "-bit"],
             "correct": "-bit",
             "image": "graphics/rabbit.png"},
            {"word": "RAINBOW",
             "question": "If you know this word, what is its last syllable?",
             "syllables": ["-drop", "-ing", "-bow", "-fall"],
             "correct": "-bow",
             "image": "graphics/rainbow.png"},
            {"word": "PIZZA",
             "question": "If you know this word, what is its last syllable?",
             "syllables": ["-ture", "-za", "-zer", "-tion"],
             "correct": "-za",
             "image": "graphics/pizza.png"},
            {"word": "ROCKET",
             "question": "If you know this word, what is its last syllable?",
             "syllables": ["-et", "-er", "-fall", "-hard"],
             "correct": "-et",
             "image": "graphics/rocket.png"},
            {"word": "FLOWER",
             "question": "If you know this word, what is its last syllable?",
             "syllables": ["-ing", "-wer", "-state", "-s"],
             "correct": "-wer",
             "image": "graphics/flower.png"},
            {"word": "CHICKEN",
             "question": "If you know this word, what is its last syllable?",
             "syllables": ["-ing", "-er", "-tion", "-en"],
             "correct": "-en",
             "image": "graphics/chicken.png"},
            {"word": "WINDOW",
             "question": "If you know this word, what is its last syllable?",
             "syllables": ["-ning", "-dow", "-ner", "-some"],
             "correct": "-dow",
             "image": "graphics/window.png"},
            {"word": "TABLE",
             "question": "If you know this word, what is its last syllable?",
             "syllables": ["-e", "-nned", "-ble", "-er"],
             "correct": "-ble",
             "image": "graphics/table.png"},
            {"word": "CACTUS",
             "question": "If you know this word, what is its last syllable?",
             "syllables": ["-tus", "-kled", "-tie", "-ing"],
             "correct": "-tus",
             "image": "graphics/cactus.png"},
        ]

        self.current_word_index = 0
        self.correct_syllable = None
        self.start_time = None
        self.selected_syllable = None
        self.geyser_positions = self.get_geyser_positions()

        background_image_path = os.path.join('graphics', 'third-level-bg.png')
        self.background_image = pygame.image.load(background_image_path).convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image,(self.display.get_width(), self.display.get_height()))

        background_image_path_2 = os.path.join('graphics', 'sylle-lagoon-topview.png')
        self.background_image_2 = pygame.image.load(background_image_path_2).convert_alpha()
        self.background_image_2 = pygame.transform.scale(self.background_image_2,
                                                       (self.display.get_width(), self.display.get_height()))

        # Load the heart image for lives representation
        self.heart_image = pygame.image.load(os.path.join('graphics', 'heart.png')).convert_alpha()
        self.heart_image = pygame.transform.scale(self.heart_image, (80, 50))  # Scale the heart image if needed
        self.heart_width, self.heart_height = self.heart_image.get_size()

        # Idle and running animation variables
        self.idle_sprite_sheet = self.load_sprite_sheet('graphics/idle.png', 48, 48)
        self.run_sprite_sheet = self.load_sprite_sheet('graphics/Run.png', 48, 48)
        print(f"Loaded {len(self.run_sprite_sheet)} frames for running animation")
        self.current_frame = 0
        self.animation_speed = 0.1
        self.moving = False
        self.target_position = None

        # Character position
        self.character_x = self.display.get_width() // 2 - 48 // 2  # Center position
        self.character_y = self.display.get_height() - 48 - 100  # Position below the geysers

        self.last_update_time = time.time()

    def run_title_screen(self):
        title_text = "SYLLE LAGOON"
        font_path_1 = os.path.join('fonts', 'ARIALBLACKITALIC.TTF')
        font_path_2 = os.path.join('fonts', 'ARIAL.TTF')
        title_font = pygame.font.Font(font_path_1, 50)  # Large font for the title
        button_font = pygame.font.Font(font_path_2, 20)

        button_color = (255, 255, 0)  # Yellow color for the button
        button_hover_color = (200, 200, 0)  # Darker yellow for hover effect
        button_rect = pygame.Rect((self.display.get_width() // 2 - 100, self.display.get_height() // 2 + 50),
                                  (200, 50))  # Button dimensions

        running = True
        while running:
            self.display.fill((0, 0, 0))  # Fill the screen with black

            # Render the title text
            title_surface = title_font.render(title_text, True, (255, 255, 255))  # White color for the title
            title_rect = title_surface.get_rect(
                center=(self.display.get_width() // 2, self.display.get_height() // 2 - 50))
            self.display.blit(title_surface, title_rect)  # Blit title text

            # Check if the mouse is over the button
            mouse_pos = pygame.mouse.get_pos()  # Get the mouse position
            if button_rect.collidepoint(mouse_pos):
                current_button_color = button_hover_color  # Use hover color
            else:
                current_button_color = button_color  # Use normal color

            # Draw the button with the current color
            pygame.draw.rect(self.display, current_button_color, button_rect)  # Draw button
            button_text = button_font.render("Continue", True, (0, 0, 0))  # Black text for the button
            button_text_rect = button_text.get_rect(center=button_rect.center)  # Center text in button
            self.display.blit(button_text, button_text_rect)  # Blit button text

            # Event handling for button click
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        if button_rect.collidepoint(mouse_pos):  # Check if mouse is over the button
                            running = False  # Exit the loop to move to the next screen

            pygame.display.flip()
            pygame.time.Clock().tick(60)  # Control the frame rate

    def run_dialogue_strip_1(self):
        self.dialogue_font = pygame.font.Font(None, 36)

        # Dialogue list (narrating the FourthLevel)
        self.dialogue_lines = [
            "After they passed the scorching trials of the volcano, they went on their way to continue their journey.",
            "Not long after, they reached a glistening lagoon not far from the volcano.",
            "Lexi the owl noticed a signage near the lagoon and scanned it.",
            "It contains pictures, but there are no sorts of words to tell them what could they all mean.",
            "In a matter of seconds, they noticed the footholds in the lake started to open one by one.",
            "Traveler caught a glimpse of sea monsters awaiting for them to fall down into those waters.",
            "Without a warning, another trial for them began."
        ]

        # Corresponding images for each dialogue line
        self.dialogue_images = [
            pygame.image.load(os.path.join('graphics', 'to-sylle-laggoon-1.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'to-sylle-laggoon-2.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'to-sylle-laggoon-3.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'to-sylle-laggoon-3.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'to-sylle-laggoon-4.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'to-sylle-laggoon-5.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'to-sylle-laggoon-5.png')).convert_alpha(),

        ]

        # Corresponding narration files for each dialogue line
        self.dialogue_sounds = [
            pygame.mixer.Sound(os.path.join('audio', 'third-narrator-1.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'third-narrator-2.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'third-narrator-3.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'third-narrator-4.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'third-narrator-5.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'third-narrator-6.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'third-narrator-7.mp3')),
        ]

        # Scale the images to fit the screen
        self.dialogue_images = [
            pygame.transform.scale(img, (self.display.get_width(), self.display.get_height()-150)) for img in
            self.dialogue_images
        ]

        self.dialogue_index = 0
        running = True

        # Initialize the mixer for playing audio
        pygame.mixer.init()

        # Flag to check if narration is playing
        self.narration_playing = False

        def play_narration():
            """Play the narration for the current dialogue line."""
            self.narration_playing = True
            self.dialogue_sounds[self.dialogue_index].play()
            pygame.time.set_timer(pygame.USEREVENT, int(self.dialogue_sounds[self.dialogue_index].get_length() * 1000))

        # Play the first narration automatically
        play_narration()

        while running:
            self.display.fill((0, 0, 0))  # Black background for the dialogue screen

            # Display the corresponding image
            self.display.blit(self.dialogue_images[self.dialogue_index], (0, 0))

            # Create and display the dialogue box
            dialogue_box_rect = pygame.Rect(0, self.display.get_height() - 150, self.display.get_width(), 150)
            pygame.draw.rect(self.display, (0, 0, 0), dialogue_box_rect)

            # Render the current dialogue line
            dialogue_text = self.dialogue_font.render(self.dialogue_lines[self.dialogue_index], True,
                                                      (255, 255, 255))  # White font
            dialogue_rect = dialogue_text.get_rect(
                center=(self.display.get_width() // 2, self.display.get_height() - 75))
            self.display.blit(dialogue_text, dialogue_rect)

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    sys.exit()

                # Allow the player to skip the narration and move to the next slide with the spacebar
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.dialogue_sounds[self.dialogue_index].stop()  # Stop the current narration
                        self.narration_playing = False
                        self.dialogue_index += 1
                        if self.dialogue_index >= len(self.dialogue_lines):
                            running = False  # End the dialogue and start the game
                        else:
                            play_narration()  # Play the next narration

                # Check if narration finished
                if event.type == pygame.USEREVENT and self.narration_playing:
                    self.narration_playing = False
                    self.dialogue_index += 1
                    if self.dialogue_index >= len(self.dialogue_lines):
                        running = False  # End the dialogue and start the game
                    else:
                        play_narration()  # Play the next narration

            pygame.display.update()

    def load_spritesheet(self,filename, frame_width, frame_height, scale_factor):
        # Load the sprite sheet image
        spritesheet = pygame.image.load(os.path.join('graphics', filename)).convert_alpha()
        # Get the width and height of the entire sprite sheet
        sheet_width, sheet_height = spritesheet.get_size()

        # Create a list to hold individual frames
        frames = []
        for y in range(0, sheet_height, frame_height):
            for x in range(0, sheet_width, frame_width):
                # Extract each frame by using a sub-surface
                frame = spritesheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
                # Scale the frame to make it larger
                scaled_frame = pygame.transform.scale(frame, (
                int(frame_width * scale_factor), int(frame_height * scale_factor)))
                frames.append(scaled_frame)

        return frames

    def run_dialogue_strip_2(self):
        # Initialize pygame's mixer for audio (if needed)
        pygame.mixer.init()

        # Load the owl sprite sheet and extract frames for animation
        owl_frames = self.load_spritesheet('owl-flying.png', 48, 48, scale_factor=6)
        owl_frame_index = 0  # Start with the first frame of the animation
        owl_animation_speed = 5  # Change the frame every 5 frames of the game loop

        # Load character images (only one image for the player)
        char1_image = pygame.image.load(os.path.join('graphics', 'character-avatar.png'))
        char1_image = pygame.transform.scale(char1_image, (200, 200))

        dialogue_data = [
            {"name": "Lexi the Owl", "text": "We cant just swim to this lagoon because piranhas and other sea monsters\n will eat us alive.", "audio": "owl-talking-24.mp3"},
            {"name": "Lexi the Owl", "text": "And it seems like we can't go around the lagoon either since we will get\n caught up by the burning forest.", "audio": "owl-talking-25.mp3"},
            {"name": "You", "text": "I think I got it, Lexi! The only way we can get across this water is to step through this footholes.", "image": char1_image},
            {"name": "You", "text": "Every foothole has a time interval before they open, and some dont even open at all. We need to take advantage of that.", "image": char1_image},
            {"name": "Lexi the Owl", "text": "Wow, adventurer! You really are observant!", "audio": "owl-talking-26.mp3"},
            {"name": "Lexi the Owl", "text": "So we just need to step onto the foothole that doesnt open at all?", "audio": "owl-talking-27.mp3"},
            {"name": "You", "text": "Correct! Lets go!", "image": char1_image},
        ]

        # Preload audio files
        audio_files = {}
        for dialogue in dialogue_data:
            if "audio" in dialogue:
                audio_file = dialogue["audio"]
                audio_files[audio_file] = pygame.mixer.Sound(os.path.join("audio", audio_file))

        dialogue_box_height = 150  # Height of the dialogue box surface
        dialogue_font = pygame.font.Font(None, 32)  # Font for dialogue text
        name_font = pygame.font.Font(None, 36)  # Font for character names
        space_prompt_font = pygame.font.Font(None, 28)  # Font for "Press SPACE to continue"

        current_line = 0
        text_displayed = ""
        text_index = 0
        text_speed = 2  # Speed of text animation
        audio_played = False  # Flag to track if audio has been played for the current line
        current_sound = None  # Track the currently playing sound

        running = True
        clock = pygame.time.Clock()

        while running:
            self.display.blit(self.background_image_2, (0, 0))

            # Create the dialogue box at the bottom
            dialogue_box = pygame.Surface((self.display.get_width(), dialogue_box_height))
            dialogue_box.fill((255, 219, 172))  # Light background for the dialogue box
            dialogue_box_rect = dialogue_box.get_rect(topleft=(0, self.display.get_height() - dialogue_box_height))

            # Draw the brown border around the dialogue box
            border_color = (139, 69, 19)  # Brown color (RGB)
            border_thickness = 20  # Thickness of the border
            pygame.draw.rect(self.display, border_color, dialogue_box_rect.inflate(border_thickness, border_thickness),
                             border_thickness)

            # Get the current dialogue data
            current_dialogue = dialogue_data[current_line]
            character_name = current_dialogue["name"]
            character_text = current_dialogue["text"]
            antagonist = "Magical Owl"

            # Play the audio file if it exists and hasn't been played yet
            if "audio" in current_dialogue and not audio_played:
                audio_file = current_dialogue["audio"]
                if current_sound is not None:
                    current_sound.stop()  # Stop the currently playing sound if it exists
                current_sound = audio_files[audio_file]  # Get the new sound
                current_sound.play()  # Play the new audio
                audio_played = True  # Set the flag to True to prevent replaying the audio

            # Update owl animation (cycle through the frames)
            if character_name == antagonist or character_name == "Lexi the Owl":
                owl_frame_index = (owl_frame_index + 1) % (len(owl_frames) * owl_animation_speed)
                current_owl_frame = owl_frames[owl_frame_index // owl_animation_speed]
                self.display.blit(current_owl_frame, (950, self.display.get_height() - dialogue_box_height - 300))

            # Render the character image (player) if it's the player's turn
            else:
                self.display.blit(char1_image, (50, self.display.get_height() - dialogue_box_height - 200))

            # Render the character name inside the dialogue box (above the text)
            name_surface = name_font.render(character_name, True, BLACK)
            dialogue_box.blit(name_surface, (20, 10))  # Draw name near the top inside the dialogue box

            # Text animation (add one letter at a time)
            if text_index < len(character_text):
                text_index += text_speed  # Control how fast letters are added
                text_displayed = character_text[:text_index]
            else:
                text_displayed = character_text

            # Render the dialogue text below the name
            text_surface = dialogue_font.render(text_displayed, True, BLACK)
            dialogue_box.blit(text_surface, (20, 60))  # Draw the text inside the dialogue box below the name

            # Add "Press SPACE to continue." prompt at the bottom right
            if text_index >= len(character_text):  # Show prompt only if the text is fully displayed
                space_prompt_surface = space_prompt_font.render("Press SPACE to continue.", True, (100, 100, 100))
                dialogue_box.blit(space_prompt_surface,
                                  (dialogue_box.get_width() - space_prompt_surface.get_width() - 20,
                                   dialogue_box.get_height() - space_prompt_surface.get_height() - 10))

            # Draw the dialogue box on the screen with the brown border
            self.display.blit(dialogue_box, dialogue_box_rect.topleft)

            # Event handling for advancing the dialogue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:  # Only proceed on SPACE key
                        if text_index >= len(character_text):
                            # Move to the next line of dialogue if the text is fully displayed
                            current_line += 1
                            text_index = 0
                            text_displayed = ""
                            audio_played = False  # Reset the audio flag for the next line
                            if current_line >= len(dialogue_data):
                                running = False  # Exit dialogue when all lines are done

            pygame.display.flip()
            clock.tick(60)  # Control the frame rate

    def load_sprite_sheet(self, path, sprite_width, sprite_height):
        """Loads a sprite sheet and returns a list of individual frames."""
        sheet = pygame.image.load(path).convert_alpha()
        sheet_width, sheet_height = sheet.get_size()
        frames = []
        for y in range(0, sheet_height, sprite_height):
            for x in range(0, sheet_width, sprite_width):
                frame = sheet.subsurface((x, y, sprite_width, sprite_height))
                frames.append(frame)
        print(f"Loaded {len(frames)} frames from {path}")  # Debug print
        return frames

    def animate_character(self, frames):
        """Handles animation by cycling through frames."""
        current_time = time.time()
        if current_time - self.last_update_time > self.animation_speed:
            self.current_frame = (self.current_frame + 1) % len(frames)  # Cycle within bounds of frames list
            self.last_update_time = current_time
        return frames[self.current_frame]

    def draw_lives(self):
        """Draw the player's lives using heart images."""
        for i in range(self.lives):
            self.display.blit(self.heart_image, (10 + i * 60, 10))  # Adjust position as needed

    def move_character_toward_syllable(self):
        """Moves the character towards the selected syllable."""
        if self.moving and self.target_position:
            target_x, target_y = self.target_position
            dx = target_x - self.character_x
            if abs(dx) < 5:  # Close enough to stop
                self.character_x = target_x
                self.moving = False
            else:
                self.character_x += dx * 0.1  # Move smoothly
            # Align the character's Y position with the geyser
            self.character_y = target_y - 48  # Adjust so the character is inside the circle

    def draw_character(self):
        """Draw the current frame of the character animation, scaled larger."""
        if self.moving:
            character_frame = self.animate_character(self.run_sprite_sheet)
        else:
            character_frame = self.animate_character(self.idle_sprite_sheet)

        # Increase the scale factor to make the character larger
        scale_factor = 1.75  # Adjusted factor to increase the size
        scaled_width = int(character_frame.get_width() * scale_factor)
        scaled_height = int(character_frame.get_height() * scale_factor)
        scaled_character_frame = pygame.transform.scale(character_frame, (scaled_width, scaled_height))

        # Calculate the new position for the scaled character
        new_character_x = self.character_x + (scaled_width - character_frame.get_width()) // 2
        new_character_y = self.character_y + (scaled_height - character_frame.get_height()) // 2

        self.display.blit(scaled_character_frame, (new_character_x, new_character_y))

    def get_geyser_positions(self):
        """Returns the positions for the four geysers with decreased spacing."""
        screen_width, screen_height = self.display.get_size()
        y_position = screen_height // 2 + 75  # Fixed y-position for all geysers
        spacing = 150  # Adjust this value for desired spacing
        positions = [
            (screen_width // 4, y_position),
            (screen_width // 4 + 70 + spacing, y_position),  # Adjusting position based on radius and spacing
            (screen_width // 4 + 2 * (70 + spacing), y_position),
            (screen_width // 4 + 3 * (70 + spacing), y_position),
        ]
        return positions

    def load_next_word(self):
        """Loads the next word and syllables."""
        if self.current_word_index >= len(self.words):
            print("All words completed!")
            self.gameStateManager.set_state('next-level')  # Move to next level
            return

        word_data = self.words[self.current_word_index]
        self.correct_syllable = word_data['correct']
        self.syllables = word_data['syllables']
        self.selected_syllable = None
        self.start_time = time.time()  # Reset the timer

    def draw_geysers(self):
        """Draws the syllable geysers with their positions as slightly oval shapes."""
        radius_x = 150  # Horizontal radius for oval
        radius_y = 125  # Vertical radius for oval
        for i, syllable in enumerate(self.syllables):
            x, y = self.geyser_positions[i]

            # Draw the oval geyser
            pygame.draw.ellipse(self.display, (41, 108, 114), (x - radius_x // 2, y - radius_y // 2, radius_x, radius_y))

            # Draw syllable text in the center of the oval
            syllable_text = pygame.font.SysFont('Arial', 30).render(syllable, True, (255, 255, 255))
            syllable_rect = syllable_text.get_rect(center=(x, y))
            self.display.blit(syllable_text, syllable_rect)

    def check_geyser_selection(self, mouse_pos):
        """Check if the player clicked on a geyser."""
        for i, pos in enumerate(self.geyser_positions):
            x, y = pos
            if pygame.Rect(x - 50, y - 50, 100, 100).collidepoint(mouse_pos):
                self.selected_syllable = self.syllables[i]
                self.target_position = (x-70, y-25)  # Set both x and y target positions for character movement
                self.moving = True  # Start moving the character

    def reset_level(self):
        # Reset relevant attributes to restart the level
        self.lives = 3
        self.current_word_index = 0
        self.start_time = time.time()
        self.current_time = 10.0
        self.is_restart = True

    def show_end_screen(self):
        # Set up screen
        self.display.fill((0, 0, 0))  # Black background
        font = pygame.font.SysFont('Arial', 20)

        # Display message based on win or lose
        message_text = "You Win!" if self.win else "You Lose"
        message_surface = font.render(message_text, True, (255, 255, 255))
        message_rect = message_surface.get_rect(center=(self.display.get_width() // 2, self.display.get_height() // 3))
        self.display.blit(message_surface, message_rect)

        # Button setup
        button_font = pygame.font.SysFont('Arial', 30)

        # Restart Level button
        restart_text = button_font.render("Restart Level", True, (255, 255, 255))
        restart_button = pygame.Rect(self.display.get_width() // 2 - (250 // 2), self.display.get_height() // 2, 250, 50)
        restart_button.center = (self.display.get_width() // 2, 300)
        pygame.draw.rect(self.display, (0, 128, 0), restart_button)
        self.display.blit(restart_text, restart_text.get_rect(center=restart_button.center))

        # Main Menu button
        menu_text = button_font.render("Main Menu", True, (255, 255, 255))
        menu_button = pygame.Rect(self.display.get_width() // 2 - (250 // 2), self.display.get_height() // 2 + 70, 250, 50)
        menu_button.center = (self.display.get_width() // 2, 380)
        pygame.draw.rect(self.display, (128, 0, 0), menu_button)
        self.display.blit(menu_text, menu_text.get_rect(center=menu_button.center))

        # Next Level button (only show if player wins)
        if self.win:
            next_level_text = button_font.render("Next Level", True, (255, 255, 255))
            next_level_button = pygame.Rect(self.display.get_width() // 2 - (250 // 2), self.display.get_height() // 2 - 70, 250, 50)
            next_level_button.center = (self.display.get_width() // 2, 220)
            pygame.draw.rect(self.display, (0, 0, 255), next_level_button)
            self.display.blit(next_level_text, next_level_text.get_rect(center=next_level_button.center))

        pygame.display.flip()  # Update display

        # Button event loop within `show_end_screen`
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    # Check if Restart Level button is clicked
                    if restart_button.collidepoint(mouse_pos):
                        self.reset_level()  # Reset level logic
                        waiting = False
                        self.run()  # Restart level

                    # Check if Main Menu button is clicked
                    elif menu_button.collidepoint(mouse_pos):
                        self.gameStateManager.set_state('main-menu')
                        waiting = False

                    # Check if Next Level button is clicked (if player won)
                    elif self.win and next_level_button.collidepoint(mouse_pos):
                        self.gameStateManager.set_state('fourth-level')
                        waiting = False

    def show_how_to_play(self):
        """Displays the 'how to play' instructions with a start button."""
        # Load the how-to-play image and scale it
        how_to_play_image = pygame.image.load(os.path.join('graphics', 'how-to-play(sylle-lagoon).png')).convert_alpha()
        how_to_play_image = pygame.transform.scale(how_to_play_image, (1280, 720))  # Scale to 1280x720

        # Define the start button
        start_button_rect = pygame.Rect((self.display.get_width() // 2 - 100, 650), (200, 50))  # Centered button

        # Define colors
        normal_color = (255, 255, 0)  # Yellow
        hover_color = (200, 200, 0)  # Darker yellow

        running = True
        while running:
            self.display.fill((0, 0, 0))  # Fill the screen with black
            self.display.blit(how_to_play_image, (0, 0))  # Display the how-to-play image

            # Check if the mouse is over the button
            mouse_pos = pygame.mouse.get_pos()
            if start_button_rect.collidepoint(mouse_pos):
                button_color = hover_color  # Change to darker yellow on hover
            else:
                button_color = normal_color  # Normal yellow color

            # Draw the start button
            pygame.draw.rect(self.display, button_color, start_button_rect)  # Draw button with the appropriate color
            start_text = self.font.render("Start", True, (0, 0, 0))  # Black text
            start_text_rect = start_text.get_rect(center=start_button_rect.center)  # Center text in button
            self.display.blit(start_text, start_text_rect)  # Blit start text

            # Event handling for button click
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if start_button_rect.collidepoint(event.pos):  # Check if mouse is over the button
                        running = False  # Exit the loop to proceed to the next screen

            pygame.display.update()

    def start_countdown(self):
        """Displays a 3-2-1 countdown before the game starts."""
        for count in range(3, 0, -1):
            self.display.fill((0, 0, 0))  # Black background
            countdown_surface = self.countdown_font.render(str(count), True, (255, 255, 255))  # White countdown number
            self.display.blit(countdown_surface, (self.display.get_width() // 2 - countdown_surface.get_width() // 2,
                                                  self.display.get_height() // 2 - countdown_surface.get_height() // 2))
            pygame.display.update()
            pygame.time.wait(1000)  # Wait 1 second for each countdown step

        pass

    def run(self):
        if not self.is_restart:
            self.run_dialogue_strip_1()
            self.run_title_screen()
            self.run_dialogue_strip_2()
        else:
            self.is_restart = False
        self.show_how_to_play()
        self.start_countdown()
        running = True
        self.load_next_word()

        while running:
            elapsed_time = (time.time() - self.start_time)
            remaining_time = max(0.0, self.timer - elapsed_time)

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    self.check_geyser_selection(mouse_pos)

            # Fill the screen with the background color
            self.display.blit(self.background_image, (0, 0)) # Light blue lagoon color

            # Display the question
            current_word_data = self.words[self.current_word_index]
            word_text = pygame.font.SysFont('Arial', 40).render(f"{current_word_data['question']}", True,
                                                                (255, 255, 255))
            self.display.blit(word_text, (self.display.get_width() // 2 - word_text.get_width() // 2, 50))

            # Load and display the image below the question
            image = pygame.image.load(current_word_data['image'])
            scaled_image = pygame.transform.scale(image, (150, 150))
            image_rect = scaled_image.get_rect()
            image_x = self.display.get_width() // 2 - image_rect.width // 2
            image_y = 50 + word_text.get_height() + 10  # 10 pixels below the question
            self.display.blit(scaled_image, (image_x, image_y))

            # Draw the geysers with syllables
            self.draw_geysers()

            # Move the character toward the selected syllable (if any)
            self.move_character_toward_syllable()

            # Draw the character animation
            self.draw_character()

            self.draw_lives()

            # Format the timer to display as 0:01 secs
            minutes = int(remaining_time // 60)
            seconds = int(remaining_time % 60)
            timer_text = f"Timer: {minutes}:{seconds:02}"  # Ensure seconds are always two digits
            timer_surface = pygame.font.SysFont('Arial', 40).render(timer_text, True, (255, 255, 255))
            # Display timer below lives
            self.display.blit(timer_surface, (10, 50 + self.heart_height + 5))  # Adjust position as needed

            # Check if the timer has run out
            if remaining_time <= 0:
                print("Time's up! Checking answer...")
                if self.selected_syllable == self.correct_syllable:
                    print("Correct! Moving to next word.")
                    self.current_word_index += 1
                    if self.current_word_index >= len(self.words):
                        print("All words completed!")
                        self.win = True
                        self.show_end_screen()
                        running = False
                    else:
                        self.load_next_word()

                else:
                    print("Incorrect! You lose a life.")
                    self.lives -= 1
                    if self.lives <= 0:
                        print("Game Over")
                        self.win = False
                        self.show_end_screen()
                        running = False
                    else:
                        print("Resetting timer for the same word.")
                        self.start_time = time.time()  # Reset timer for the same word
                        self.selected_syllable = None  # Reset selected syllable

            pygame.display.update()
            pygame.time.Clock().tick(60)

class TheBrokenBridge:
        def __init__(self, display, gameStateManager):
            self.display = display
            self.gameStateManager = gameStateManager
            self.screen_width, self.screen_height = self.display.get_size()  # Get screen size for responsiveness
            self.countdown_font = pygame.font.Font(None, 100)
            ladder_x_ratio = 0.435
            ladder_y_start_ratio = 0.03
            ladder_y_spacing_ratio = 0.131

            draggable_x_start_ratio = 0.15
            draggable_y_ratio = 0.72
            draggable_x_spacing_ratio = 0.152

            green_platform_path = os.path.join('graphics', 'First-Level-Platform.png')
            self.green_platform = pygame.image.load(green_platform_path).convert_alpha()

            bottom_platform_path = os.path.join('graphics', 'First-Level-Bottom-Platform.png')
            self.bottom_platform = pygame.image.load(bottom_platform_path).convert_alpha()

            # Ladder slots for words
            self.ladder_slots = [
                {"word": "", "rect": pygame.Rect(int(self.screen_width * ladder_x_ratio), int(self.screen_height * (
                        ladder_y_start_ratio + i * ladder_y_spacing_ratio)), 175, 30),
                 "correct_word": correct_word, "occupied": False, "color": (251, 242, 54), "pair_word": pair_word}
                # Added "pair_word"
                for i, (correct_word, pair_word) in enumerate([
                    ("BOAT", "GOAT"), ("DOG", "HOG"), ("CROWN", "DROWN"), ("BALL", "FALL"), ("CAT", "BAT")
                ])
            ]

            # Draggable images (replacing draggable words)
            self.draggable_images = [
                {"word": word,
                 "image": pygame.image.load(os.path.join('graphics', f'{word.lower()}.png')).convert_alpha(),
                 "rect": pygame.Rect(int(self.screen_width * (draggable_x_start_ratio + i * draggable_x_spacing_ratio)),
                                     int(self.screen_height * draggable_y_ratio), 150, 80),
                 "dragging": False,
                 "original_pos": (int(self.screen_width * (draggable_x_start_ratio + i * draggable_x_spacing_ratio)),
                                  int(self.screen_height * draggable_y_ratio)),
                 "placed": False}
                for i, word in enumerate(["CAT", "CROWN", "BALL", "BOAT", "DOG"])
            ]

            # Scale the images to fit within the draggable area
            for image_data in self.draggable_images:
                image_data["image"] = pygame.transform.scale(image_data["image"], (100, 100))

            # Load ladder (bridge) and heart images
            self.ladder_image = pygame.image.load(os.path.join('graphics', 'ladder-1.png')).convert_alpha()
            self.heart_image = pygame.image.load(os.path.join('graphics', 'heart.png')).convert_alpha()
            self.heart_image = pygame.transform.scale(self.heart_image, (80, 50))

            self.ladder_image = pygame.transform.scale(self.ladder_image,(int(self.screen_width * 0.5), int(self.screen_height * 0.7)))

            # Game variables
            self.lives = 3
            self.selected_word = None
            self.offset_x = 0
            self.offset_y = 0

            # Game state variables
            self.game_over = False
            self.win = False
            self.is_restart = False

            # Load the Arial font
            font_path = os.path.join('fonts', 'ARIAL.TTF')
            self.font = pygame.font.Font(font_path, 20)

            # Initialize the Text-to-Speech engine
            self.tts_engine = pyttsx3.init()

            # Load the speaker icon for TTS
            self.speaker_icon = pygame.image.load(os.path.join('graphics', 'audio-logo.png')).convert_alpha()
            self.speaker_icon = pygame.transform.scale(self.speaker_icon, (30, 30))  # Resize speaker icon

            # Track dialogue playback
            self.dialogue_played = False

        def draw_hearts(self):
            for i in range(self.lives):
                self.display.blit(self.heart_image, (10 + i * 60, 10))

        def speak_word(self, word):
            """Pronounce the word using Text-to-Speech (TTS)."""
            self.tts_engine.say(word)
            self.tts_engine.runAndWait()

        def show_end_screen(self):
            self.display.blit(self.bottom_platform, (0, 0))  # Draw the bottom platform
            self.display.blit(self.green_platform, (0, 320))  # Draw the green platform
            self.display.blit(self.ladder_image, (self.screen_width * 0.25, 0))  # Draw the ladder image
            overlay = pygame.Surface(self.display.get_size())
            # overlay.set_alpha(150)  # Set transparency level
            overlay.fill((0, 0, 0))  # Black background
            self.display.blit(overlay, (0, 0))  # Fill the screen with black

            # Display the appropriate message based on win or loss
            message = "You Win!" if self.win else "Game Over!"
            text_surface = self.font.render(message, True, (255, 255, 255))
            self.display.blit(text_surface, (
                self.display.get_width() // 2 - text_surface.get_width() // 2, self.display.get_height() // 3))

            # Define button positions
            self.restart_button = pygame.Rect(self.display.get_width() // 2 - (250 // 2), self.display.get_height() // 2, 250,
                                              50)
            self.exit_button = pygame.Rect(self.display.get_width() // 2 - (250 // 2), self.display.get_height() // 2 + 70,
                                           250, 50)

            if self.win:
                # If player wins, add a Next Level button
                self.next_level_button = pygame.Rect(self.display.get_width() // 2 - (250 // 2),
                                                     self.display.get_height() // 2 - 70, 250, 50)

                # Draw the Next Level button (Blue)
                pygame.draw.rect(self.display, (0, 0, 255), self.next_level_button)
                next_level_text = self.font.render("Next Level", True, (255, 255, 255))
                self.display.blit(next_level_text, (self.next_level_button.x + 80, self.next_level_button.y + 10))

            # Draw the Restart button (Green)
            pygame.draw.rect(self.display, (0, 128, 0), self.restart_button)
            restart_text = self.font.render("Restart Level", True, (255, 255, 255))
            self.display.blit(restart_text, (self.restart_button.x + 65, self.restart_button.y + 10))

            # Draw the Exit button (Red)
            pygame.draw.rect(self.display, (128, 0, 0), self.exit_button)
            exit_text = self.font.render("Return to Main Menu", True, (255, 255, 255))
            self.display.blit(exit_text, (self.exit_button.x + 30, self.exit_button.y + 10))

        def restart_level(self):
            # Reinitialize the level to reset all variables and the game state
            self.__init__(self.display, self.gameStateManager)
            self.gameStateManager.set_state('fourth-level')  # Set the game state back to 'first-level'
            self.is_restart = True

        def exit_to_main_menu(self):
            # Change the game state to 'main-menu'
            self.reset_level()
            self.gameStateManager.set_state('main-menu')

        def reset_level(self):
            """Reset the level to its original state."""
            self.lives = 3
            self.selected_word = None
            self.offset_x = 0
            self.offset_y = 0
            self.game_over = False
            self.win = False
            self.dialogue_played = False

            # Reset ladder slots
            for slot in self.ladder_slots:
                slot["word"] = ""
                slot["occupied"] = False
                slot["color"] = (251, 242, 54)

            # Reset draggable images
            for word_data in self.draggable_images:
                word_data["dragging"] = False
                word_data["placed"] = False
                word_data["rect"].x, word_data["rect"].y = word_data["original_pos"]

        def run_title_screen(self):
            title_text = "THE BROKEN BRIDGE"
            font_path_1 = os.path.join('fonts', 'ARIALBLACKITALIC.TTF')
            font_path_2 = os.path.join('fonts', 'ARIAL.TTF')
            title_font = pygame.font.Font(font_path_1, 50)  # Large font for the title
            button_font = pygame.font.Font(font_path_2, 20)

            button_color = (255, 255, 0)  # Yellow color for the button
            button_hover_color = (200, 200, 0)  # Darker yellow for hover effect
            button_rect = pygame.Rect((self.display.get_width() // 2 - 100, self.display.get_height() // 2 + 50),
                                      (200, 50))  # Button dimensions

            running = True
            while running:
                self.display.fill((0, 0, 0))  # Fill the screen with black

                # Render the title text
                title_surface = title_font.render(title_text, True, (255, 255, 255))  # White color for the title
                title_rect = title_surface.get_rect(
                    center=(self.display.get_width() // 2, self.display.get_height() // 2 - 50))
                self.display.blit(title_surface, title_rect)  # Blit title text

                # Check if the mouse is over the button
                mouse_pos = pygame.mouse.get_pos()  # Get the mouse position
                if button_rect.collidepoint(mouse_pos):
                    current_button_color = button_hover_color  # Use hover color
                else:
                    current_button_color = button_color  # Use normal color

                # Draw the button with the current color
                pygame.draw.rect(self.display, current_button_color, button_rect)  # Draw button
                button_text = button_font.render("Continue", True, (0, 0, 0))  # Black text for the button
                button_text_rect = button_text.get_rect(center=button_rect.center)  # Center text in button
                self.display.blit(button_text, button_text_rect)  # Blit button text

                # Event handling for button click
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:  # Left mouse button
                            if button_rect.collidepoint(mouse_pos):  # Check if mouse is over the button
                                running = False  # Exit the loop to move to the next screen

                pygame.display.flip()
                pygame.time.Clock().tick(60)  # Control the frame rate

        def run_dialogue_strip_1(self):
            self.dialogue_font = pygame.font.Font(None, 36)

            # Dialogue list (narrating the FourthLevel)
            self.dialogue_lines = [
                "Successfully crossed the treacherous lagoon full of sea monsters beneath the waters,\n they once again continued their journey.",
                "Traveler’s feet and Lexi’s wings brought them to a path that lead towards a broken bridge.",
                "The bridge that connects the lands of Dyscape that had been scrambled after Confusion’s arrival.",
                "As the Traveler peaked near the edge of the cliff, he then realized how high it was.",
                "Luckily, he noticed that there are specific sounds that are contained in each step of\n the bridge. Would this help them cross? Or will this hinder their journey to Confusion?",
            ]

            # Corresponding images for each dialogue line
            self.dialogue_images = [
                pygame.image.load(os.path.join('graphics', 'to-broken-bridge-1.png')).convert_alpha(),
                pygame.image.load(os.path.join('graphics', 'to-broken-bridge-2.png')).convert_alpha(),
                pygame.image.load(os.path.join('graphics', 'to-broken-bridge-2.png')).convert_alpha(),
                pygame.image.load(os.path.join('graphics', 'to-broken-bridge-3.png')).convert_alpha(),
                pygame.image.load(os.path.join('graphics', 'to-broken-bridge-3.png')).convert_alpha(),

            ]

            # Corresponding narration files for each dialogue line
            self.dialogue_sounds = [
                pygame.mixer.Sound(os.path.join('audio', 'fourth-narrator-1.mp3')),
                pygame.mixer.Sound(os.path.join('audio', 'fourth-narrator-2.mp3')),
                pygame.mixer.Sound(os.path.join('audio', 'fourth-narrator-3.mp3')),
                pygame.mixer.Sound(os.path.join('audio', 'fourth-narrator-4.mp3')),
                pygame.mixer.Sound(os.path.join('audio', 'fourth-narrator-5.mp3')),
            ]

            # Scale the images to fit the screen
            self.dialogue_images = [
                pygame.transform.scale(img, (self.display.get_width(), self.display.get_height() - 150)) for img in
                self.dialogue_images
            ]

            self.dialogue_index = 0
            running = True

            # Initialize the mixer for playing audio
            pygame.mixer.init()

            # Flag to check if narration is playing
            self.narration_playing = False

            def play_narration():
                """Play the narration for the current dialogue line."""
                self.narration_playing = True
                self.dialogue_sounds[self.dialogue_index].play()
                pygame.time.set_timer(pygame.USEREVENT,
                                      int(self.dialogue_sounds[self.dialogue_index].get_length() * 1000))

            # Play the first narration automatically
            play_narration()

            while running:
                self.display.fill((0, 0, 0))  # Black background for the dialogue screen

                # Display the corresponding image
                self.display.blit(self.dialogue_images[self.dialogue_index], (0, 0))

                # Create and display the dialogue box
                dialogue_box_rect = pygame.Rect(0, self.display.get_height() - 150, self.display.get_width(), 150)
                pygame.draw.rect(self.display, (0, 0, 0), dialogue_box_rect)

                # Render the current dialogue line
                dialogue_text = self.dialogue_font.render(self.dialogue_lines[self.dialogue_index], True,
                                                          (255, 255, 255))  # White font
                dialogue_rect = dialogue_text.get_rect(
                    center=(self.display.get_width() // 2, self.display.get_height() - 75))
                self.display.blit(dialogue_text, dialogue_rect)

                # Event handling
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        sys.exit()

                    # Allow the player to skip the narration and move to the next slide with the spacebar
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.dialogue_sounds[self.dialogue_index].stop()  # Stop the current narration
                            self.narration_playing = False
                            self.dialogue_index += 1
                            if self.dialogue_index >= len(self.dialogue_lines):
                                running = False  # End the dialogue and start the game
                            else:
                                play_narration()  # Play the next narration

                    # Check if narration finished
                    if event.type == pygame.USEREVENT and self.narration_playing:
                        self.narration_playing = False
                        self.dialogue_index += 1
                        if self.dialogue_index >= len(self.dialogue_lines):
                            running = False  # End the dialogue and start the game
                        else:
                            play_narration()  # Play the next narration

                pygame.display.update()

        def load_spritesheet(self, filename, frame_width, frame_height, scale_factor):
            # Load the sprite sheet image
            spritesheet = pygame.image.load(os.path.join('graphics', filename)).convert_alpha()
            # Get the width and height of the entire sprite sheet
            sheet_width, sheet_height = spritesheet.get_size()

            # Create a list to hold individual frames
            frames = []
            for y in range(0, sheet_height, frame_height):
                for x in range(0, sheet_width, frame_width):
                    # Extract each frame by using a sub-surface
                    frame = spritesheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
                    # Scale the frame to make it larger
                    scaled_frame = pygame.transform.scale(frame, (
                        int(frame_width * scale_factor), int(frame_height * scale_factor)))
                    frames.append(scaled_frame)

            return frames

        def run_dialogue_strip_2(self):
            # Initialize pygame's mixer for audio (if needed)
            pygame.mixer.init()

            # Load the owl sprite sheet and extract frames for animation
            owl_frames = self.load_spritesheet('owl-flying.png', 48, 48, scale_factor=6)
            owl_frame_index = 0  # Start with the first frame of the animation
            owl_animation_speed = 5  # Change the frame every 5 frames of the game loop

            # Load character images (only one image for the player)
            char1_image = pygame.image.load(os.path.join('graphics', 'character-avatar.png'))
            char1_image = pygame.transform.scale(char1_image, (200, 200))

            dialogue_data = [
                {"name": "Lexi the Owl", "text": "This bridge was really destroyed because of Confusion", "audio": "owl-talking-28.mp3"},
                {"name": "Lexi the Owl", "text": "But you know what, adventurer? We can fix this bridge.", "audio": "owl-talking-29.mp3"},
                {"name": "You", "text": "Really!? How?", "image": char1_image},
                {"name": "Lexi the Owl", "text": "You see those planks with audio symbols? Those can speak out words.", "audio": "owl-talking-30.mp3"},
                {"name": "Lexi the Owl", "text": "All we need to do is to COLLECT PICTURES that RHYMES with the word inside the bridge plank", "audio": "owl-talking-31.mp3"},
                {"name": "Lexi the Owl", "text": "Put that picture beside the plank and we can make a temporary wood that can make us cross this bridge.", "audio": "owl-talking-32.mp3"},
                {"name": "You", "text": "Wow! That's amazing! Okay, got it...", "image": char1_image},
            ]

            # Preload audio files
            audio_files = {}
            for dialogue in dialogue_data:
                if "audio" in dialogue:
                    audio_file = dialogue["audio"]
                    audio_files[audio_file] = pygame.mixer.Sound(os.path.join("audio", audio_file))

            dialogue_box_height = 150  # Height of the dialogue box surface
            dialogue_font = pygame.font.Font(None, 32)  # Font for dialogue text
            name_font = pygame.font.Font(None, 36)  # Font for character names
            space_prompt_font = pygame.font.Font(None, 28)  # Font for "Press SPACE to continue"

            current_line = 0
            text_displayed = ""
            text_index = 0
            text_speed = 2  # Speed of text animation
            audio_played = False  # Flag to track if audio has been played for the current line
            current_sound = None  # Track the currently playing sound

            running = True
            clock = pygame.time.Clock()

            while running:
                self.display.blit(self.bottom_platform, (0, 0))  # Draw the bottom platform
                self.display.blit(self.green_platform, (0, 320))  # Draw the green platform
                self.display.blit(self.ladder_image, (self.screen_width * 0.25, 0))  # Draw the ladder image

                # Create the dialogue box at the bottom
                dialogue_box = pygame.Surface((self.display.get_width(), dialogue_box_height))
                dialogue_box.fill((255, 219, 172))  # Light background for the dialogue box
                dialogue_box_rect = dialogue_box.get_rect(topleft=(0, self.display.get_height() - dialogue_box_height))

                # Draw the brown border around the dialogue box
                border_color = (139, 69, 19)  # Brown color (RGB)
                border_thickness = 20  # Thickness of the border
                pygame.draw.rect(self.display, border_color,
                                 dialogue_box_rect.inflate(border_thickness, border_thickness),
                                 border_thickness)

                # Get the current dialogue data
                current_dialogue = dialogue_data[current_line]
                character_name = current_dialogue["name"]
                character_text = current_dialogue["text"]
                antagonist = "Magical Owl"

                # Play the audio file if it exists and hasn't been played yet
                if "audio" in current_dialogue and not audio_played:
                    audio_file = current_dialogue["audio"]
                    if current_sound is not None:
                        current_sound.stop()  # Stop the currently playing sound if it exists
                    current_sound = audio_files[audio_file]  # Get the new sound
                    current_sound.play()  # Play the new audio
                    audio_played = True  # Set the flag to True to prevent replaying the audio

                # Update owl animation (cycle through the frames)
                if character_name == antagonist or character_name == "Lexi the Owl":
                    owl_frame_index = (owl_frame_index + 1) % (len(owl_frames) * owl_animation_speed)
                    current_owl_frame = owl_frames[owl_frame_index // owl_animation_speed]
                    self.display.blit(current_owl_frame, (950, self.display.get_height() - dialogue_box_height - 300))

                # Render the character image (player) if it's the player's turn
                else:
                    self.display.blit(char1_image, (50, self.display.get_height() - dialogue_box_height - 200))

                # Render the character name inside the dialogue box (above the text)
                name_surface = name_font.render(character_name, True, BLACK)
                dialogue_box.blit(name_surface, (20, 10))  # Draw name near the top inside the dialogue box

                # Text animation (add one letter at a time)
                if text_index < len(character_text):
                    text_index += text_speed  # Control how fast letters are added
                    text_displayed = character_text[:text_index]
                else:
                    text_displayed = character_text

                # Render the dialogue text below the name
                text_surface = dialogue_font.render(text_displayed, True, BLACK)
                dialogue_box.blit(text_surface, (20, 60))  # Draw the text inside the dialogue box below the name

                # Add "Press SPACE to continue." prompt at the bottom right
                if text_index >= len(character_text):  # Show prompt only if the text is fully displayed
                    space_prompt_surface = space_prompt_font.render("Press SPACE to continue.", True, (100, 100, 100))
                    dialogue_box.blit(space_prompt_surface,
                                      (dialogue_box.get_width() - space_prompt_surface.get_width() - 20,
                                       dialogue_box.get_height() - space_prompt_surface.get_height() - 10))

                # Draw the dialogue box on the screen with the brown border
                self.display.blit(dialogue_box, dialogue_box_rect.topleft)

                # Event handling for advancing the dialogue
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:  # Only proceed on SPACE key
                            if text_index >= len(character_text):
                                # Move to the next line of dialogue if the text is fully displayed
                                current_line += 1
                                text_index = 0
                                text_displayed = ""
                                audio_played = False  # Reset the audio flag for the next line
                                if current_line >= len(dialogue_data):
                                    running = False  # Exit dialogue when all lines are done

                pygame.display.flip()
                clock.tick(60)  # Control the frame rate

        def show_how_to_play(self):
            """Displays the 'how to play' instructions with a start button."""
            # Load the how-to-play image and scale it
            how_to_play_image = pygame.image.load(
                os.path.join('graphics', 'how-to-play(broken-bridge).png')).convert_alpha()
            how_to_play_image = pygame.transform.scale(how_to_play_image, (1280, 720))  # Scale to 1280x720

            # Define the start button
            start_button_rect = pygame.Rect((self.display.get_width() // 2 - 100, 650), (200, 50))  # Centered button

            # Define colors
            normal_color = (255, 255, 0)  # Yellow
            hover_color = (200, 200, 0)  # Darker yellow

            running = True
            while running:
                self.display.fill((0, 0, 0))  # Fill the screen with black
                self.display.blit(how_to_play_image, (0, 0))  # Display the how-to-play image

                # Check if the mouse is over the button
                mouse_pos = pygame.mouse.get_pos()
                if start_button_rect.collidepoint(mouse_pos):
                    button_color = hover_color  # Change to darker yellow on hover
                else:
                    button_color = normal_color  # Normal yellow color

                # Draw the start button
                pygame.draw.rect(self.display, button_color,
                                 start_button_rect)  # Draw button with the appropriate color
                start_text = self.font.render("Start", True, (0, 0, 0))  # Black text
                start_text_rect = start_text.get_rect(center=start_button_rect.center)  # Center text in button
                self.display.blit(start_text, start_text_rect)  # Blit start text

                # Event handling for button click
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if start_button_rect.collidepoint(event.pos):  # Check if mouse is over the button
                            running = False  # Exit the loop to proceed to the next screen

                pygame.display.update()

        def start_countdown(self):
            """Displays a 3-2-1 countdown before the game starts."""
            for count in range(3, 0, -1):
                self.display.fill((0, 0, 0))  # Black background
                countdown_surface = self.countdown_font.render(str(count), True,
                                                               (255, 255, 255))  # White countdown number
                self.display.blit(countdown_surface,
                                  (self.display.get_width() // 2 - countdown_surface.get_width() // 2,
                                   self.display.get_height() // 2 - countdown_surface.get_height() // 2))
                pygame.display.update()
                pygame.time.wait(1000)  # Wait 1 second for each countdown step

            pass

        def run(self):
            """Main game loop for the first level."""

            correct_answer_sound = pygame.mixer.Sound(os.path.join('audio', 'correct-answer.mp3'))
            wrong_answer_sound = pygame.mixer.Sound(os.path.join('audio', 'wrong-answer.mp3'))

            speaker_icon = pygame.image.load(os.path.join('graphics', 'audio-logo.png')).convert_alpha()
            speaker_icon = pygame.transform.scale(speaker_icon, (30, 30))  # Resize the speaker icon to fit on the ladder

            # Only run the dialogue strip the first time the level is played
            if not self.dialogue_played:
                self.run_dialogue_strip_1()
                self.run_title_screen()
                self.run_dialogue_strip_2()
            else:
                self.is_restart = False
            self.show_how_to_play()
            self.start_countdown()
            running = True
            while running:

                if self.game_over or self.win:
                    self.show_end_screen()  # Display the end screen when game is over or won
                    pygame.display.update()

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()

                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            # Check if the Restart button is clicked
                            if self.restart_button.collidepoint(event.pos):
                                self.restart_level()  # Restart the level if clicked
                                self.dialogue_played = True
                                running = False

                            # Check if the Exit button is clicked
                            elif self.exit_button.collidepoint(event.pos):
                                self.exit_to_main_menu()  # Exit to the main menu if clicked
                                running = False
                            elif self.win and self.next_level_button.collidepoint(event.pos):
                                self.gameStateManager.set_state('fifth-level')
                                running = False
                    continue  # Skip the rest of the game loop while in the end screen

                # Main game logic
                self.display.blit(self.bottom_platform, (0, 0))  # Draw the bottom platform
                self.display.blit(self.green_platform, (0, 320))  # Draw the green platform
                self.display.blit(self.ladder_image, (self.screen_width * 0.25, 0))  # Draw the ladder image

                # Display lives (hearts)
                for i in range(self.lives):
                    self.display.blit(self.heart_image, (10 + i * 60, 10))

                # Display ladder slots and draggable images
                for slot in self.ladder_slots:
                    # Draw slot rectangles
                    if slot["color"] == (143, 86, 59):
                        pygame.draw.rect(self.display, slot["color"], slot["rect"])  # Full brown for correct placement
                    else:
                        pygame.draw.rect(self.display, slot["color"], slot["rect"], 3)

                    # **Display the speaker icon on the ladder slot (brown part)**
                    speaker_icon_rect = speaker_icon.get_rect(center=(slot["rect"].centerx, slot["rect"].centery + 45))
                    self.display.blit(speaker_icon, speaker_icon_rect)

                # Display the draggable images (only if not placed)
                for word_data in self.draggable_images:
                    if not word_data["placed"]:  # Only draw the image if it hasn't been placed correctly yet
                        self.display.blit(word_data["image"], word_data["rect"])

                mouse_pos = pygame.mouse.get_pos()

                # **Update the selected image's position smoothly along with the mouse cursor**
                if self.selected_word:
                    self.selected_word["rect"].x = mouse_pos[0] + self.offset_x
                    self.selected_word["rect"].y = mouse_pos[1] + self.offset_y

                # Event handling
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        # **Handle image dragging logic more responsively**
                        if not self.selected_word:
                            for word_data in self.draggable_images:
                                if word_data["rect"].collidepoint(event.pos) and not word_data["placed"]:
                                    self.selected_word = word_data
                                    # Capture the precise offset between the image and the cursor
                                    self.offset_x = word_data["rect"].x - event.pos[0]
                                    self.offset_y = word_data["rect"].y - event.pos[1]
                                    break

                                    # Check if mouse clicked on speaker icon
                            for slot in self.ladder_slots:
                                speaker_icon_rect = speaker_icon.get_rect(center=(slot["rect"].centerx, slot["rect"].centery + 45))
                                if speaker_icon_rect.collidepoint(event.pos):
                                    self.speak_word(slot["pair_word"])  # Trigger TTS for the word on the ladder slot

                    elif event.type == pygame.MOUSEBUTTONUP:
                        # Handle image placement logic
                        if self.selected_word:
                            placed_in_slot = False
                            wrong_slot = False  # Flag to track if the image was placed in the wrong slot
                            for slot in self.ladder_slots:
                                if slot["rect"].colliderect(self.selected_word["rect"]) and not slot["occupied"]:
                                    placed_in_slot = True
                                    if slot["correct_word"] == self.selected_word["word"]:
                                        # Snap image into place if correct
                                        correct_answer_sound.play()
                                        self.selected_word["rect"].center = slot["rect"].center
                                        slot["occupied"] = True
                                        slot["color"] = (143, 86, 59)  # Change color to brown for correct placement
                                        self.selected_word["placed"] = True  # Mark the word as placed, so it disappears
                                    else:
                                        # Image was placed in a wrong slot
                                        wrong_answer_sound.play()
                                        wrong_slot = True
                                        self.selected_word["rect"].x, self.selected_word["rect"].y = self.selected_word[
                                            "original_pos"]
                            # If the image was placed in a slot but it's wrong, deduct a life
                            if wrong_slot:
                                self.lives -= 1
                            # If the image was not placed in any slot, snap it back to its original position (no life deduction)
                            if not placed_in_slot:
                                self.selected_word["rect"].x, self.selected_word["rect"].y = self.selected_word[
                                    "original_pos"]

                            self.selected_word = None

                # Check game over conditions
                if self.lives <= 0:
                    self.game_over = True
                    print("Game Over!")

                # Check win condition (all slots occupied)
                if all(slot["occupied"] for slot in self.ladder_slots):
                    self.win = True
                    print("You Win!")

                pygame.display.update()  # Update the display

class TheRhymeanGarden:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager
        self.screen_width, self.screen_height = self.display.get_size()
        self.countdown_font = pygame.font.Font(None, 100)

        # Initialize player attributes
        self.lives = 3
        self.time_limit = 15.0
        self.current_time = 0
        self.timer_started = False
        self.win = False
        self.game_over = False
        self.is_restart = False

        # Track current round
        self.rounds_completed = 0
        self.max_rounds = 10

        # Load the Arial font
        font_path = os.path.join('fonts', 'ARIAL.TTF')
        self.font = pygame.font.Font(font_path, 30)
        self.large_font = pygame.font.Font(font_path, 55)

        # Load necessary assets
        self.background = pygame.image.load(os.path.join('graphics', 'garden.png')).convert_alpha()
        self.background = pygame.transform.scale(self.background, (self.display.get_width(), self.display.get_height()))

        # Words for the game
        self.flower_words = ["Tree", "Box", "Ball", "Duck", "Cat", "Dog", "Fish", "Bird", "Bed", "House"]
        random.shuffle(self.flower_words)
        self.current_flower_word = self.flower_words[self.rounds_completed]

        # Dictionary to map words to images
        self.word_images = {
            "Tree": pygame.image.load(os.path.join('graphics', 'corrupted-tree.png')).convert_alpha(),
            "Bed": pygame.image.load(os.path.join('graphics', 'corrupted-bed.png')).convert_alpha(),
            "Dog": pygame.image.load(os.path.join('graphics', 'corrupted-dog.png')).convert_alpha(),
            "Box": pygame.image.load(os.path.join('graphics', 'corrupted-box.png')).convert_alpha(),
            "Ball": pygame.image.load(os.path.join('graphics', 'corrupted-ball.png')).convert_alpha(),
            "Duck": pygame.image.load(os.path.join('graphics', 'corrupted-duck.png')).convert_alpha(),
            "Cat": pygame.image.load(os.path.join('graphics', 'corrupted-cat.png')).convert_alpha(),
            "Fish": pygame.image.load(os.path.join('graphics', 'corrupted-fish.png')).convert_alpha(),
            "Bird": pygame.image.load(os.path.join('graphics', 'corrupted-bird.png')).convert_alpha(),
            "House": pygame.image.load(os.path.join('graphics', 'corrupted-house.png')).convert_alpha(),
        }
        # Scale images to fit the screen (if needed)
        for word in self.word_images:
            self.word_images[word] = pygame.transform.scale(self.word_images[word], (450, 520))

        # Initialize game state
        self.input_text = ''
        self.clock = pygame.time.Clock()
        self.last_time = pygame.time.get_ticks()
        self.time_passed = 0.0

        # Load hearts for lives display and resize them
        self.heart_image = pygame.image.load(os.path.join('graphics', 'heart.png')).convert_alpha()
        self.heart_image = pygame.transform.scale(self.heart_image, (80, 50))

        # Load warrior sprite sheet and initialize animation variables
        self.warrior_spritesheet = pygame.image.load(
            os.path.join('graphics', 'idle-character-with-sword.png')).convert_alpha()
        self.warrior_frame_width = 400
        self.warrior_frame_height = 426
        self.warrior_frames = [
            self.warrior_spritesheet.subsurface(
                (i * self.warrior_frame_width, 0, self.warrior_frame_width, self.warrior_frame_height))
            for i in range(9)
        ]
        self.warrior_current_frame = 0
        self.warrior_animation_speed = 0.2  # Adjust speed (higher is slower)
        self.warrior_frame_time = 0  # Time tracking for frame updates

        # Load warrior attack sprite sheet and initialize animation variables
        self.attack_spritesheet = pygame.image.load(
            os.path.join('graphics', 'slash-animation.png')).convert_alpha()
        self.attack_frames = [
            self.attack_spritesheet.subsurface(
                (i * self.warrior_frame_width, 0, self.warrior_frame_width, self.warrior_frame_height))
            for i in range(9)
        ]
        self.attack_current_frame = 0
        self.attack_animation_speed = 0.1  # Adjust as needed
        self.is_attacking = False  # Track if attack animation is active

        # Track the type of animation currently playing
        self.current_animation = 'idle'

        # Load speaker icon
        self.speaker_image = pygame.image.load(os.path.join('graphics', 'audio-logo.png')).convert_alpha()
        self.speaker_image = pygame.transform.scale(self.speaker_image, (100, 100))
        self.speaker_rect = self.speaker_image.get_rect(center=(self.screen_width // 2, 50))

        # Initialize TTS (text-to-speech) engine
        self.tts_engine = pyttsx3.init()

    def draw_hearts(self):
        for i in range(self.lives):
            self.display.blit(self.heart_image, (10 + i * 60, 10))

    def draw_timer(self, time_left):
        # Calculate minutes and seconds
        minutes = int(time_left) // 60
        seconds = int(time_left) % 60

        # Format time as MM:SS
        timer_text = self.large_font.render(f"Time: {minutes:02}:{seconds:02}", True, (255, 255, 255))

        # Render and blit the timer text
        self.display.blit(timer_text, (30, 80))


    def draw_text_box(self):
        pygame.draw.rect(self.display, (255, 255, 255),
                         [self.screen_width // 2 - 175, self.screen_height - 100, 350, 50], 0)
        text_surface = self.font.render(self.input_text, True, (0, 0, 0))
        self.display.blit(text_surface, (self.screen_width // 2 - 150, self.screen_height - 90))

        prompt_surface = self.font.render("Name a word that rhymes:", True, (0, 0, 0))
        self.display.blit(prompt_surface, (self.screen_width // 2 - 175, self.screen_height - 150))

    def draw_enemy(self):
        current_image = self.word_images[self.current_flower_word]
        self.display.blit(current_image, (650, 100))

    # Function to draw the character
    def draw_warrior(self):
        if self.current_animation == 'idle':
            # Draw the idle animation
            self.display.blit(self.warrior_frames[self.warrior_current_frame],
                              (150, self.screen_height - self.warrior_frame_height - 1))
        elif self.current_animation == 'attack':
            # Draw the attack animation
            self.display.blit(self.attack_frames[self.attack_current_frame],
                              (150, self.screen_height - self.warrior_frame_height - 1))


    # Function to update the warrior animation
    def update_animation(self):
        if self.current_animation == 'idle':
            # Idle animation logic
            self.warrior_frame_time += self.clock.get_time() / 1000.0
            if self.warrior_frame_time >= self.warrior_animation_speed:
                self.warrior_current_frame = (self.warrior_current_frame + 1) % len(self.warrior_frames)
                self.warrior_frame_time = 0
        elif self.current_animation == 'attack':
            # Attack animation logic
            self.warrior_frame_time += self.clock.get_time() / 1000.0
            if self.warrior_frame_time >= self.attack_animation_speed:
                if self.attack_current_frame < len(self.attack_frames) - 1:
                    self.attack_current_frame += 1
                else:
                    # Reset to idle animation after the attack is complete
                    self.current_animation = 'idle'
                    self.attack_current_frame = 0
                self.warrior_frame_time = 0
    def draw_speaker(self):
        self.display.blit(self.speaker_image, self.speaker_rect.topleft)

    def check_rhyme(self):
        rhymes = pronouncing.rhymes(self.current_flower_word.lower())
        return self.input_text.strip().lower() in rhymes

    def pronounce_word(self):
        self.tts_engine.say(self.current_flower_word)
        self.tts_engine.runAndWait()

    def reset_round(self):
        self.rounds_completed += 1
        if self.rounds_completed < self.max_rounds:
            self.current_flower_word = self.flower_words[self.rounds_completed]
            self.input_text = ''
            self.current_time = self.time_limit
        else:
            # self.gameStateManager.set_state('win')
            print("Level done. Showing end screen")
            self.show_end_screen()
            self.game_over = True

    def run_title_screen(self):
        title_text = "THE RHYMEAN GARDEN"
        font_path_1 = os.path.join('fonts', 'ARIALBLACKITALIC.TTF')
        font_path_2 = os.path.join('fonts', 'ARIAL.TTF')
        title_font = pygame.font.Font(font_path_1, 50)  # Large font for the title
        button_font = pygame.font.Font(font_path_2, 20)

        button_color = (255, 255, 0)  # Yellow color for the button
        button_hover_color = (200, 200, 0)  # Darker yellow for hover effect
        button_rect = pygame.Rect((self.display.get_width() // 2 - 100, self.display.get_height() // 2 + 50),
                                  (200, 50))  # Button dimensions

        running = True
        while running:
            self.display.fill((0, 0, 0))  # Fill the screen with black

            # Render the title text
            title_surface = title_font.render(title_text, True, (255, 255, 255))  # White color for the title
            title_rect = title_surface.get_rect(
                center=(self.display.get_width() // 2, self.display.get_height() // 2 - 50))
            self.display.blit(title_surface, title_rect)  # Blit title text

            # Check if the mouse is over the button
            mouse_pos = pygame.mouse.get_pos()  # Get the mouse position
            if button_rect.collidepoint(mouse_pos):
                current_button_color = button_hover_color  # Use hover color
            else:
                current_button_color = button_color  # Use normal color

            # Draw the button with the current color
            pygame.draw.rect(self.display, current_button_color, button_rect)  # Draw button
            button_text = button_font.render("Continue", True, (0, 0, 0))  # Black text for the button
            button_text_rect = button_text.get_rect(center=button_rect.center)  # Center text in button
            self.display.blit(button_text, button_text_rect)  # Blit button text

            # Event handling for button click
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        if button_rect.collidepoint(mouse_pos):  # Check if mouse is over the button
                            running = False  # Exit the loop to move to the next screen

            pygame.display.flip()
            pygame.time.Clock().tick(60)  # Control the frame rate

    def run_dialogue_strip_1(self):
        self.dialogue_font = pygame.font.Font(None, 36)

        # Dialogue list (narrating the FourthLevel)
        self.dialogue_lines = [
            "Completed another one of their trials, they went on their way to their quest.",
            "Shortly, they noticed a huge garden standing in the middle of the lands.",
            "As they went down, Lexi saw a plunged sword on the ground.",
            "He then notified Traveler, telling him it’s best if he’s equipped with a weapon to aid him on this journey.",
            "As the Traveler picked and held the sword, the radiating energy overflows as it glows like rays of the sun.",
            "As they entered the abandoned garden, the place felt eerie and scary. It was awfully quiet.",
            "Little did they know, the objects inside the garden absorbed the malicious powers of Confusion,\n bringing them to life to terrorize the intruders."
        ]

        # Corresponding images for each dialogue line
        self.dialogue_images = [
            pygame.image.load(os.path.join('graphics', 'to-rhymean-garden-1.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'to-rhymean-garden-1.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'to-rhymean-garden-2.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'to-rhymean-garden-2.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'to-rhymean-garden-3.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'to-rhymean-garden-4.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'to-rhymean-garden-5.png')).convert_alpha(),
        ]

        # Corresponding narration files for each dialogue line
        self.dialogue_sounds = [
            pygame.mixer.Sound(os.path.join('audio', 'fifth-narrator-1.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'fifth-narrator-2.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'fifth-narrator-3.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'fifth-narrator-4.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'fifth-narrator-5.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'fifth-narrator-6.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'fifth-narrator-7.mp3')),
        ]

        # Scale the images to fit the screen
        self.dialogue_images = [
            pygame.transform.scale(img, (self.display.get_width(), self.display.get_height() - 150)) for img in
            self.dialogue_images
        ]

        self.dialogue_index = 0
        running = True

        # Initialize the mixer for playing audio
        pygame.mixer.init()

        # Flag to check if narration is playing
        self.narration_playing = False

        def play_narration():
            """Play the narration for the current dialogue line."""
            self.narration_playing = True
            self.dialogue_sounds[self.dialogue_index].play()
            pygame.time.set_timer(pygame.USEREVENT,
                                  int(self.dialogue_sounds[self.dialogue_index].get_length() * 1000))

        # Play the first narration automatically
        play_narration()

        while running:
            self.display.fill((0, 0, 0))  # Black background for the dialogue screen

            # Display the corresponding image
            self.display.blit(self.dialogue_images[self.dialogue_index], (0, 0))

            # Create and display the dialogue box
            dialogue_box_rect = pygame.Rect(0, self.display.get_height() - 150, self.display.get_width(), 150)
            pygame.draw.rect(self.display, (0, 0, 0), dialogue_box_rect)

            # Render the current dialogue line
            dialogue_text = self.dialogue_font.render(self.dialogue_lines[self.dialogue_index], True,
                                                      (255, 255, 255))  # White font
            dialogue_rect = dialogue_text.get_rect(
                center=(self.display.get_width() // 2, self.display.get_height() - 75))
            self.display.blit(dialogue_text, dialogue_rect)

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    sys.exit()

                # Allow the player to skip the narration and move to the next slide with the spacebar
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.dialogue_sounds[self.dialogue_index].stop()  # Stop the current narration
                        self.narration_playing = False
                        self.dialogue_index += 1
                        if self.dialogue_index >= len(self.dialogue_lines):
                            running = False  # End the dialogue and start the game
                        else:
                            play_narration()  # Play the next narration

                # Check if narration finished
                if event.type == pygame.USEREVENT and self.narration_playing:
                    self.narration_playing = False
                    self.dialogue_index += 1
                    if self.dialogue_index >= len(self.dialogue_lines):
                        running = False  # End the dialogue and start the game
                    else:
                        play_narration()  # Play the next narration

            pygame.display.update()

    def load_spritesheet(self, filename, frame_width, frame_height, scale_factor):
        # Load the sprite sheet image
        spritesheet = pygame.image.load(os.path.join('graphics', filename)).convert_alpha()
        # Get the width and height of the entire sprite sheet
        sheet_width, sheet_height = spritesheet.get_size()

        # Create a list to hold individual frames
        frames = []
        for y in range(0, sheet_height, frame_height):
            for x in range(0, sheet_width, frame_width):
                # Extract each frame by using a sub-surface
                frame = spritesheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
                # Scale the frame to make it larger
                scaled_frame = pygame.transform.scale(frame, (
                    int(frame_width * scale_factor), int(frame_height * scale_factor)))
                frames.append(scaled_frame)

        return frames

    def run_dialogue_strip_2(self):
        # Initialize pygame's mixer for audio (if needed)
        pygame.mixer.init()

        # Load the owl sprite sheet and extract frames for animation
        owl_frames = self.load_spritesheet('owl-flying.png', 48, 48, scale_factor=6)
        owl_frame_index = 0  # Start with the first frame of the animation
        owl_animation_speed = 5  # Change the frame every 5 frames of the game loop

        # Load character images (only one image for the player)
        char1_image = pygame.image.load(os.path.join('graphics', 'character-avatar.png'))
        char1_image = pygame.transform.scale(char1_image, (200, 200))

        dialogue_data = [
            {"name": "Lexi the Owl", "text": "This will be the perfect time that we will use your sword, adventurer.", "audio": "owl-talking-33.mp3"},
            {"name": "Lexi the Owl", "text": "Not only physical things, but also animals nearby are being affected by the curse.", "audio": "owl-talking-34.mp3"},
            {"name": "You", "text": "What can we do, Lexi? This is my first time holding a sword.", "image": char1_image},
            {"name": "You", "text": "I only held an axe my entire life.", "image": char1_image},
            {"name": "Lexi the Owl", "text": "Then use it like an axe.", "audio": "owl-talking-35.mp3"},
            {"name": "Lexi the Owl", "text": "Maybe there is some way we can defeat them effectively.", "audio": "owl-talking-36.mp3"},
            {"name": "You", "text": "Maybe a perfect combo will do a thing? like RHYMING words?", "image": char1_image},
            {"name": "Lexi the Owl", "text": "That's a good idea! This garden is called Rhymean Garden, after all.", "audio": "owl-talking-37.mp3"},
            {"name": "You", "text": "Okay. Let's do it!", "image": char1_image},

        ]

        # Preload audio files
        audio_files = {}
        for dialogue in dialogue_data:
            if "audio" in dialogue:
                audio_file = dialogue["audio"]
                audio_files[audio_file] = pygame.mixer.Sound(os.path.join("audio", audio_file))

        dialogue_box_height = 150  # Height of the dialogue box surface
        dialogue_font = pygame.font.Font(None, 32)  # Font for dialogue text
        name_font = pygame.font.Font(None, 36)  # Font for character names
        space_prompt_font = pygame.font.Font(None, 28)  # Font for "Press SPACE to continue"

        current_line = 0
        text_displayed = ""
        text_index = 0
        text_speed = 2  # Speed of text animation
        audio_played = False  # Flag to track if audio has been played for the current line
        current_sound = None  # Track the currently playing sound

        running = True
        clock = pygame.time.Clock()

        while running:
            self.display.blit(self.background, (0,0))

            # Create the dialogue box at the bottom
            dialogue_box = pygame.Surface((self.display.get_width(), dialogue_box_height))
            dialogue_box.fill((255, 219, 172))  # Light background for the dialogue box
            dialogue_box_rect = dialogue_box.get_rect(topleft=(0, self.display.get_height() - dialogue_box_height))

            # Draw the brown border around the dialogue box
            border_color = (139, 69, 19)  # Brown color (RGB)
            border_thickness = 20  # Thickness of the border
            pygame.draw.rect(self.display, border_color,
                             dialogue_box_rect.inflate(border_thickness, border_thickness),
                             border_thickness)

            # Get the current dialogue data
            current_dialogue = dialogue_data[current_line]
            character_name = current_dialogue["name"]
            character_text = current_dialogue["text"]
            antagonist = "Magical Owl"

            # Play the audio file if it exists and hasn't been played yet
            if "audio" in current_dialogue and not audio_played:
                audio_file = current_dialogue["audio"]
                if current_sound is not None:
                    current_sound.stop()  # Stop the currently playing sound if it exists
                current_sound = audio_files[audio_file]  # Get the new sound
                current_sound.play()  # Play the new audio
                audio_played = True  # Set the flag to True to prevent replaying the audio

            # Update owl animation (cycle through the frames)
            if character_name == antagonist or character_name == "Lexi the Owl":
                owl_frame_index = (owl_frame_index + 1) % (len(owl_frames) * owl_animation_speed)
                current_owl_frame = owl_frames[owl_frame_index // owl_animation_speed]
                self.display.blit(current_owl_frame, (950, self.display.get_height() - dialogue_box_height - 300))

            # Render the character image (player) if it's the player's turn
            else:
                self.display.blit(char1_image, (50, self.display.get_height() - dialogue_box_height - 200))

            # Render the character name inside the dialogue box (above the text)
            name_surface = name_font.render(character_name, True, BLACK)
            dialogue_box.blit(name_surface, (20, 10))  # Draw name near the top inside the dialogue box

            # Text animation (add one letter at a time)
            if text_index < len(character_text):
                text_index += text_speed  # Control how fast letters are added
                text_displayed = character_text[:text_index]
            else:
                text_displayed = character_text

            # Render the dialogue text below the name
            text_surface = dialogue_font.render(text_displayed, True, BLACK)
            dialogue_box.blit(text_surface, (20, 60))  # Draw the text inside the dialogue box below the name

            # Add "Press SPACE to continue." prompt at the bottom right
            if text_index >= len(character_text):  # Show prompt only if the text is fully displayed
                space_prompt_surface = space_prompt_font.render("Press SPACE to continue.", True, (100, 100, 100))
                dialogue_box.blit(space_prompt_surface,
                                  (dialogue_box.get_width() - space_prompt_surface.get_width() - 20,
                                   dialogue_box.get_height() - space_prompt_surface.get_height() - 10))

            # Draw the dialogue box on the screen with the brown border
            self.display.blit(dialogue_box, dialogue_box_rect.topleft)

            # Event handling for advancing the dialogue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:  # Only proceed on SPACE key
                        if text_index >= len(character_text):
                            # Move to the next line of dialogue if the text is fully displayed
                            current_line += 1
                            text_index = 0
                            text_displayed = ""
                            audio_played = False  # Reset the audio flag for the next line
                            if current_line >= len(dialogue_data):
                                running = False  # Exit dialogue when all lines are done

            pygame.display.flip()
            clock.tick(60)  # Control the frame rate

    def show_how_to_play(self):
        """Displays the 'how to play' instructions with a start button."""
        # Load the how-to-play image and scale it
        how_to_play_image = pygame.image.load(os.path.join('graphics', 'how-to-play(rhymean-garden).png')).convert_alpha()
        how_to_play_image = pygame.transform.scale(how_to_play_image, (1280, 720))  # Scale to 1280x720

        # Define the start button
        start_button_rect = pygame.Rect((self.display.get_width() // 2 - 100, 650), (200, 50))  # Centered button

        # Define colors
        normal_color = (255, 255, 0)  # Yellow
        hover_color = (200, 200, 0)  # Darker yellow

        running = True
        while running:
            self.display.fill((0, 0, 0))  # Fill the screen with black
            self.display.blit(how_to_play_image, (0, 0))  # Display the how-to-play image

            # Check if the mouse is over the button
            mouse_pos = pygame.mouse.get_pos()
            if start_button_rect.collidepoint(mouse_pos):
                button_color = hover_color  # Change to darker yellow on hover
            else:
                button_color = normal_color  # Normal yellow color

            # Draw the start button
            pygame.draw.rect(self.display, button_color, start_button_rect)  # Draw button with the appropriate color
            start_text = self.font.render("Start", True, (0, 0, 0))  # Black text
            start_text_rect = start_text.get_rect(center=start_button_rect.center)  # Center text in button
            self.display.blit(start_text, start_text_rect)  # Blit start text

            # Event handling for button click
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if start_button_rect.collidepoint(event.pos):  # Check if mouse is over the button
                        running = False  # Exit the loop to proceed to the next screen

            pygame.display.update()

    def start_countdown(self):
        """Displays a 3-2-1 countdown before the game starts."""
        for count in range(3, 0, -1):
            self.display.fill((0, 0, 0))  # Black background
            countdown_surface = self.countdown_font.render(str(count), True, (255, 255, 255))  # White countdown number
            self.display.blit(countdown_surface, (self.display.get_width() // 2 - countdown_surface.get_width() // 2,
                                                  self.display.get_height() // 2 - countdown_surface.get_height() // 2))
            pygame.display.update()
            pygame.time.wait(1000)  # Wait 1 second for each countdown step

        pass

    def show_end_screen(self):
        self.display.fill((0, 0, 0))

        message = "You Win!" if self.rounds_completed >= self.max_rounds else "Game Over!"
        text_surface = self.font.render(message, True, (255, 255, 255))
        self.display.blit(text_surface,
                          (self.screen_width // 2 - text_surface.get_width() // 2, self.screen_height // 3))

        # Define Restart and Exit buttons
        self.restart_button = pygame.Rect(self.screen_width // 2 - 100, self.screen_height // 2, 200, 50)
        self.exit_button = pygame.Rect(self.screen_width // 2 - 100, self.screen_height // 2 + 70, 200, 50)

        if self.rounds_completed >= self.max_rounds:
            # If player wins, add a Next Level button
            self.next_level_button = pygame.Rect(self.screen_width // 2 - 100,
                                                 self.screen_height // 2 - 70, 200, 50)

            # Draw the Next Level button (Blue)
            pygame.draw.rect(self.display, (0, 0, 255), self.next_level_button)
            next_level_text = self.font.render("Next Level", True, (255, 255, 255))
            self.display.blit(next_level_text, (self.next_level_button.x + 50, self.next_level_button.y + 10))

        # Draw the Restart button (Green)
        pygame.draw.rect(self.display, (0, 128, 0), self.restart_button)
        restart_text = self.font.render("Restart", True, (255, 255, 255))
        self.display.blit(restart_text, (self.restart_button.x + 50, self.restart_button.y + 10))

        # Draw the Exit button (Red)
        pygame.draw.rect(self.display, (128, 0, 0), self.exit_button)
        exit_text = self.font.render("Exit", True, (255, 255, 255))
        self.display.blit(exit_text, (self.exit_button.x + 70, self.exit_button.y + 10))

    def run(self):
        if not self.is_restart:
            self.run_dialogue_strip_1()
            self.run_title_screen()
            self.run_dialogue_strip_2()
        else:
            self.is_restart = False
        self.show_how_to_play()
        self.start_countdown()
        self.current_time = self.time_limit
        self.last_time = pygame.time.get_ticks()  # Initialize last_time here
        running = True
        self.game_over = False
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif not self.game_over:  # Only handle gameplay input if the game is not over
                    if event.type == pygame.KEYDOWN:
                        # if event.key == pygame.K_ESCAPE:
                        #     self.gameStateManager.set_state('main-menu')
                        #     running = False
                        if event.key == pygame.K_RETURN:
                            if self.check_rhyme():
                                self.current_animation = 'attack'
                                self.reset_round()
                            else:
                                if self.lives <= 0:
                                    self.game_over = True
                                else:
                                    self.input_text = ''
                        elif event.key == pygame.K_BACKSPACE:
                            self.input_text = self.input_text[:-1]
                        else:
                            self.input_text += event.unicode
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if self.speaker_rect.collidepoint(event.pos):
                            self.pronounce_word()
                else:
                    # Handle clicks on the restart or exit buttons after the game is over
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.restart_button.collidepoint(event.pos):
                            # Restart the game
                            self.lives = 3
                            self.rounds_completed = 0
                            self.current_flower_word = self.flower_words[self.rounds_completed]
                            self.input_text = ''
                            self.current_time = self.time_limit
                            self.last_time = pygame.time.get_ticks()  # Reset last_time to the current time
                            self.timer_started = False  # Reset timer_started to False
                            self.game_over = False  # Exit end screen mode
                            self.is_restart = True
                        elif self.exit_button.collidepoint(event.pos):
                            self.gameStateManager.set_state('main-menu')
                            running = False
                        elif self.next_level_button.collidepoint(event.pos):
                            self.gameStateManager.set_state('sixth-level')
                            running = False

            # Update the warrior animation frame
            self.warrior_frame_time += self.clock.get_time() / 1000.0  # Increment frame time
            if self.warrior_frame_time >= self.warrior_animation_speed:  # Check if it's time to update the frame
                self.warrior_current_frame = (self.warrior_current_frame + 1) % len(
                    self.warrior_frames)  # Move to the next frame
                self.warrior_frame_time = 0  # Reset frame time

            # # Update the timer
            # time_passed = pygame.time.get_ticks() - self.last_time
            # self.current_time -= time_passed / 1000.0
            # self.last_time = pygame.time.get_ticks()

            if not self.game_over:
                if self.timer_started:  # Check if the timer has started
                    self.time_passed = pygame.time.get_ticks() - self.last_time
                    self.current_time -= self.time_passed / 1000.0
                    self.last_time = pygame.time.get_ticks()
                    print(self.current_time)
                    if self.current_time <= 0:
                        self.lives -= 1
                        print("deducts a life.")
                        if self.lives <= 0:
                            self.game_over = True
                        else:
                            self.reset_round()
                else:
                    self.timer_started = True  # Start the timer
                    self.last_time = pygame.time.get_ticks()  # Reset last_time

                # Update the warrior animation frame
                self.update_animation()

                    # Redraw everything
                self.display.blit(self.background, (0, 0))
                self.draw_hearts()
                self.draw_timer(self.current_time)
                self.draw_enemy()
                self.draw_text_box()
                self.draw_warrior()  # Draw animated warrior
                self.draw_speaker()

            else:
                    # Show the end screen
                self.show_end_screen()

            pygame.display.update()
            self.clock.tick(FPS)  # Cap frame rate at 60 FPS

class ForestOfNolite:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager
        self.light_radius = 100  # Define the radius of the light
        self.lives = 3  # Player starts with 3 lives
        self.words_to_find = ["firefly", "tower", "letter", "forest", "tree", "bush", "cave", "leaf", "word", "escape", "almost", "trap", "done"]  # Words to find
        self.word_index = 0  # Start with the first word
        self.correct_word = self.words_to_find[self.word_index]  # Word to find on screen
        self.engine = pyttsx3.init()  # Text-to-speech engine
        self.win = False
        self.gameOver = False
        self.is_game_initialized = False

        self.continue_button = pygame.Rect(self.display.get_width() // 2 - 100, self.display.get_height() - 100, 200,
                                           50)
        self.countdown_font = pygame.font.Font(None, 100)

        # Load background image
        background_image_path = os.path.join('graphics', 'forest-of-nolite-level-bgm.png')
        self.background_image = pygame.image.load(background_image_path).convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image, (self.display.get_width(), self.display.get_height()))

        bg_music_path = os.path.join('audio', 'night-forest-sound.mp3')
        self.bgm = pygame.mixer.Sound(bg_music_path)
        self.bgm.set_volume(0.4)
        self.bgm_isplaying = False

        heart_image_path = os.path.join('graphics', 'heart.png')
        self.heart_image = pygame.image.load(heart_image_path).convert_alpha()
        self.heart_image = pygame.transform.scale(self.heart_image, (80, 50))  # Resize heart

        # Create buttons (audio, left, right)
        # Load the audio button image
        self.audio_icon = pygame.image.load(os.path.join('graphics', 'audio-logo.png')).convert_alpha()
        self.audio_icon = pygame.transform.scale(self.audio_icon, (100, 100))  # Scale to a suitable size
        self.audio_button_rect = self.audio_icon.get_rect(topleft=((self.display.get_width()//2) - (100//2), 10))  # Position on screen
        self.left_arrow_image = pygame.image.load(os.path.join('graphics', 'left-arrow.png')).convert_alpha()
        self.right_arrow_image = pygame.image.load(os.path.join('graphics', 'right-arrow.png')).convert_alpha()

        # Scale the arrows to a desired size if needed
        self.left_arrow_image = pygame.transform.scale(self.left_arrow_image, (150, 75))  # Adjust size as needed
        self.right_arrow_image = pygame.transform.scale(self.right_arrow_image, (150, 75))

        # Define button rects
        self.left_button = self.left_arrow_image.get_rect(topleft=(50, self.display.get_height() - 100))
        self.right_button = self.right_arrow_image.get_rect(topleft=(self.display.get_width() - 200, self.display.get_height() - 100))

        # Font for displaying words
        self.font = pygame.font.Font(None, 40)
        screen_center_x = self.display.get_width() // 2  # Find the horizontal center of the screen
        left_side_limit = screen_center_x // 2  # Limit for placing the word on the left side
        right_side_limit = screen_center_x + (screen_center_x // 2)  # Limit for placing the word on the right side

        # Randomly choose whether to place the word on the left or right side
        if random.choice([True, False]):  # Randomly choose between left and right
            # Place the word on the left side
            word_x = random.randint(50, left_side_limit)  # Set x on the left half
        else:
            # Place the word on the right side
            word_x = random.randint(right_side_limit, self.display.get_width() - 50)  # Set x on the right half

        # y-coordinate remains random but within a safe range
        word_y = random.randint(100, self.display.get_height() - 200)

        self.word_position = (word_x, word_y)


    def read_word(self):
        # Read the current word aloud
        self.engine.say(self.correct_word)
        self.engine.runAndWait()

    def draw_hearts(self):
        """Draw remaining lives as heart icons."""
        for i in range(self.lives):
            self.display.blit(self.heart_image, (10 + i * 60, 10))  # Draw each heart with spacing

    def next_word(self):
        # Move to the next word
        self.word_index += 1
        if self.word_index >= len(self.words_to_find):
            print("Level completed!")
            self.win = True
        else:
            self.correct_word = self.words_to_find[self.word_index]
            self.word_position = (random.randint(100, self.display.get_width() - 200), random.randint(100, self.display.get_height() - 200))

    def lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            print("Game Over!")
            self.gameOver = True
        else:
            print(f"Lives remaining: {self.lives}")

    def run_title_screen(self):
        title_text = "FOREST OF NOLITE"
        font_path_1 = os.path.join('fonts', 'ARIALBLACKITALIC.TTF')
        font_path_2 = os.path.join('fonts', 'ARIAL.TTF')
        title_font = pygame.font.Font(font_path_1, 50)  # Large font for the title
        button_font = pygame.font.Font(font_path_2, 20)

        button_color = (255, 255, 0)  # Yellow color for the button
        button_hover_color = (200, 200, 0)  # Darker yellow for hover effect
        button_rect = pygame.Rect((self.display.get_width() // 2 - 100, self.display.get_height() // 2 + 50),
                                  (200, 50))  # Button dimensions

        running = True
        while running:
            self.display.fill((0, 0, 0))  # Fill the screen with black

            # Render the title text
            title_surface = title_font.render(title_text, True, (255, 255, 255))  # White color for the title
            title_rect = title_surface.get_rect(
                center=(self.display.get_width() // 2, self.display.get_height() // 2 - 50))
            self.display.blit(title_surface, title_rect)  # Blit title text

            # Check if the mouse is over the button
            mouse_pos = pygame.mouse.get_pos()  # Get the mouse position
            if button_rect.collidepoint(mouse_pos):
                current_button_color = button_hover_color  # Use hover color
            else:
                current_button_color = button_color  # Use normal color

            # Draw the button with the current color
            pygame.draw.rect(self.display, current_button_color, button_rect)  # Draw button
            button_text = button_font.render("Continue", True, (0, 0, 0))  # Black text for the button
            button_text_rect = button_text.get_rect(center=button_rect.center)  # Center text in button
            self.display.blit(button_text, button_text_rect)  # Blit button text

            # Event handling for button click
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        if button_rect.collidepoint(mouse_pos):  # Check if mouse is over the button
                            running = False  # Exit the loop to move to the next screen

            pygame.display.flip()
            pygame.time.Clock().tick(60)  # Control the frame rate

    def run_dialogue_strip_1(self):
        self.dialogue_font = pygame.font.Font(None, 36)

        # Dialogue list (narrating the FourthLevel)
        self.dialogue_lines = [
            "The Forest of Nolite was once full of light from thousands of fireflies.",
            "The fireflies made the forest beautiful, a special place in Dyscape.",
            "But then Confusion came and placed a curse on the forest.",
            "He filled the forest with dark smoke, scaring the fireflies away.",
            "Now, the forest is covered in darkness, and the light is gone.",
            "It is up to our adventurer and his friend owl to find the light and bring back the magic."
        ]

        # Corresponding images for each dialogue line
        self.dialogue_images = [
            pygame.image.load(os.path.join('graphics', 'forest-of-nolite.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'forest-of-nolite.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'forest-of-nolite-2.5.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'forest-of-nolite-2.5.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'forest-of-nolite-3.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'forest-of-nolite-3.png')).convert_alpha()
        ]

        # Corresponding narration files for each dialogue line
        self.dialogue_sounds = [
            pygame.mixer.Sound(os.path.join('audio', 'sixth-narrator-1.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'sixth-narrator-2.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'sixth-narrator-3.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'sixth-narrator-4.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'sixth-narrator-5.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'sixth-narrator-6.mp3'))
        ]

        # Scale the images to fit the screen
        self.dialogue_images = [
            pygame.transform.scale(img, (self.display.get_width(), self.display.get_height())) for img in
            self.dialogue_images
        ]

        self.dialogue_index = 0
        running = True

        # Initialize the mixer for playing audio
        pygame.mixer.init()

        # Flag to check if narration is playing
        self.narration_playing = False

        def play_narration():
            """Play the narration for the current dialogue line."""
            self.narration_playing = True
            self.dialogue_sounds[self.dialogue_index].play()
            pygame.time.set_timer(pygame.USEREVENT, int(self.dialogue_sounds[self.dialogue_index].get_length() * 1000))

        # Play the first narration automatically
        play_narration()

        while running:
            self.display.fill((0, 0, 0))  # Black background for the dialogue screen

            # Display the corresponding image
            self.display.blit(self.dialogue_images[self.dialogue_index], (0, 0))

            # Create and display the dialogue box
            dialogue_box_rect = pygame.Rect(0, self.display.get_height() - 150, self.display.get_width(), 150)
            pygame.draw.rect(self.display, (0, 0, 0), dialogue_box_rect)

            # Render the current dialogue line
            dialogue_text = self.dialogue_font.render(self.dialogue_lines[self.dialogue_index], True,
                                                      (255, 255, 255))  # White font
            dialogue_rect = dialogue_text.get_rect(
                center=(self.display.get_width() // 2, self.display.get_height() - 75))
            self.display.blit(dialogue_text, dialogue_rect)

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    sys.exit()

                # Allow the player to skip the narration and move to the next slide with the spacebar
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.dialogue_sounds[self.dialogue_index].stop()  # Stop the current narration
                        self.narration_playing = False
                        self.dialogue_index += 1
                        if self.dialogue_index >= len(self.dialogue_lines):
                            running = False  # End the dialogue and start the game
                        else:
                            play_narration()  # Play the next narration

                # Check if narration finished
                if event.type == pygame.USEREVENT and self.narration_playing:
                    self.narration_playing = False
                    self.dialogue_index += 1
                    if self.dialogue_index >= len(self.dialogue_lines):
                        running = False  # End the dialogue and start the game
                    else:
                        play_narration()  # Play the next narration

            pygame.display.update()

    def load_spritesheet(self,filename, frame_width, frame_height, scale_factor):
        # Load the sprite sheet image
        spritesheet = pygame.image.load(os.path.join('graphics', filename)).convert_alpha()
        # Get the width and height of the entire sprite sheet
        sheet_width, sheet_height = spritesheet.get_size()

        # Create a list to hold individual frames
        frames = []
        for y in range(0, sheet_height, frame_height):
            for x in range(0, sheet_width, frame_width):
                # Extract each frame by using a sub-surface
                frame = spritesheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
                # Scale the frame to make it larger
                scaled_frame = pygame.transform.scale(frame, (
                int(frame_width * scale_factor), int(frame_height * scale_factor)))
                frames.append(scaled_frame)

        return frames

    def run_dialogue_strip_2(self):
        # Initialize pygame's mixer for audio (if needed)
        pygame.mixer.init()

        # Load the owl sprite sheet and extract frames for animation
        owl_frames = self.load_spritesheet('owl-flying.png', 48, 48, scale_factor=6)
        owl_frame_index = 0  # Start with the first frame of the animation
        owl_animation_speed = 5  # Change the frame every 5 frames of the game loop

        # Load character images (only one image for the player)
        char1_image = pygame.image.load(os.path.join('graphics', 'character-avatar.png'))
        char1_image = pygame.transform.scale(char1_image, (200, 200))

        dialogue_data = [
            {"name": "You", "text": "Do we have to go through this forest?", "image": char1_image},
            {"name": "Lexi the Owl", "text": "Yes. This is the only path to the tower.", "audio": "owl-talking-38.mp3"},
            {"name": "You", "text": "Man, this gives me the creepy vibes.", "image": char1_image},
            {"name": "Lexi the Owl", "text": "This is a vibrant forest, traveler. Confusion drove away the fireflies", "audio": "owl-talking-39.mp3"},
            {"name": "Lexi the Owl", "text": "As a result, the bright forest became a dull one.", "audio": "owl-talking-40.mp3"},
            {"name": "Lexi the Owl", "text": "We have to save this forest, and its fireflies.", "audio": "owl-talking-41.mp3"},
            {"name": "Lexi the Owl", "text": "And we have to go through here.", "audio": "owl-talking-42.mp3"},
            {"name": "You", "text": "Thank God, I brought my flashlight.", "image": char1_image},
        ]

        # Preload audio files
        audio_files = {}
        for dialogue in dialogue_data:
            if "audio" in dialogue:
                audio_file = dialogue["audio"]
                audio_files[audio_file] = pygame.mixer.Sound(os.path.join("audio", audio_file))

        dialogue_box_height = 150  # Height of the dialogue box surface
        dialogue_font = pygame.font.Font(None, 32)  # Font for dialogue text
        name_font = pygame.font.Font(None, 36)  # Font for character names
        space_prompt_font = pygame.font.Font(None, 28)  # Font for "Press SPACE to continue"

        current_line = 0
        text_displayed = ""
        text_index = 0
        text_speed = 2  # Speed of text animation
        audio_played = False  # Flag to track if audio has been played for the current line
        current_sound = None  # Track the currently playing sound

        running = True
        clock = pygame.time.Clock()

        running = True
        clock = pygame.time.Clock()

        while running:
            self.display.blit(self.background_image, (0, 0))

            # Create the dialogue box at the bottom
            dialogue_box = pygame.Surface((self.display.get_width(), dialogue_box_height))
            dialogue_box.fill((255, 219, 172))  # Light background for the dialogue box
            dialogue_box_rect = dialogue_box.get_rect(topleft=(0, self.display.get_height() - dialogue_box_height))

            # Draw the brown border around the dialogue box
            border_color = (139, 69, 19)  # Brown color (RGB)
            border_thickness = 20  # Thickness of the border
            pygame.draw.rect(self.display, border_color, dialogue_box_rect.inflate(border_thickness, border_thickness),
                             border_thickness)

            # Get the current dialogue data
            current_dialogue = dialogue_data[current_line]
            character_name = current_dialogue["name"]
            character_text = current_dialogue["text"]
            antagonist = "Lexi the Owl"

            # Play the audio file if it exists and hasn't been played yet
            if "audio" in current_dialogue and not audio_played:
                audio_file = current_dialogue["audio"]
                if current_sound is not None:
                    current_sound.stop()  # Stop the currently playing sound if it exists
                current_sound = audio_files[audio_file]  # Get the new sound
                current_sound.play()  # Play the new audio
                audio_played = True  # Set the flag to True to prevent replaying the audio

            # Update owl animation (cycle through the frames)
            if character_name == antagonist:
                owl_frame_index = (owl_frame_index + 1) % (len(owl_frames) * owl_animation_speed)
                current_owl_frame = owl_frames[owl_frame_index // owl_animation_speed]
                self.display.blit(current_owl_frame, (950, self.display.get_height() - dialogue_box_height - 300))

            # Render the character image (player) if it's the player's turn
            else:
                self.display.blit(char1_image, (50, self.display.get_height() - dialogue_box_height - 200))

            # Render the character name inside the dialogue box (above the text)
            name_surface = name_font.render(character_name, True, BLACK)
            dialogue_box.blit(name_surface, (20, 10))  # Draw name near the top inside the dialogue box

            # Text animation (add one letter at a time)
            if text_index < len(character_text):
                text_index += text_speed  # Control how fast letters are added
                text_displayed = character_text[:text_index]
            else:
                text_displayed = character_text

            # Render the dialogue text below the name
            text_surface = dialogue_font.render(text_displayed, True, BLACK)
            dialogue_box.blit(text_surface, (20, 60))  # Draw the text inside the dialogue box below the name

            # Add "Press SPACE to continue." prompt at the bottom right
            if text_index >= len(character_text):  # Show prompt only if the text is fully displayed
                space_prompt_surface = space_prompt_font.render("Press SPACE to continue.", True, (100, 100, 100))
                dialogue_box.blit(space_prompt_surface,
                                  (dialogue_box.get_width() - space_prompt_surface.get_width() - 20,
                                   dialogue_box.get_height() - space_prompt_surface.get_height() - 10))

            # Draw the dialogue box on the screen with the brown border
            self.display.blit(dialogue_box, dialogue_box_rect.topleft)

            # Event handling for advancing the dialogue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:  # Only proceed on SPACE key
                        if text_index >= len(character_text):
                            # Move to the next line of dialogue if the text is fully displayed
                            current_line += 1
                            text_index = 0
                            text_displayed = ""
                            if current_line >= len(dialogue_data):
                                running = False  # Exit dialogue when all lines are done

            pygame.display.flip()
            clock.tick(60)  # Control the frame rate

    def show_how_to_play(self):
        """Displays the 'how to play' instructions with a start button."""
        # Load the how-to-play image and scale it
        how_to_play_image = pygame.image.load(os.path.join('graphics', 'how-to-play(forest-of-nolite).png')).convert_alpha()
        how_to_play_image = pygame.transform.scale(how_to_play_image, (1280, 720))  # Scale to 1280x720

        # Define the start button
        start_button_rect = pygame.Rect((self.display.get_width() // 2 - 100, 600), (200, 50))  # Centered button

        # Define colors
        normal_color = (255, 255, 0)  # Yellow
        hover_color = (200, 200, 0)  # Darker yellow

        running = True
        while running:
            self.display.fill((0, 0, 0))  # Fill the screen with black
            self.display.blit(how_to_play_image, (0, 0))  # Display the how-to-play image

            # Check if the mouse is over the button
            mouse_pos = pygame.mouse.get_pos()
            if start_button_rect.collidepoint(mouse_pos):
                button_color = hover_color  # Change to darker yellow on hover
            else:
                button_color = normal_color  # Normal yellow color

            # Draw the start button
            pygame.draw.rect(self.display, button_color, start_button_rect)  # Draw button with the appropriate color
            start_text = self.font.render("Start", True, (0, 0, 0))  # Black text
            start_text_rect = start_text.get_rect(center=start_button_rect.center)  # Center text in button
            self.display.blit(start_text, start_text_rect)  # Blit start text

            # Event handling for button click
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if start_button_rect.collidepoint(event.pos):  # Check if mouse is over the button
                        running = False  # Exit the loop to proceed to the next screen

            pygame.display.update()

    def start_countdown(self):
        """Displays a 3-2-1 countdown before the game starts."""
        for count in range(3, 0, -1):
            self.display.fill((0, 0, 0))  # Black background
            countdown_surface = self.countdown_font.render(str(count), True, (255, 255, 255))  # White countdown number
            self.display.blit(countdown_surface, (self.display.get_width() // 2 - countdown_surface.get_width() // 2,
                                                  self.display.get_height() // 2 - countdown_surface.get_height() // 2))
            pygame.display.update()
            pygame.time.wait(1000)  # Wait 1 second for each countdown step

        pass

    def restart_game(self):
        """Resets all values to start the game over."""
        # Reset player lives
        self.lives = 3
        self.font = pygame.font.Font(None, 40)

        # Reset the word index and choose the first word
        self.word_index = 0
        self.correct_word = self.words_to_find[self.word_index]

        # Reset game state variables
        self.win = False
        self.gameOver = False

        # Stop the background music
        if self.bgm_isplaying:
            self.bgm.stop()
            self.bgm_isplaying = False

        # Optionally, you can reset the position of the word if needed
        self.word_position = (random.randint(100, self.display.get_width() - 200),
                              random.randint(100, self.display.get_height() - 200))

        # Restart any other necessary game state variables
        # For example, you may want to reset the countdown timer if you have one
        # self.countdown_timer = initial_value

        # Optionally, restart the background music if desired
        self.bgm.play(-1)
        self.bgm_isplaying = True

        print("Game has been restarted.")

    def show_end_screen(self):
        """Displays the end screen with win/lose messages and buttons."""
        font_path = os.path.join('fonts', 'ARIAL.TTF')
        self.font = pygame.font.Font(font_path, 20)
        running = True
        while running:
            self.display.fill((0,0,0))  # Fill with background

            # Determine the message and button configurations
            if self.win:
                message = "You win!"
                next_level_button = pygame.Rect(self.display.get_width() // 2 - 100,
                                                self.display.get_height() // 2 - 50, 200, 50)
                restart_button = pygame.Rect(self.display.get_width() // 2 - 100, self.display.get_height() // 2 + 10,
                                             200, 50)
                main_menu_button = pygame.Rect(self.display.get_width() // 2 - 100, self.display.get_height() // 2 + 70,
                                               200, 50)
            else:  # Game over
                message = "You lose."
                restart_button = pygame.Rect(self.display.get_width() // 2 - 100, self.display.get_height() // 2, 200,
                                             50)
                main_menu_button = pygame.Rect(self.display.get_width() // 2 - 100, self.display.get_height() // 2 + 60,
                                               200, 50)

            # Render the message
            text_surface = self.font.render(message, True, (255, 255, 255))
            text_rect = text_surface.get_rect(
                center=(self.display.get_width() // 2, self.display.get_height() // 2 - 100))
            self.display.blit(text_surface, text_rect)

            # Draw buttons
            pygame.draw.rect(self.display, (0, 0, 255),
                             next_level_button if self.win else restart_button)  # Green button for next level or restart
            pygame.draw.rect(self.display, (0, 128, 0), restart_button)  # Orange button for restart
            pygame.draw.rect(self.display, (128, 0, 0), main_menu_button)  # Blue button for main menu

            # Render button texts
            if self.win:
                next_level_text = self.font.render("Next Level", True, (255, 255, 255))
                self.display.blit(next_level_text, (next_level_button.x + 50, next_level_button.y + 10))

            restart_text = self.font.render("Restart", True, (255, 255, 255))
            self.display.blit(restart_text, (restart_button.x + 65, restart_button.y + 10))

            main_menu_text = self.font.render("Main Menu", True, (255, 255, 255))
            self.display.blit(main_menu_text, (main_menu_button.x + 45, main_menu_button.y + 10))

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.win and next_level_button.collidepoint(event.pos):
                        # Load the next level (this would depend on how your levels are structured)
                        self.bgm.stop()
                        print("Loading next level...")
                        # Here you would call the method to load the next level
                        self.gameStateManager.set_state('seventh-level')
                        running = False  # Exit the end screen

                    if restart_button.collidepoint(event.pos):
                        print("Restarting level...")
                        # Restart the current level
                        # Here you would reset the game state to restart the level
                        self.restart_game()
                        running = False  # Exit the end screen

                    if main_menu_button.collidepoint(event.pos):
                        print("Returning to main menu...")
                        # Load the main menu
                        self.gameStateManager.set_state('main-menu')
                        running = False  # Exit the end screen

            pygame.display.update()

    def run(self):
        correct_answer_sound = pygame.mixer.Sound(os.path.join('audio', 'correct-answer.mp3'))
        wrong_answer_sound = pygame.mixer.Sound(os.path.join('audio', 'wrong-answer.mp3'))

        if not self.is_game_initialized:
            self.run_title_screen()
            self.run_dialogue_strip_1()
            self.run_dialogue_strip_2()
            self.is_game_initialized = True

        self.show_how_to_play()
        self.start_countdown()
        running = True
        while running:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Fill the display with the background image
            self.display.blit(self.background_image, (0, 0))
            if not self.bgm_isplaying:
                self.bgm.play(-1)
                print("bgm playing")
                self.bgm_isplaying = True

            # Draw the word with transparency (making it harder to see)
            word_surface = self.font.render(self.correct_word, True, (255, 255, 255))
            word_surface.set_alpha(40)  # Set transparency (0-255 scale, where 255 is fully opaque)
            self.display.blit(word_surface, self.word_position)

            # Create the pitch-black screen with light source around the cursor
            darkness = pygame.Surface(self.display.get_size(), pygame.SRCALPHA)
            darkness.fill((0, 0, 0, 255))  # Solid black covering the whole screen
            pygame.draw.circle(darkness, (0, 0, 0, 0), (mouse_x, mouse_y),
                               self.light_radius)  # Transparent circle around the cursor
            self.display.blit(darkness, (0, 0))

            # Position and blit the labels
            self.display.blit(self.audio_icon, self.audio_button_rect.topleft)
            self.display.blit(self.left_arrow_image, self.left_button.topleft)
            self.display.blit(self.right_arrow_image, self.right_button.topleft)
            # Draw the remaining hearts (lives)
            self.draw_hearts()

            # Determine whether the word is on the left or right side of the screen
            word_x, word_y = self.word_position
            screen_center_x = self.display.get_width() // 2

            word_is_on_left = word_x < screen_center_x
            word_is_on_right = word_x > screen_center_x

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.audio_button_rect.collidepoint(event.pos):
                        self.read_word()  # Play the audio of the word

                    elif self.left_button.collidepoint(event.pos):
                        if word_is_on_left:
                            print("Correct! Word is on the left.")
                            correct_answer_sound.play()
                            self.next_word()  # Move to the next word

                        else:
                            print("Incorrect! Word is not on the left.")
                            wrong_answer_sound.play()
                            self.lose_life()  # Lose a life

                    elif self.right_button.collidepoint(event.pos):
                        if word_is_on_right:
                            print("Correct! Word is on the right.")
                            correct_answer_sound.play()
                            self.next_word()  # Move to the next word

                        else:
                            print("Incorrect! Word is not on the right.")
                            wrong_answer_sound.play()
                            self.lose_life()  # Lose a life

            # Check if the game is over
            if self.win or self.gameOver:
                self.show_end_screen()  # Display the end screen
                running = False  # Exit the game loop

            pygame.display.update()

class EchoingChambers:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager
        self.display = pygame.display.set_mode((1280, 720))
        self.screen_width = 1280
        self.screen_height = 720
        self.countdown_font = pygame.font.Font(None, 100)
        self.is_restart = False

        self.font = pygame.font.SysFont('Arial', 36)
        self.button_font = pygame.font.SysFont('Arial', 25)

        # Load background, heart, speaker, and wood sign images with resizing
        self.background = pygame.image.load(os.path.join('graphics', 'cave.png')).convert_alpha()
        self.heart_image = pygame.transform.scale(
            pygame.image.load(os.path.join('graphics', 'heart.png')).convert_alpha(), (80, 50))
        self.speaker_icon = pygame.transform.scale(
            pygame.image.load(os.path.join('graphics', 'audio-logo.png')).convert_alpha(), (100, 100))

        # Separate left and right wood signs
        self.left_wood_sign = pygame.transform.scale(
            pygame.image.load(os.path.join('graphics', 'left-wood-sign.png')).convert_alpha(), (250, 250))
        self.right_wood_sign = pygame.transform.scale(
            pygame.image.load(os.path.join('graphics', 'right-wood-sign.png')).convert_alpha(), (250, 250))

        self.lives = 3
        self.current_round = 0
        self.game_over = False
        self.win = False
        self.overlay_color = None
        self.overlay_alpha = 0  # Alpha value for the overlay
        self.overlay_duration = 0  # Duration for the overlay

        # Define the list of words, choices, and correct answers
        self.words = [
            {"word": "RING", "choices": ["SING", "RING"], "correct": "RING"},
            {"word": "CAR", "choices": ["CAR", "JAR"], "correct": "CAR"},
            {"word": "MAP", "choices": ["CAP", "MAP"], "correct": "MAP"},
            {"word": "NAIL", "choices": ["NAIL", "MAIL"], "correct": "NAIL"},
            {"word": "WOOD", "choices": ["FOOD", "WOOD"], "correct": "WOOD"},
            {"word": "OWL", "choices": ["OWL", "BOWL"], "correct": "OWL"},
            {"word": "BIKE", "choices": ["LIKE", "BIKE"], "correct": "BIKE"},
            {"word": "BOOK", "choices": ["HOOK", "BOOK"], "correct": "BOOK"},
            {"word": "OIL", "choices": ["OIL", "FOIL"], "correct": "OIL"},
            {"word": "VAN", "choices": ["CAN", "VAN"], "correct": "VAN"}
        ]
        self.current_word_data = self.words[self.current_round]

        # Initialize pyttsx3 for text-to-speech
        self.tts_engine = pyttsx3.init()

        # Load choice images, resize them to fit on the wood signs
        self.choice_images = {choice: pygame.transform.scale(
            pygame.image.load(os.path.join('graphics', f'{choice.lower()}.png')).convert_alpha(), (110, 110)
        ) for word_data in self.words for choice in word_data["choices"]}

        # Set the positions for the left and right wood signs
        self.left_wood_sign_position = (self.screen_width * 0.1, 450)
        self.right_wood_sign_position = (self.screen_width * 0.7, 450)

        # Button positions for restart, next level, and exit
        self.restart_button = pygame.Rect(0, 0, 200, 60)
        self.next_level_button = pygame.Rect(0, 0, 200, 60)  # Next level button
        self.exit_button = pygame.Rect(0, 0, 200, 60)

    def run_title_screen(self):
        title_text = "ECHOING CHAMBERS"
        font_path_1 = os.path.join('fonts', 'ARIALBLACKITALIC.TTF')
        font_path_2 = os.path.join('fonts', 'ARIAL.TTF')
        title_font = pygame.font.Font(font_path_1, 50)  # Large font for the title
        button_font = pygame.font.Font(font_path_2, 20)

        button_color = (255, 255, 0)  # Yellow color for the button
        button_hover_color = (200, 200, 0)  # Darker yellow for hover effect
        button_rect = pygame.Rect((self.display.get_width() // 2 - 100, self.display.get_height() // 2 + 50),
                                  (200, 50))  # Button dimensions

        running = True
        while running:
            self.display.fill((0, 0, 0))  # Fill the screen with black

            # Render the title text
            title_surface = title_font.render(title_text, True, (255, 255, 255))  # White color for the title
            title_rect = title_surface.get_rect(
                center=(self.display.get_width() // 2, self.display.get_height() // 2 - 50))
            self.display.blit(title_surface, title_rect)  # Blit title text

            # Check if the mouse is over the button
            mouse_pos = pygame.mouse.get_pos()  # Get the mouse position
            if button_rect.collidepoint(mouse_pos):
                current_button_color = button_hover_color  # Use hover color
            else:
                current_button_color = button_color  # Use normal color

            # Draw the button with the current color
            pygame.draw.rect(self.display, current_button_color, button_rect)  # Draw button
            button_text = button_font.render("Continue", True, (0, 0, 0))  # Black text for the button
            button_text_rect = button_text.get_rect(center=button_rect.center)  # Center text in button
            self.display.blit(button_text, button_text_rect)  # Blit button text

            # Event handling for button click
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        if button_rect.collidepoint(mouse_pos):  # Check if mouse is over the button
                            running = False  # Exit the loop to move to the next screen

            pygame.display.flip()
            pygame.time.Clock().tick(60)  # Control the frame rate

    def run_dialogue_strip_1(self):
        self.dialogue_font = pygame.font.Font(None, 36)

        # Dialogue list (narrating the FourthLevel)
        self.dialogue_lines = [
            "Escaped the darkness of the forest, they finally had the glimpse of the kingdom of Dyscape. The kingdom that had fallen into Confusion’s hands.",
            "They continued their journey despite the cruel thunderstorms and heavy raindrops pouring in their way.",
            "Running and looking for a shelter, they stumbled upon a cave and decided to take a rest there.",
            "The traveler observed that this isn’t one of the usual caves. Each guide leads to a different path.",
            "Not knowing what lies inside the enormous cave, Traveler and Lexi will once again bravely face the unknown.",
        ]

        # Corresponding images for each dialogue line
        self.dialogue_images = [
            pygame.image.load(os.path.join('graphics', 'to-echoing-chambers-1.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'to-echoing-chambers-2.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'to-echoing-chambers-3.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'to-echoing-chambers-3.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'to-echoing-chambers-4.png')).convert_alpha(),

        ]

        # Corresponding narration files for each dialogue line
        self.dialogue_sounds = [
            pygame.mixer.Sound(os.path.join('audio', 'seventh-narrator-1.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'seventh-narrator-2.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'seventh-narrator-3.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'seventh-narrator-4.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'seventh-narrator-5.mp3')),
        ]

        # Scale the images to fit the screen
        self.dialogue_images = [
            pygame.transform.scale(img, (self.display.get_width(), self.display.get_height() - 150)) for img in
            self.dialogue_images
        ]

        self.dialogue_index = 0
        running = True

        # Initialize the mixer for playing audio
        pygame.mixer.init()

        # Flag to check if narration is playing
        self.narration_playing = False

        def play_narration():
            """Play the narration for the current dialogue line."""
            self.narration_playing = True
            self.dialogue_sounds[self.dialogue_index].play()
            pygame.time.set_timer(pygame.USEREVENT,
                                  int(self.dialogue_sounds[self.dialogue_index].get_length() * 1000))

        # Play the first narration automatically
        play_narration()

        while running:
            self.display.fill((0, 0, 0))  # Black background for the dialogue screen

            # Display the corresponding image
            self.display.blit(self.dialogue_images[self.dialogue_index], (0, 0))

            # Create and display the dialogue box
            dialogue_box_rect = pygame.Rect(0, self.display.get_height() - 150, self.display.get_width(), 150)
            pygame.draw.rect(self.display, (0, 0, 0), dialogue_box_rect)

            # Render the current dialogue line
            dialogue_text = self.dialogue_font.render(self.dialogue_lines[self.dialogue_index], True,
                                                      (255, 255, 255))  # White font
            dialogue_rect = dialogue_text.get_rect(
                center=(self.display.get_width() // 2, self.display.get_height() - 75))
            self.display.blit(dialogue_text, dialogue_rect)

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    sys.exit()

                # Allow the player to skip the narration and move to the next slide with the spacebar
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.dialogue_sounds[self.dialogue_index].stop()  # Stop the current narration
                        self.narration_playing = False
                        self.dialogue_index += 1
                        if self.dialogue_index >= len(self.dialogue_lines):
                            running = False  # End the dialogue and start the game
                        else:
                            play_narration()  # Play the next narration

                # Check if narration finished
                if event.type == pygame.USEREVENT and self.narration_playing:
                    self.narration_playing = False
                    self.dialogue_index += 1
                    if self.dialogue_index >= len(self.dialogue_lines):
                        running = False  # End the dialogue and start the game
                    else:
                        play_narration()  # Play the next narration

            pygame.display.update()

    def show_how_to_play(self):
        """Displays the 'how to play' instructions with a start button."""
        # Load the how-to-play image and scale it
        how_to_play_image = pygame.image.load(
            os.path.join('graphics', 'how-to-play(echoing-chambers).png')).convert_alpha()
        how_to_play_image = pygame.transform.scale(how_to_play_image, (1280, 720))  # Scale to 1280x720

        # Define the start button
        start_button_rect = pygame.Rect((self.display.get_width() // 2 - 100, 650), (200, 50))  # Centered button

        # Define colors
        normal_color = (255, 255, 0)  # Yellow
        hover_color = (200, 200, 0)  # Darker yellow

        running = True
        while running:
            self.display.fill((0, 0, 0))  # Fill the screen with black
            self.display.blit(how_to_play_image, (0, 0))  # Display the how-to-play image

            # Check if the mouse is over the button
            mouse_pos = pygame.mouse.get_pos()
            if start_button_rect.collidepoint(mouse_pos):
                button_color = hover_color  # Change to darker yellow on hover
            else:
                button_color = normal_color  # Normal yellow color

            # Draw the start button
            pygame.draw.rect(self.display, button_color,
                             start_button_rect)  # Draw button with the appropriate color
            start_text = self.font.render("Start", True, (0, 0, 0))  # Black text
            start_text_rect = start_text.get_rect(center=start_button_rect.center)  # Center text in button
            self.display.blit(start_text, start_text_rect)  # Blit start text

            # Event handling for button click
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if start_button_rect.collidepoint(event.pos):  # Check if mouse is over the button
                        running = False  # Exit the loop to proceed to the next screen

            pygame.display.update()

    def start_countdown(self):
        """Displays a 3-2-1 countdown before the game starts."""
        for count in range(3, 0, -1):
            self.display.fill((0, 0, 0))  # Black background
            countdown_surface = self.countdown_font.render(str(count), True,
                                                           (255, 255, 255))  # White countdown number
            self.display.blit(countdown_surface,
                              (self.display.get_width() // 2 - countdown_surface.get_width() // 2,
                               self.display.get_height() // 2 - countdown_surface.get_height() // 2))
            pygame.display.update()
            pygame.time.wait(1000)  # Wait 1 second for each countdown step

        pass

    def speak_word(self, word):
        """Use pyttsx3 to pronounce the word."""
        self.tts_engine.say(word)
        self.tts_engine.runAndWait()

    def next_round(self):
        """Proceed to the next round or end the game if all rounds are done."""
        self.current_round += 1
        if self.current_round >= len(self.words):
            self.win = True
        else:
            self.current_word_data = self.words[self.current_round]

    def restart_level(self):
        """Reset all level values to restart the level."""
        self.lives = 3
        self.current_round = 0
        self.game_over = False
        self.win = False
        self.current_word_data = self.words[self.current_round]
        self.is_restart = True

    def show_overlay(self, color):
        """Display a transparent overlay for a short duration."""
        self.overlay_color = color
        self.overlay_alpha = 75  # Set the initial alpha value
        self.overlay_duration = 30  # Set the duration (frames)

    def run(self):
        if not self.is_restart:
            self.run_title_screen()
        else:
            self.is_restart = False
        self.show_how_to_play()
        self.start_countdown()

        """Main game loop for the seventh level."""
        correct_answer_sound = pygame.mixer.Sound(os.path.join('audio', 'correct-answer.mp3'))
        wrong_answer_sound = pygame.mixer.Sound(os.path.join('audio', 'wrong-answer.mp3'))



        running = True
        clock = pygame.time.Clock()
        while running:
            self.display.blit(self.background, (0, 0))

            # Display lives (hearts) resized to 50x50
            for i in range(self.lives):
                self.display.blit(self.heart_image, (10 + i * 60, 10))

            # Display speaker icon resized to 60x60
            speaker_icon_rect = self.speaker_icon.get_rect(center=(self.screen_width // 2, 80))
            self.display.blit(self.speaker_icon, speaker_icon_rect)

            # Display left wood sign
            self.display.blit(self.left_wood_sign, self.left_wood_sign_position)

            # Display right wood sign
            self.display.blit(self.right_wood_sign, self.right_wood_sign_position)

            # Resize and center the choice image on the left wood sign
            left_choice = self.current_word_data["choices"][0]
            left_image_rect = self.choice_images[left_choice].get_rect(
                center=(self.left_wood_sign_position[0] + 125, self.left_wood_sign_position[1] + 85))
            self.display.blit(self.choice_images[left_choice], left_image_rect)

            # Resize and center the choice image on the right wood sign
            right_choice = self.current_word_data["choices"][1]
            right_image_rect = self.choice_images[right_choice].get_rect(
                center=(self.right_wood_sign_position[0] + 125, self.right_wood_sign_position[1] + 85))
            self.display.blit(self.choice_images[right_choice], right_image_rect)

            mouse_pos = pygame.mouse.get_pos()

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if speaker_icon_rect.collidepoint(mouse_pos):
                        self.speak_word(self.current_word_data["word"])  # Speak the word when speaker icon is clicked

                    # Check if the player clicked the left or right wood sign
                    if left_image_rect.collidepoint(mouse_pos):
                        if left_choice == self.current_word_data["correct"]:
                            correct_answer_sound.play()
                            self.show_overlay((0, 255, 0))  # Show green overlay for correct answer
                            self.next_round()  # Proceed to the next round if correct
                        else:
                            wrong_answer_sound.play()
                            self.show_overlay((255, 0, 0))  # Show red overlay for incorrect answer
                            self.lives -= 1  # Deduct a life if incorrect
                    elif right_image_rect.collidepoint(mouse_pos):
                        if right_choice == self.current_word_data["correct"]:
                            correct_answer_sound.play()
                            self.show_overlay((0, 255, 0))  # Show green overlay for correct answer
                            self.next_round()  # Proceed to the next round if correct
                        else:
                            wrong_answer_sound.play()
                            self.show_overlay((255, 0, 0))  # Show red overlay for incorrect answer
                            self.lives -= 1  # Deduct a life if incorrect

            # Update overlay
            if self.overlay_alpha > 0:
                s = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
                s.fill((self.overlay_color[0], self.overlay_color[1], self.overlay_color[2], self.overlay_alpha))
                self.display.blit(s, (0, 0))
                self.overlay_alpha -= 4  # Decrease alpha value
                self.overlay_duration -= 1  # Decrease duration
                if self.overlay_duration <= 0:
                    self.overlay_alpha = 0  # Reset alpha value

            # Check game over condition
            if self.lives <= 0:
                self.game_over = True
                self.show_end_screen()
                running = False

            # Check win condition
            if self.win:
                self.show_end_screen()
                running = False

            pygame.display.update()
            clock.tick(FPS)

    def show_end_screen(self):
        """Display the end screen based on win/lose state."""
        font_path = os.path.join('fonts', 'ARIAL.TTF')
        font = pygame.font.Font(font_path, 20)
        if self.win:
            text = font.render("You Win!", True, (255, 255, 255))
            self.display.fill((0, 0, 0))
            self.display.blit(text,
                              (self.display.get_width() // 2 - text.get_width() // 2, self.display.get_height() // 3))

            # Calculate button positions with adjusted start_y to lower the buttons
            button_width = 200
            button_height = 60
            button_gap = 20
            total_button_height = button_height * 3 + button_gap * 2
            start_y = self.screen_height // 2 - total_button_height // 2 + 50  # Lower buttons by 50 pixels

            self.next_level_button.x = self.screen_width // 2 - button_width // 2
            self.next_level_button.y = start_y
            self.restart_button.x = self.screen_width // 2 - button_width // 2
            self.restart_button.y = start_y + button_height + button_gap
            self.exit_button.x = self.screen_width // 2 - button_width // 2
            self.exit_button.y = start_y + 2 * (button_height + button_gap)

            # Draw buttons with fill colors
            pygame.draw.rect(self.display, (0, 0, 255), self.next_level_button)  # Blue fill for Next Level button
            pygame.draw.rect(self.display, (0, 128, 0), self.restart_button)  # Green fill for Restart button
            pygame.draw.rect(self.display, (128, 0, 0), self.exit_button)  # Red fill for Exit button

            # Button text
            # font = pygame.font.Font(os.path.join('fonts', 'ARIAL.TTF'), 36)
            next_level_text = font.render("Next Level", True, (255, 255, 255))
            restart_text = font.render("Restart", True, (255, 255, 255))
            exit_text = font.render("Exit", True, (255, 255, 255))

            # Center text in each button
            self.display.blit(next_level_text, (
                self.next_level_button.x + (button_width - next_level_text.get_width()) // 2,
                self.next_level_button.y + (button_height - next_level_text.get_height()) // 2
            ))
            self.display.blit(restart_text, (
                self.restart_button.x + (button_width - restart_text.get_width()) // 2,
                self.restart_button.y + (button_height - restart_text.get_height()) // 2
            ))
            self.display.blit(exit_text, (
                self.exit_button.x + (button_width - exit_text.get_width()) // 2,
                self.exit_button.y + (button_height - exit_text.get_height()) // 2
            ))

            pygame.display.update()

            # Button event handling
            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()
                        if self.next_level_button.collidepoint(mouse_pos):
                            # Go to the next level
                            self.gameStateManager.set_state('eighth-level')
                            running = False
                        elif self.restart_button.collidepoint(mouse_pos):
                            # Restart the current level
                            self.restart_level()
                            running = False
                        elif self.exit_button.collidepoint(mouse_pos):
                            # Exit the game
                            self.gameStateManager.set_state('main-menu')
                            running = False
        else:
            text = font.render("Game Over!", True, (255, 255, 255))
            self.display.fill((0, 0, 0))
            self.display.blit(text,
                              (self.display.get_width() // 2 - text.get_width() // 2, self.display.get_height() // 3))

            # Calculate button positions
            button_width = 200
            button_height = 60
            button_gap = 20
            total_button_height = button_height * 2 + button_gap
            start_y = self.screen_height // 2 - total_button_height // 2

            self.restart_button.x = self.screen_width // 2 - button_width // 2
            self.restart_button.y = start_y
            self.exit_button.x = self.screen_width // 2 - button_width // 2
            self.exit_button.y = start_y + button_height + button_gap

            # Draw buttons with fill colors
            pygame.draw.rect(self.display, (0, 128, 0), self.restart_button)  # Green fill for Restart button
            pygame.draw.rect(self.display, (128, 0, 0), self.exit_button)  # Red fill for Exit button

            # Button text
            # font = pygame.font.Font(None, 36)
            restart_text = font.render("Restart", True, (255, 255, 255))
            exit_text = font.render("Exit", True, (255, 255, 255))

            # Center text within each button
            self.display.blit(restart_text, (
                self.restart_button.x + (button_width - restart_text.get_width()) // 2,
                self.restart_button.y + (button_height - restart_text.get_height()) // 2
            ))
            self.display.blit(exit_text, (
                self.exit_button.x + (button_width - exit_text.get_width()) // 2,
                self.exit_button.y + (button_height - exit_text.get_height()) // 2
            ))

            pygame.display.update()

            # Button event handling
            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()
                        if self.restart_button.collidepoint(mouse_pos):
                            # Restart the current level
                            self.restart_level()
                            running = False
                        elif self.exit_button.collidepoint(mouse_pos):
                            # Exit the game
                            self.gameStateManager.set_state('main-menu')
                            running = False

class EighthLevel:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager
        self.lives = 3
        self.current_gate = 1
        self.win = False
        self.game_over = False
        self.end_screen_displayed = False  # Flag to track if end screen has been displayed
        self.is_restart = False


        # Initialize the TTS engine
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)

        # Calculate the center of the screen
        self.screen_width, self.screen_height = self.display.get_size()
        self.center_x = self.screen_width // 2
        self.center_y = self.screen_height // 2

        # Load the audio logo image
        self.audio_logo_image = pygame.image.load(os.path.join('graphics', 'audio-logo.png')).convert_alpha()
        self.audio_logo_rect = self.audio_logo_image.get_rect(center=(self.center_x, 60))  # Centered at the top

        self.heart_image = pygame.image.load(os.path.join('graphics', 'heart.png')).convert_alpha()
        self.heart_image = pygame.transform.scale(self.heart_image, (80, 50))

        # Lamp animation parameters
        self.lamp_opacity = 120
        self.opacity_increasing = True
        self.lamp_positions = [(275, 265), (982, 272)]

        # Slot and word settings
        self.slot_width = 60
        self.slot_height = 40
        self.slot_gap = 20
        self.word_width = 60
        self.word_height = 40
        self.word_gap = 20

        # Load background image
        background_image_path = os.path.join('graphics', 'test-bg.png')
        self.background_image = pygame.image.load(background_image_path).convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image,
                                                       (self.display.get_width(), self.display.get_height()))

        # List of sentence segmenting rounds
        self.rounds = [
            {"sentence": "Iwenttothestore", "words": ["I", "went", "to", "the", "store"],
             "correct-sentence": "I went to the store"},
            {"sentence": "Heplaysintheyard", "words": ["He", "plays", "in", "the", "yard"],
             "correct-sentence": "He plays in the yard"},
            {"sentence": "Weclimbonthehill", "words": ["We", "climb", "on", "the", "hill"],
             "correct-sentence": "We climb on the hill"},
            {"sentence": "Thecatjumpshigh", "words": ["The", "cat", "jumps", "high"],
             "correct-sentence": "The cat jumps high"}
        ]

        # List of syllable segmenting rounds
        self.syllable_rounds = [
            {"word": "banana", "syllables": ["ba", "na", "na"]},
            {"word": "butterfly", "syllables": ["but", "ter", "fly"]},
            {"word": "telephone", "syllables": ["te", "le", "phone"]},
            {"word": "hospital", "syllables": ["hos", "pi", "tal"]},
        ]
        self.word_images = {
            'banana': pygame.image.load('graphics/banana.png'),
            'butterfly': pygame.image.load('graphics/butterfly.png'),
            'telephone': pygame.image.load('graphics/telephone.png'),
            'hospital': pygame.image.load('graphics/hospital.png'),
        }

        self.correct_slots = []
        self.last_answer = []
        self.current_round = 0
        self.is_syllable_round = False
        self.load_round()

        # Cutscene attributes
        self.cutscene_frames = self.load_cutscene_frames()
        self.cutscene_index = 0
        self.is_playing_cutscene = False
        self.cutscene_done = False
        self.cutscene_frame_delay = 100  # Delay in milliseconds between frames
        self.last_frame_time = pygame.time.get_ticks()  # Initialize the last frame time

    def load_spritesheet(self, filename, frame_width, frame_height, scale_factor):
        # Load the sprite sheet image
        spritesheet = pygame.image.load(os.path.join('graphics', filename)).convert_alpha()
        # Get the width and height of the entire sprite sheet
        sheet_width, sheet_height = spritesheet.get_size()

        # Create a list to hold individual frames
        frames = []
        for y in range(0, sheet_height, frame_height):
            for x in range(0, sheet_width, frame_width):
                # Extract each frame by using a sub-surface
                frame = spritesheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
                # Scale the frame to make it larger
                scaled_frame = pygame.transform.scale(frame, (
                    int(frame_width * scale_factor), int(frame_height * scale_factor)))
                frames.append(scaled_frame)

        return frames

    def run_dialogue_strip(self):
        self.dialogue_font = pygame.font.Font(None, 36)

        # Dialogue list (narrating the FourthLevel)
        self.dialogue_lines = [
            "After how many hours, they reached the center of Dyscape. And finally, reached the foot of the tower. ",
            "Lexi and the adventurer climbed the very long stairs of the tower despite the weather being dark and windy.",
            "As they reached the entrance, their eyes wandered as they look for the door to the top.",
            "They saw only one passageway, and as they approached it, they were shocked.",
            "They are blocked by a very big gate that is locked and has some kind of puzzle in it."
        ]

        # Corresponding images for each dialogue line
        self.dialogue_images = [
            pygame.image.load(os.path.join('graphics', 'reached-the-tower-1.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'reached-the-tower-2.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'reached-the-tower-3.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'reached-the-tower-4.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'reached-the-tower-5.png')).convert_alpha(),
        ]

        # Corresponding narration files for each dialogue line
        self.dialogue_sounds = [
            pygame.mixer.Sound(os.path.join('audio', 'eighth-narrator-1.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'eighth-narrator-2.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'eighth-narrator-3.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'eighth-narrator-4.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'eighth-narrator-5.mp3')),
        ]

        # Scale the images to fit the screen
        self.dialogue_images = [
            pygame.transform.scale(img, (self.display.get_width(), self.display.get_height() - 150)) for img in
            self.dialogue_images
        ]

        self.dialogue_index = 0
        running = True

        # Initialize the mixer for playing audio
        pygame.mixer.init()

        # Flag to check if narration is playing
        self.narration_playing = False

        def play_narration():
            """Play the narration for the current dialogue line."""
            self.narration_playing = True
            self.dialogue_sounds[self.dialogue_index].play()
            pygame.time.set_timer(pygame.USEREVENT, int(self.dialogue_sounds[self.dialogue_index].get_length() * 1000))

        # Stop any currently playing narration before starting the new one
        for sound in self.dialogue_sounds:
            sound.stop()

        # Play the first narration automatically
        play_narration()

        while running:
            self.display.fill((0, 0, 0))  # Black background for the dialogue screen

            # Display the corresponding image
            self.display.blit(self.dialogue_images[self.dialogue_index], (0, 0))

            # Create and display the dialogue box
            dialogue_box_rect = pygame.Rect(0, self.display.get_height() - 150, self.display.get_width(), 150)
            pygame.draw.rect(self.display, (0, 0, 0), dialogue_box_rect)

            # Render the current dialogue line
            dialogue_text = self.dialogue_font.render(self.dialogue_lines[self.dialogue_index], True,
                                                      (255, 255, 255))  # White font
            dialogue_rect = dialogue_text.get_rect(
                center=(self.display.get_width() // 2, self.display.get_height() - 75))
            self.display.blit(dialogue_text, dialogue_rect)

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    sys.exit()

                # Allow the player to skip the narration and move to the next slide with the spacebar
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.dialogue_sounds[self.dialogue_index].stop()  # Stop the current narration
                        self.narration_playing = False
                        self.dialogue_index += 1
                        if self.dialogue_index >= len(self.dialogue_lines):
                            running = False  # End the dialogue and start the game
                        else:
                            play_narration()  # Play the next narration

                # Check if narration finished
                if event.type == pygame.USEREVENT and self.narration_playing:
                    self.narration_playing = False
                    self.dialogue_index += 1
                    if self.dialogue_index >= len(self.dialogue_lines):
                        running = False  # End the dialogue and start the game
                    else:
                        play_narration()  # Play the next narration

            pygame.display.update()

    def run_dialogue_strip_1(self):
        # Initialize pygame's mixer for audio (if needed)
        pygame.mixer.init()

        # Load the owl sprite sheet and extract frames for animation
        owl_frames = self.load_spritesheet('owl-flying.png', 48, 48, scale_factor=6)
        owl_frame_index = 0  # Start with the first frame of the animation
        owl_animation_speed = 5  # Change the frame every 5 frames of the game loop

        # Load character images (only one image for the player)
        char1_image = pygame.image.load(os.path.join('graphics', 'character-avatar.png'))
        char1_image = pygame.transform.scale(char1_image, (200, 200))

        dialogue_data = [
            {"name": "You", "text": "The king was really loved by the people that they put out a very secure tower for him.", "image": char1_image},
            {"name": "Magical Owl", "text": "You're right about that. Unfortunately, Confusion was just too powerful\n that this gate dont have a chance."},
            {"name": "You", "text": "I can't wait to defeat him.", "image": char1_image},
            {"name": "Magical Owl", "text": "Yes. I know. But for now, let's focus at the task at hand."},
            {"name": "Magical Owl", "text": "This is the GATES OF ALPHA-BETA. A tightly secure set of gates that lead to the top of the tower."},
            {"name": "You", "text": "Set of gates? So it's just not a single gate?", "image": char1_image},
            {"name": "Magical Owl", "text": "Yes. It is a set of EIGHT gates all lined up. Do you see how secured this is?"},
            {"name": "You", "text": "Wow! That is some amazing architecture.", "image": char1_image},
            {"name": "Magical Owl", "text": "Moreover, each gate has its own unique way of opening it."},
            {"name": "Magical Owl", "text": "Each gate has its own puzzle that needs to be solved for it to be opened."},
            {"name": "You", "text": "So we just to solve all 8 problems to get trough?", "image": char1_image},
            {"name": "Magical Owl", "text": "You're right, adventurer! Are you ready to go?"},
            {"name": "You", "text": "Let's get it on!", "image": char1_image},
        ]

        # Preload audio files
        audio_files = {}
        for dialogue in dialogue_data:
            if "audio" in dialogue:
                audio_file = dialogue["audio"]
                audio_files[audio_file] = pygame.mixer.Sound(os.path.join("audio", audio_file))

        dialogue_box_height = 150  # Height of the dialogue box surface
        dialogue_font = pygame.font.Font(None, 32)  # Font for dialogue text
        name_font = pygame.font.Font(None, 36)  # Font for character names
        space_prompt_font = pygame.font.Font(None, 28)  # Font for "Press SPACE to continue"

        current_line = 0
        text_displayed = ""
        text_index = 0
        text_speed = 2  # Speed of text animation
        audio_played = False  # Flag to track if audio has been played for the current line
        current_sound = None  # Track the currently playing sound

        running = True
        clock = pygame.time.Clock()

        while running:
            self.display.blit(self.background_image, (0, 0))

            # Create the dialogue box at the bottom
            dialogue_box = pygame.Surface((self.display.get_width(), dialogue_box_height))
            dialogue_box.fill((255, 219, 172))  # Light background for the dialogue box
            dialogue_box_rect = dialogue_box.get_rect(topleft=(0, self.display.get_height() - dialogue_box_height))

            # Draw the brown border around the dialogue box
            border_color = (139, 69, 19)  # Brown color (RGB)
            border_thickness = 20  # Thickness of the border
            pygame.draw.rect(self.display, border_color, dialogue_box_rect.inflate(border_thickness, border_thickness),
                             border_thickness)

            # Get the current dialogue data
            current_dialogue = dialogue_data[current_line]
            character_name = current_dialogue["name"]
            character_text = current_dialogue["text"]
            antagonist = "Magical Owl"

            # Play the audio file if it exists and hasn't been played yet
            if "audio" in current_dialogue and not audio_played:
                audio_file = current_dialogue["audio"]
                if current_sound is not None:
                    current_sound.stop()  # Stop the currently playing sound if it exists
                current_sound = audio_files[audio_file]  # Get the new sound
                current_sound.play()  # Play the new audio
                audio_played = True  # Set the flag to True to prevent replaying the audio

            # Update owl animation (cycle through the frames)
            if character_name == antagonist or character_name == "Lexi the Owl":
                owl_frame_index = (owl_frame_index + 1) % (len(owl_frames) * owl_animation_speed)
                current_owl_frame = owl_frames[owl_frame_index // owl_animation_speed]
                self.display.blit(current_owl_frame, (950, self.display.get_height() - dialogue_box_height - 300))

            # Render the character image (player) if it's the player's turn
            else:
                self.display.blit(char1_image, (50, self.display.get_height() - dialogue_box_height - 200))

            # Render the character name inside the dialogue box (above the text)
            name_surface = name_font.render(character_name, True, (0,0,0))
            dialogue_box.blit(name_surface, (20, 10))  # Draw name near the top inside the dialogue box

            # Text animation (add one letter at a time)
            if text_index < len(character_text):
                text_index += text_speed  # Control how fast letters are added
                text_displayed = character_text[:text_index]
            else:
                text_displayed = character_text

            # Render the dialogue text below the name
            text_surface = dialogue_font.render(text_displayed, True, (0,0,0))
            dialogue_box.blit(text_surface, (20, 60))  # Draw the text inside the dialogue box below the name

            # Add "Press SPACE to continue." prompt at the bottom right
            if text_index >= len(character_text):  # Show prompt only if the text is fully displayed
                space_prompt_surface = space_prompt_font.render("Press SPACE to continue.", True, (100, 100, 100))
                dialogue_box.blit(space_prompt_surface,
                                  (dialogue_box.get_width() - space_prompt_surface.get_width() - 20,
                                   dialogue_box.get_height() - space_prompt_surface.get_height() - 10))

            # Draw the dialogue box on the screen with the brown border
            self.display.blit(dialogue_box, dialogue_box_rect.topleft)

            # Event handling for advancing the dialogue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:  # Only proceed on SPACE key
                        if text_index >= len(character_text):
                            # Move to the next line of dialogue if the text is fully displayed
                            current_line += 1
                            text_index = 0
                            text_displayed = ""
                            audio_played = False  # Reset the audio flag for the next line
                            if current_line >= len(dialogue_data):
                                running = False  # Exit dialogue when all lines are done

            pygame.display.flip()
            clock.tick(60)  # Control the frame rate

    def load_cutscene_frames(self):
        # Load and split the gate-open-animation sprite sheet into individual frames
        cutscene_frames = []
        sprite_sheet_path = os.path.join('graphics', 'gate-open-animation.png')
        sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()

        # Assume 25 frames, each 1280x720
        for i in range(25):
            frame = sprite_sheet.subsurface((i * 1280, 0, 1280, 720))
            cutscene_frames.append(frame)

        return cutscene_frames

    def load_round(self):
        # print("Loading round...")  # Debugging line
        if not self.is_syllable_round:
            round_data = self.rounds[self.current_round]
            self.sentence = round_data["sentence"]
            self.words = round_data["words"]
            self.correct_sentence = round_data["correct-sentence"]
            self.correct_slots = self.words[:]  # Store the correct order for this round
        else:
            round_data = self.syllable_rounds[self.current_round]
            self.sentence = round_data["word"]
            self.words = round_data["syllables"]
            self.correct_slots = self.words[:]  # Store the correct order for this round

        self.word_slots = [None] * len(self.words)
        self.dragging_word = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        # Calculate slot positions
        self.slot_positions = []
        for i in range(len(self.words)):
            slot_x = self.center_x - (len(self.words) * (self.slot_width + self.slot_gap)) // 2 + i * (
                    self.slot_width + self.slot_gap)
            slot_y = self.center_y - (self.slot_height - 50)
            self.slot_positions.append((slot_x, slot_y))

        # Create a copy of words for shuffling
        self.words_copy = self.words[:]  # Make a copy of the words
        random.shuffle(self.words_copy)  # Shuffle the copy

        # Calculate initial word positions based on shuffled words
        self.word_positions = []
        for i in range(len(self.words_copy)):
            word_x = self.center_x - (len(self.words_copy) * (self.word_width + self.word_gap)) // 2 + i * (
                    self.word_width + self.word_gap)
            word_y = self.center_y - self.word_height // 2 + 200
            self.word_positions.append((word_x, word_y))

        # Set original positions to match shuffled positions
        self.original_word_positions = list(self.word_positions)
        self.display_words = self.words_copy
        print(self.words)
        print(self.words_copy)


        # Debugging output
        # print("Shuffled words or syllables:", self.words)
        # print("Shuffled word or syllable positions:", self.word_positions)

    def check_slots_correctness(self):
        # Check if the current slots match the correct order
        print(f"Checking slots: {self.word_slots} against {self.correct_slots}")  # Debugging line
        return self.word_slots == self.correct_slots

    def advance_round(self):
        """Advance to the next round or handle incorrect answers."""
        if self.check_slots_correctness():
            self.last_answer = self.word_slots[:]
            self.current_round += 1
            if not self.is_syllable_round and self.current_round < len(self.rounds):
                self.load_round()
                print(f"Successfully completed round {self.current_round}. Proceeding to the next round.")
                self.is_playing_cutscene = True
            elif not self.is_syllable_round and self.current_round >= len(self.rounds):
                print("Sentence segmenting completed! Transitioning to syllable segmenting rounds.")
                self.is_playing_cutscene = True
                self.current_round = 0
                self.is_syllable_round = True
                self.load_round()
            elif self.is_syllable_round and self.current_round < len(self.syllable_rounds):
                self.load_round()
                print(f"Successfully completed syllable round {self.current_round}. Proceeding to the next round.")
                self.is_playing_cutscene = True
            else:
                print("All rounds completed! Proceed to the next stage.")
                self.win = True

    def reset_slots(self):
        # Check if the game is over after losing a life
        if self.lives > 0:
            # Reset the slots to None and return words to original positions
            self.word_slots = [None] * len(self.display_words)
            for i in range(len(self.display_words)):
                self.word_positions[i] = self.original_word_positions[i]
            print(self.rounds)
        else:
            self.last_answer = self.word_slots[:]
            self.check_game_over()  # Trigger game over if lives are zero

    def check_game_over(self):
        """Check if the player has lost all lives and end the game."""
        if self.lives <= 0:
            print("Game Over! The player has lost all lives.")
            self.game_over = True
            self.set_correct_order()

            # You can use self.last_answer for feedback or display purposes
            print(f"Last answer provided by the player: {self.last_answer}")

    def set_correct_order(self):
        """Set the word slots and positions to the correct order based on the current round."""
        if self.current_round < len(self.rounds):
            correct_words = self.rounds[self.current_round]["words"]
            self.word_slots = correct_words[:]  # Set word slots to the correct words
            self.word_positions = [(-100, -100)] * len(correct_words)  # Hide the words by moving them off-screen
            print(f"Correct order set: {self.rounds}")

    def show_end_screen(self):
        self.display.blit(self.background_image, (0, 0))
        overlay = pygame.Surface(self.display.get_size())
        overlay.set_alpha(150)  # Set transparency level
        overlay.fill((0, 0, 0))  # Black background
        self.display.blit(overlay, (0, 0))  # Fill the screen with black
        font_path = os.path.join('fonts', 'ARIAL.TTF')
        self.font = pygame.font.Font(font_path, 20)

        # Display the appropriate message based on win or loss
        message = "You Win!" if self.win else "Game Over!"
        text_surface = self.font.render(message, True, (255, 255, 255))
        self.display.blit(text_surface, (
            self.display.get_width() // 2 - text_surface.get_width() // 2, self.display.get_height() // 3))

        # Define button positions
        self.restart_button = pygame.Rect(self.display.get_width() // 2 - (250 // 2), self.display.get_height() // 2,
                                          250,
                                          50)
        self.exit_button = pygame.Rect(self.display.get_width() // 2 - (250 // 2), self.display.get_height() // 2 + 70,
                                       250, 50)

        if self.win:
            # If player wins, add a Next Level button
            self.next_level_button = pygame.Rect(self.display.get_width() // 2 - (250 // 2),
                                                 self.display.get_height() // 2 - 70, 250, 50)

            # Draw the Next Level button (Blue)
            pygame.draw.rect(self.display, (0, 0, 255), self.next_level_button)
            next_level_text = self.font.render("Next Level", True, (255, 255, 255))
            self.display.blit(next_level_text, (self.next_level_button.x + 80, self.next_level_button.y + 10))

        # Draw the Restart button (Green)
        pygame.draw.rect(self.display, (0, 128, 0), self.restart_button)
        restart_text = self.font.render("Restart Level", True, (255, 255, 255))
        self.display.blit(restart_text, (self.restart_button.x + 65, self.restart_button.y + 10))

        # Draw the Exit button (Red)
        pygame.draw.rect(self.display, (128, 0, 0), self.exit_button)
        exit_text = self.font.render("Return to Main Menu", True, (255, 255, 255))
        self.display.blit(exit_text, (self.exit_button.x + 30, self.exit_button.y + 10))

    def play_cutscene(self):
        current_time = pygame.time.get_ticks()  # Get the current time
        if current_time - self.last_frame_time >= self.cutscene_frame_delay:
            # Update the frame only if the delay has passed
            if self.cutscene_index < len(self.cutscene_frames):
                self.display.blit(self.cutscene_frames[self.cutscene_index], (0, 0))
                self.cutscene_index += 1
            else:
                # Cutscene done, move to the next round
                self.is_playing_cutscene = False
                self.cutscene_index = 0
                self.advance_round()

            self.last_frame_time = current_time

    def speak_current_text(self):
        def speak():
            if not self.is_syllable_round:
                text_to_speak = self.correct_sentence  # Use the correct sentence for TTS
            else:
                text_to_speak = self.sentence  # Word for self.syllable_rounds

            # Speak the text using pyttsx3
            self.tts_engine.say(text_to_speak)
            self.tts_engine.runAndWait()

            # Create and start a new thread for TTS

        tts_thread = threading.Thread(target=speak)
        tts_thread.start()

    def handle_events(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if not self.is_playing_cutscene:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if self.audio_logo_rect.collidepoint(mouse_x, mouse_y):
                    self.speak_current_text()
                # Check if clicking on a placed word to remove it from the slot
                for i, (slot_word, slot_pos) in enumerate(zip(self.word_slots, self.slot_positions)):
                    if slot_word is not None:
                        slot_x, slot_y = slot_pos
                        if slot_x <= mouse_x <= slot_x + 60 and slot_y <= mouse_y <= slot_y + 40:
                            self.word_slots[i] = None
                            original_pos = self.original_word_positions[self.display_words.index(slot_word)]
                            self.word_positions[self.display_words.index(slot_word)] = original_pos
                            return
                # Start dragging if clicking on a word in the draggable area
                for i, word in enumerate(self.display_words):
                    word_x, word_y = self.word_positions[i]
                    if word_x <= mouse_x <= word_x + 60 and word_y <= mouse_y <= word_y + 40:
                        self.dragging_word = i
                        self.drag_offset_x = mouse_x - word_x
                        self.drag_offset_y = mouse_y - word_y
                        break

            elif event.type == pygame.MOUSEBUTTONUP:
                if self.dragging_word is not None:
                    mouse_x, mouse_y = event.pos
                    # Snap to nearest slot if within range
                    for i, (slot_x, slot_y) in enumerate(self.slot_positions):
                        if slot_x <= mouse_x <= slot_x + 60 and slot_y <= mouse_y <= slot_y + 40:
                            if self.word_slots[i] is None:
                                self.word_slots[i] = self.display_words[self.dragging_word]
                                self.word_positions[self.dragging_word] = (-100, -100)
                                break
                    self.dragging_word = None
                    # Check if the round is complete
                    if None not in self.word_slots:
                        if self.check_slots_correctness():
                            self.advance_round()  # Call this only if the answer is correct
                        else:
                            self.lives -= 1
                            print("Incorrect order. Lives remaining: ", self.lives)
                            self.reset_slots()  # Reset slots and check for game over after incorrect answer

            elif event.type == pygame.MOUSEMOTION and self.dragging_word is not None:
                mouse_x, mouse_y = event.pos
                self.word_positions[self.dragging_word] = (mouse_x - self.drag_offset_x, mouse_y - self.drag_offset_y)


    def draw(self):
        # Draw background and elements
        if not self.is_playing_cutscene:
            self.display.blit(self.background_image, (0, 0))

            # Draw the audio logo image
            self.display.blit(self.audio_logo_image, self.audio_logo_rect)

            # Animate the lamps by adjusting the opacity
            for pos in self.lamp_positions:
                lamp_surface = pygame.Surface((100, 100), pygame.SRCALPHA)
                pygame.draw.circle(lamp_surface, (255, 255, 100, self.lamp_opacity), (50, 50), 50)
                self.display.blit(lamp_surface, (pos[0] - 50, pos[1] - 50))

            if self.opacity_increasing:
                self.lamp_opacity += 1
                if self.lamp_opacity >= 255:
                    self.opacity_increasing = False
            else:
                self.lamp_opacity -= 1
                if self.lamp_opacity <= 120:
                    self.opacity_increasing = True

            # Display the sentence or word/illustration above the slots
            font = pygame.font.Font(None, 36)
            if not self.is_syllable_round:
                # Display the sentence in non-syllable rounds
                sentence_text = self.sentence
                sentence_surface = font.render(sentence_text, True, (255, 255, 255))
                sentence_rect = sentence_surface.get_rect(center=(self.center_x, self.center_y - 100))
                self.display.blit(sentence_surface, sentence_rect)
            else:
                # Display the illustration in syllable rounds
                word_image = self.word_images.get(self.sentence, None)
                if word_image:
                    # Adjust image size and position if necessary
                    scaled_image = pygame.transform.scale(word_image, (75, 75))
                    image_rect = word_image.get_rect(center=(self.center_x + 75, self.center_y - 50))
                    self.display.blit(scaled_image, image_rect)

            # Draw slots
            for (slot_x, slot_y) in self.slot_positions:
                pygame.draw .rect(self.display, (255, 255, 255), (slot_x, slot_y, 60, 40), 2)

            # Draw words and placed words
            for i, word in enumerate(self.display_words):
                word_x, word_y = self.word_positions[i]
                pygame.draw.rect(self.display, (36, 34, 33), (word_x, word_y, 60, 40))
                word_surface = font.render(word, True, (255, 255, 255))
                word_rect = word_surface.get_rect(center=(word_x + 30, word_y + 20))
                self.display.blit(word_surface, word_rect)

            for i, word in enumerate(self.word_slots):
                if word is not None:
                    slot_x, slot_y = self.slot_positions[i]
                    pygame.draw.rect(self.display, (36, 34, 33), (slot_x, slot_y, 60, 40))
                    word_surface = font.render(word, True, (255, 255, 255))
                    word_rect = word_surface.get_rect(center=(slot_x + 30, slot_y + 20))
                    self.display.blit(word_surface, word_rect)

            # Draw player lives on the screen
            for i in range(self.lives):
                self.display.blit(self.heart_image, (10 + i * 60, 10))

        else:
            self.play_cutscene()


    def reset_game(self):
        """Reset the game state to the initial conditions."""
        print("Resetting game...")
        self.lives = 3
        self.current_round = 0
        self.correct_slots = self.initialize_correct_slots()  # Call to set correct slots
        self.word_slots = [None] * len(self.words)  # Reset word slots
        round_data = self.rounds[self.current_round]
        self.sentence = round_data["sentence"]
        self.words = round_data["words"]
        self.correct_sentence = round_data["correct-sentence"]
        self.correct_slots = self.words[:]  # Store the correct order for this round
        print(self.correct_slots)
        self.load_round()  # Load the first round
        self.game_over = False  # Reset game over state
        self.win = False  # Reset win state
        self.end_screen_displayed = False  # Reset end screen display flag
        print("Game has been reset.")
        self.is_restart = True

    def initialize_correct_slots(self):
        """Return the correct slots for the current level based on the current round."""
        if self.current_round < len(self.rounds):
            return self.rounds[self.current_round]["words"]  # Ensure this retrieves the correct order
        return []

    def load_next_level(self):
        self.gameStateManager.set_state('ninth-level')

    def run(self):
        pygame.mixer.init()
        if not self.is_restart:
            pygame.mixer.music.unload()
            pygame.mixer.music.load(os.path.join('audio', '02 Wonderin.mp3'))
            pygame.mixer.music.set_volume(0.05)
            pygame.mixer.music.play(-1)
            self.run_dialogue_strip()
            self.run_dialogue_strip_1()
            pygame.mixer.music.stop()
        else:
            self.is_restart = False
        pygame.mixer.music.unload()
        pygame.mixer.music.load(os.path.join('audio', '02 Wonderin.mp3'))
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(-1)
        running = True
        while running:
            for event in pygame.event.get():
                self.handle_events(event)

                # Check for mouse button clicks
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
                    mouse_pos = event.pos  # Get the mouse position
                    if self.game_over or self.win:  # Only check button clicks when game is over or won
                        # Check if the Next Level button is clicked
                        if self.win and self.next_level_button.collidepoint(mouse_pos):
                            pygame.mixer.music.stop()
                            self.load_next_level()  # Replace with your method to load the next level
                            running = False
                        # Check if the Restart button is clicked
                        elif self.restart_button.collidepoint(mouse_pos):
                            pygame.mixer.music.play(-1)
                            self.reset_game()
                            print("Reset button clicked!")
                        # Check if the Exit button is clicked
                        elif self.exit_button.collidepoint(mouse_pos):
                            pygame.mixer.music.stop()
                            self.gameStateManager.set_state('main-menu')
                            running = False  # Exit the game loop (or you could go to the main menu)

            if self.game_over or self.win:
                if not self.end_screen_displayed:  # Check if end screen is not yet displayed
                    pygame.mixer.music.stop()
                    self.show_end_screen()  # Display the end screen
                    pygame.display.update()  # Update the display
                    self.end_screen_displayed = True  # Set flag to indicate end screen has been displayed
            else:
                self.draw()  # Only draw if the game is not over or won
                pygame.display.update()  # Update the display
        pygame.mixer.music.stop()

class NinthLevel:
    class Syllable:
        def __init__(self, text, x, y, font_size, boulder_image):
            self.text = text
            self.rect = pygame.Rect(x, y, font_size * len(text), font_size)
            self.boulder_image = boulder_image  # Assign the boulder image
            self.boulder_rect = self.boulder_image.get_rect(
                topleft=(x, y))  # Position the boulder image at the same position

        def fall(self, speed):
            self.rect.y += speed
            self.boulder_rect.y += speed  # Move the boulder along with the syllable

        def draw(self, surface, font):
            # Draw the boulder image
            surface.blit(self.boulder_image, (self.boulder_rect.x, self.boulder_rect.y))

            # Draw the syllable text on top of the boulder
            text_surface = font.render(self.text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=self.boulder_rect.center)  # Center the text on the boulder
            surface.blit(text_surface, text_rect)

    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager

        # Initialize Pygame
        pygame.init()

        # Game constants
        self.WIDTH, self.HEIGHT = 1200, 550
        self.SYLLABLES = [
            {"word": "hospital", "syllables": ["hos", "pi", "tal"]},
            {"word": "banana", "syllables": ["ba", "na", "na"]},
            {"word": "computer", "syllables": ["com", "pu", "ter"]},
            {"word": "watermelon", "syllables": ["wa", "ter", "me", "lon"]},
            {"word": "chocolate", "syllables": ["cho", "co", "late"]},
            {"word": "potato", "syllables": ["po", "ta", "to"]},
            {"word": "hamburger", "syllables": ["ham", "bur", "ger"]},
            {"word": "dinosaur", "syllables": ["di", "no", "saur"]},
            {"word": "crocodile", "syllables": ["cro", "co", "dile"]},
            # Add more words and syllables as needed
        ]
        self.FONT_SIZE = 36
        self.LIVES = 100
        self.current_word = ""  # Track the current word
        self.energy_level = 100  # Initialize energy level
        self.backspace_pressed = False
        self.win = False
        self.is_restart = False

        # Set up font
        self.font = pygame.font.Font(None, self.FONT_SIZE)

        # Load boulder image
        self.boulder_image_path = os.path.join('graphics', 'Boulder.png')
        self.boulder_image = pygame.image.load(self.boulder_image_path).convert_alpha()
        self.boulder_image = pygame.transform.scale(self.boulder_image, (75, 75))

        # Enemy Logo image
        self.enemylogo_image_path = os.path.join('graphics', 'Confusion-Logo.png')
        self.enemylogo_image = pygame.image.load(self.enemylogo_image_path).convert_alpha()
        self.enemylogo_image = pygame.transform.scale(self.enemylogo_image, (60, 60))

        # Shield Logo image
        self.shieldlogo_image_path = os.path.join('graphics', 'shield-Logo.png')
        self.shieldlogo_image = pygame.image.load(self.shieldlogo_image_path).convert_alpha()
        self.shieldlogo_image = pygame.transform.scale(self.shieldlogo_image, (60, 60))

        # Load background image
        background_image_path = os.path.join('graphics', 'tower-final-bg.png')
        self.background_image = pygame.image.load(background_image_path).convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image,
                                                       (self.display.get_width(), self.display.get_height()))

        # black image
        black_image_path = os.path.join('graphics', 'black-screen.png')
        self.black_image = pygame.image.load(black_image_path).convert_alpha()
        self.black_image = pygame.transform.scale(self.black_image,
                                                       (self.display.get_width(), self.display.get_height()))

        # Load background image
        shield_image_path = os.path.join('graphics', 'shield.png')
        self.shield_image = pygame.image.load(shield_image_path).convert_alpha()
        self.shield_image = pygame.transform.scale(self.shield_image,
                                                       (self.display.get_width(), self.display.get_height()))

        # Load shield broke image
        shield_broke_image_path = os.path.join('graphics', 'shield-broke.png')
        self.shield_broke_image = pygame.image.load(shield_broke_image_path).convert_alpha()
        self.shield_broke_image = pygame.transform.scale(self.shield_broke_image,
                                                         (self.display.get_width(), self.display.get_height()))
        self.show_shield_broke = False  # Flag to control the display of the shield-broke image
        self.shield_broke_timer = 0  # Timer to keep track of how long to display the image

        # Game constants
        self.WIDTH, self.HEIGHT = 1000, 525

        # Load the Confusion Final Form sprite sheet
        self.confusion_sprite_sheet_path = os.path.join('graphics', 'Confusion-Final-Form-Sheet.png')
        self.confusion_sprite_sheet = pygame.image.load(self.confusion_sprite_sheet_path).convert_alpha()

        self.confusion_frames = []
        self.load_confusion_frames()

        # Variables for animation
        self.current_frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 100  # milliseconds between frames

        # Input box properties
        self.input_box_width = 300
        self.input_box_height = 40
        self.input_box_x = 110 # Center horizontally
        self.input_box_y = 660
        self.input_box = pygame.Rect(self.input_box_x, self.input_box_y, self.input_box_width, self.input_box_height)
        self.input_color = (255, 255, 255)  # White
        self.text_color = (0, 0, 0)  # Black
        self.current_text = ""

        # Game properties
        self.syllables = []
        self.spawn_timer = 0
        self.spawn_interval = 1000  # milliseconds

    def load_spritesheet(self, filename, frame_width, frame_height, scale_factor):
        # Load the sprite sheet image
        spritesheet = pygame.image.load(os.path.join('graphics', filename)).convert_alpha()
        # Get the width and height of the entire sprite sheet
        sheet_width, sheet_height = spritesheet.get_size()

        # Create a list to hold individual frames
        frames = []
        for y in range(0, sheet_height, frame_height):
            for x in range(0, sheet_width, frame_width):
                # Extract each frame by using a sub-surface
                frame = spritesheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
                # Scale the frame to make it larger
                scaled_frame = pygame.transform.scale(frame, (
                    int(frame_width * scale_factor), int(frame_height * scale_factor)))
                frames.append(scaled_frame)

        return frames

    def run_dialogue_strip(self):
        self.dialogue_font = pygame.font.Font(None, 36)

        # Dialogue list (narrating the FourthLevel)
        self.dialogue_lines = [
            "After entering the gate, Lexi and the adventurer rush their way onto the spiral stairs.",
            "...",
            "Upon reaching the top of the tower, they saw the king lying on the floor",
            "They approached the king who cant move due to the curse of Confusion.",
            '"Confusion is on the opposite side of the tower. Go there and end all of this.", the king said.',
            "The two rushed on the other room opposite of the tower and that is where they found confusion.",
        ]

        # Corresponding images for each dialogue line
        self.dialogue_images = [
            pygame.image.load(os.path.join('graphics', 'To-Confusion-1.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'To-Confusion-2.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'To-Confusion-3.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'To-Confusion-4.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'To-Confusion-5.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'To-Confusion-6.png')).convert_alpha(),
        ]

        # Corresponding narration files for each dialogue line
        self.dialogue_sounds = [
            pygame.mixer.Sound(os.path.join('audio', 'ninth-narrator-1.mp3')),
            pygame.mixer.Sound(os.path.join('audio', '500-milliseconds-of-silence.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'ninth-narrator-2.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'ninth-narrator-3.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'ninth-narrator-4.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'ninth-narrator-5.mp3')),
        ]

        # Scale the images to fit the screen
        self.dialogue_images = [
            pygame.transform.scale(img, (self.display.get_width(), self.display.get_height() - 150)) for img in
            self.dialogue_images
        ]

        self.dialogue_index = 0
        running = True

        # Initialize the mixer for playing audio
        pygame.mixer.init()

        # Flag to check if narration is playing
        self.narration_playing = False

        def play_narration():
            """Play the narration for the current dialogue line."""
            self.narration_playing = True
            self.dialogue_sounds[self.dialogue_index].play()
            pygame.time.set_timer(pygame.USEREVENT, int(self.dialogue_sounds[self.dialogue_index].get_length() * 1000))

        # Stop any currently playing narration before starting the new one
        for sound in self.dialogue_sounds:
            sound.stop()

        # Play the first narration automatically
        play_narration()

        while running:
            self.display.fill((0, 0, 0))  # Black background for the dialogue screen

            # Display the corresponding image
            self.display.blit(self.dialogue_images[self.dialogue_index], (0, 0))

            # Create and display the dialogue box
            dialogue_box_rect = pygame.Rect(0, self.display.get_height() - 150, self.display.get_width(), 150)
            pygame.draw.rect(self.display, (0, 0, 0), dialogue_box_rect)

            # Render the current dialogue line
            dialogue_text = self.dialogue_font.render(self.dialogue_lines[self.dialogue_index], True,
                                                      (255, 255, 255))  # White font
            dialogue_rect = dialogue_text.get_rect(
                center=(self.display.get_width() // 2, self.display.get_height() - 75))
            self.display.blit(dialogue_text, dialogue_rect)

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    sys.exit()

                # Allow the player to skip the narration and move to the next slide with the spacebar
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.dialogue_sounds[self.dialogue_index].stop()  # Stop the current narration
                        self.narration_playing = False
                        self.dialogue_index += 1
                        if self.dialogue_index >= len(self.dialogue_lines):
                            running = False  # End the dialogue and start the game
                        else:
                            play_narration()  # Play the next narration

                # Check if narration finished
                if event.type == pygame.USEREVENT and self.narration_playing:
                    self.narration_playing = False
                    self.dialogue_index += 1
                    if self.dialogue_index >= len(self.dialogue_lines):
                        running = False  # End the dialogue and start the game
                    else:
                        play_narration()  # Play the next narration

            pygame.display.update()

    def run_dialogue_strip_1(self):
        # Initialize pygame's mixer for audio (if needed)
        pygame.mixer.init()

        # Load character images (only one image for the player)
        char1_image = pygame.image.load(os.path.join('graphics', 'character-avatar.png'))
        char1_image = pygame.transform.scale(char1_image, (200, 200))

        # Load character images (only one image for the player)
        char2_image = pygame.image.load(os.path.join('graphics', 'confusion-avatar.png'))
        char2_image = pygame.transform.scale(char2_image, (200, 200))

        dialogue_data = [
            {"name": "You", "text": "STOP ALL OF THIS CONFUSION!", "image": char1_image},
            {"name": "You", "text": "Dyscape will be fully destroyed if you still continue this.", "image": char1_image},
            {"name": "Confusion", "text": "Stop me if you can. This world's destruction is inevitable.", "image": char2_image},
            {"name": "Confusion", "text": "All of the people here are like pawns to me. Their weakness disgusts me.", "image": char2_image},
            {"name": "Confusion", "text": "Even the king of this world thinks he is that mighty. What a joke.", "image": char2_image},
            {"name": "You", "text": "What is your intention, Confusion? Did you understand every single word you said?", "image": char1_image},
            {"name": "Confusion", "text": "I don't know, really. Maybe I just love the thought of destroying things\n that are not my liking.", "image": char2_image},
            {"name": "You", "text": "YOU ARE A MONSTER!", "image": char1_image},
            {"name": "Confusion","text": "Haha! Maybe I am! And your mere sword cant defeat a monster.", "image": char2_image},
            {"name": "You", "text": "I will take you on! Right here and right now!", "image": char1_image},
            {"name": "Confusion", "text": "That's the spirit! Haha! I'd like to see you try, weakling.", "image": char2_image},
        ]

        # Preload audio files
        audio_files = {}
        for dialogue in dialogue_data:
            if "audio" in dialogue:
                audio_file = dialogue["audio"]
                audio_files[audio_file] = pygame.mixer.Sound(os.path.join("audio", audio_file))

        dialogue_box_height = 150  # Height of the dialogue box surface
        dialogue_font = pygame.font.Font(None, 32)  # Font for dialogue text
        name_font = pygame.font.Font(None, 36)  # Font for character names
        space_prompt_font = pygame.font.Font(None, 28)  # Font for "Press SPACE to continue"

        current_line = 0
        text_displayed = ""
        text_index = 0
        text_speed = 2  # Speed of text animation
        audio_played = False  # Flag to track if audio has been played for the current line
        current_sound = None  # Track the currently playing sound

        running = True
        clock = pygame.time.Clock()

        while running:
            self.display.blit(self.background_image, (0, 0))

            # Create the dialogue box at the bottom
            dialogue_box = pygame.Surface((self.display.get_width(), dialogue_box_height))
            dialogue_box.fill((255, 219, 172))  # Light background for the dialogue box
            dialogue_box_rect = dialogue_box.get_rect(topleft=(0, self.display.get_height() - dialogue_box_height))

            # Draw the brown border around the dialogue box
            border_color = (139, 69, 19)  # Brown color (RGB)
            border_thickness = 20  # Thickness of the border
            pygame.draw.rect(self.display, border_color, dialogue_box_rect.inflate(border_thickness, border_thickness),
                             border_thickness)

            # Get the current dialogue data
            current_dialogue = dialogue_data[current_line]
            character_name = current_dialogue["name"]
            character_text = current_dialogue["text"]
            antagonist = "Confusion"

            # Play the audio file if it exists and hasn't been played yet
            if "audio" in current_dialogue and not audio_played:
                audio_file = current_dialogue["audio"]
                if current_sound is not None:
                    current_sound.stop()  # Stop the currently playing sound if it exists
                current_sound = audio_files[audio_file]  # Get the new sound
                current_sound.play()  # Play the new audio
                audio_played = True  # Set the flag to True to prevent replaying the audio

            # Update owl animation (cycle through the frames)
            if character_name == antagonist or character_name == "Confusion":
                self.display.blit(char2_image, (950, self.display.get_height() - dialogue_box_height - 200))

            # Render the character image (player) if it's the player's turn
            else:
                self.display.blit(char1_image, (50, self.display.get_height() - dialogue_box_height - 200))

            # Render the character name inside the dialogue box (above the text)
            name_surface = name_font.render(character_name, True, (0,0,0))
            dialogue_box.blit(name_surface, (20, 10))  # Draw name near the top inside the dialogue box

            # Text animation (add one letter at a time)
            if text_index < len(character_text):
                text_index += text_speed  # Control how fast letters are added
                text_displayed = character_text[:text_index]
            else:
                text_displayed = character_text

            # Render the dialogue text below the name
            text_surface = dialogue_font.render(text_displayed, True, (0,0,0))
            dialogue_box.blit(text_surface, (20, 60))  # Draw the text inside the dialogue box below the name

            # Add "Press SPACE to continue." prompt at the bottom right
            if text_index >= len(character_text):  # Show prompt only if the text is fully displayed
                space_prompt_surface = space_prompt_font.render("Press SPACE to continue.", True, (100, 100, 100))
                dialogue_box.blit(space_prompt_surface,
                                  (dialogue_box.get_width() - space_prompt_surface.get_width() - 20,
                                   dialogue_box.get_height() - space_prompt_surface.get_height() - 10))

            # Draw the dialogue box on the screen with the brown border
            self.display.blit(dialogue_box, dialogue_box_rect.topleft)

            # Event handling for advancing the dialogue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:  # Only proceed on SPACE key
                        if text_index >= len(character_text):
                            # Move to the next line of dialogue if the text is fully displayed
                            current_line += 1
                            text_index = 0
                            text_displayed = ""
                            audio_played = False  # Reset the audio flag for the next line
                            if current_line >= len(dialogue_data):
                                running = False  # Exit dialogue when all lines are done

            pygame.display.flip()
            clock.tick(60)  # Control the frame rate

    def run_dialogue_strip_2(self):
        # Initialize pygame's mixer for audio (if needed)
        pygame.mixer.init()

        # Load the owl sprite sheet and extract frames for animation
        owl_frames = self.load_spritesheet('owl-flying.png', 48, 48, scale_factor=6)
        owl_frame_index = 0  # Start with the first frame of the animation
        owl_animation_speed = 5  # Change the frame every 5 frames of the game loop

        # Load character images (only one image for the player)
        char1_image = pygame.image.load(os.path.join('graphics', 'character-avatar.png'))
        char1_image = pygame.transform.scale(char1_image, (200, 200))

        dialogue_data = [
            {"name": "Magical Owl", "text": "Psst! Adventurer! I have a plan"},
            {"name": "You", "text": "What is it, Lexi?", "image": char1_image},
            {"name": "Magical Owl", "text": "We cannot defeat Confusion if we trade blows with him. But we can TIRE HIM out."},
            {"name": "You", "text": "That's a great idea! Tell me more.", "image": char1_image},
            {"name": "Magical Owl", "text": "I ll put up a MAGIC SHIELD and block Confusion's Attacks."},
            {"name": "Magical Owl", "text": "He will probably use his power to throw chunks and boulders."},
            {"name": "Magical Owl", "text": "This shield will deal a great amount of my magic, but so does his power."},
            {"name": "Magical Owl", "text": "This shield has its limit, so try to DESTROY as many boulders as you can."},
            {"name": "Magical Owl","text": "Let's do this, adventurer! This is a battle of endurance."},
            {"name": "You", "text": "I got you, Lexi! I'm on it.", "image": char1_image},
        ]

        # Preload audio files
        audio_files = {}
        for dialogue in dialogue_data:
            if "audio" in dialogue:
                audio_file = dialogue["audio"]
                audio_files[audio_file] = pygame.mixer.Sound(os.path.join("audio", audio_file))

        dialogue_box_height = 150  # Height of the dialogue box surface
        dialogue_font = pygame.font.Font(None, 32)  # Font for dialogue text
        name_font = pygame.font.Font(None, 36)  # Font for character names
        space_prompt_font = pygame.font.Font(None, 28)  # Font for "Press SPACE to continue"

        current_line = 0
        text_displayed = ""
        text_index = 0
        text_speed = 2  # Speed of text animation
        audio_played = False  # Flag to track if audio has been played for the current line
        current_sound = None  # Track the currently playing sound

        running = True
        clock = pygame.time.Clock()

        while running:
            self.display.blit(self.black_image, (0, 0))

            # Create the dialogue box at the bottom
            dialogue_box = pygame.Surface((self.display.get_width(), dialogue_box_height))
            dialogue_box.fill((255, 219, 172))  # Light background for the dialogue box
            dialogue_box_rect = dialogue_box.get_rect(topleft=(0, self.display.get_height() - dialogue_box_height))

            # Draw the brown border around the dialogue box
            border_color = (139, 69, 19)  # Brown color (RGB)
            border_thickness = 20  # Thickness of the border
            pygame.draw.rect(self.display, border_color, dialogue_box_rect.inflate(border_thickness, border_thickness),
                             border_thickness)

            # Get the current dialogue data
            current_dialogue = dialogue_data[current_line]
            character_name = current_dialogue["name"]
            character_text = current_dialogue["text"]
            antagonist = "Magical Owl"

            # Play the audio file if it exists and hasn't been played yet
            if "audio" in current_dialogue and not audio_played:
                audio_file = current_dialogue["audio"]
                if current_sound is not None:
                    current_sound.stop()  # Stop the currently playing sound if it exists
                current_sound = audio_files[audio_file]  # Get the new sound
                current_sound.play()  # Play the new audio
                audio_played = True  # Set the flag to True to prevent replaying the audio

            # Update owl animation (cycle through the frames)
            if character_name == antagonist or character_name == "Lexi the Owl":
                owl_frame_index = (owl_frame_index + 1) % (len(owl_frames) * owl_animation_speed)
                current_owl_frame = owl_frames[owl_frame_index // owl_animation_speed]
                self.display.blit(current_owl_frame, (950, self.display.get_height() - dialogue_box_height - 300))

            # Render the character image (player) if it's the player's turn
            else:
                self.display.blit(char1_image, (50, self.display.get_height() - dialogue_box_height - 200))

            # Render the character name inside the dialogue box (above the text)
            name_surface = name_font.render(character_name, True, (0,0,0))
            dialogue_box.blit(name_surface, (20, 10))  # Draw name near the top inside the dialogue box

            # Text animation (add one letter at a time)
            if text_index < len(character_text):
                text_index += text_speed  # Control how fast letters are added
                text_displayed = character_text[:text_index]
            else:
                text_displayed = character_text

            # Render the dialogue text below the name
            text_surface = dialogue_font.render(text_displayed, True, (0,0,0))
            dialogue_box.blit(text_surface, (20, 60))  # Draw the text inside the dialogue box below the name

            # Add "Press SPACE to continue." prompt at the bottom right
            if text_index >= len(character_text):  # Show prompt only if the text is fully displayed
                space_prompt_surface = space_prompt_font.render("Press SPACE to continue.", True, (100, 100, 100))
                dialogue_box.blit(space_prompt_surface,
                                  (dialogue_box.get_width() - space_prompt_surface.get_width() - 20,
                                   dialogue_box.get_height() - space_prompt_surface.get_height() - 10))

            # Draw the dialogue box on the screen with the brown border
            self.display.blit(dialogue_box, dialogue_box_rect.topleft)

            # Event handling for advancing the dialogue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:  # Only proceed on SPACE key
                        if text_index >= len(character_text):
                            # Move to the next line of dialogue if the text is fully displayed
                            current_line += 1
                            text_index = 0
                            text_displayed = ""
                            audio_played = False  # Reset the audio flag for the next line
                            if current_line >= len(dialogue_data):
                                running = False  # Exit dialogue when all lines are done

            pygame.display.flip()
            clock.tick(60)  # Control the frame rate

    def load_confusion_frames(self):
        """Extracts 9 frames from the sprite sheet, each of size 500x500."""
        frame_width = 500
        frame_height = 500
        num_frames = 9

        for i in range(num_frames):
            # Cut out each frame from the sprite sheet
            frame = self.confusion_sprite_sheet.subsurface((i * frame_width, 0, frame_width, frame_height))
            self.confusion_frames.append(frame)

    def update_animation(self):
        """Updates the current frame index based on time for the animation."""
        current_time = pygame.time.get_ticks()  # Get the time in milliseconds
        if current_time - self.animation_timer > self.animation_speed:
            self.animation_timer = current_time
            # Update to the next frame, looping back to the first frame when reaching the end
            self.current_frame_index = (self.current_frame_index + 1) % len(self.confusion_frames)

    def draw_confusion(self):
        """Draws the current frame of the Confusion animation with scaling and adjustable placement."""
        current_frame = self.confusion_frames[self.current_frame_index]

        # Define new width and height for scaling (you can adjust the scaling factors as needed)
        scale_width, scale_height = 300, 300  # Example scaling to 300x300

        # Scale the current frame to the desired size
        scaled_frame = pygame.transform.scale(current_frame, (scale_width, scale_height))

        # Define new x and y positions for placement
        new_x = WIDTH // 2 - scale_width // 2  # Center horizontally
        new_y = -50  # Adjust vertical placement (50 pixels from the top)

        # Draw the scaled frame at the new position
        self.display.blit(scaled_frame, (new_x, new_y))

    def draw_text_box(self):
        # Draw the input box
        pygame.draw.rect(self.display, self.input_color, self.input_box, 0)
        text_surface = self.font.render(self.current_text, True, self.text_color)
        self.display.blit(text_surface, (self.input_box.x + 5, self.input_box.y + 5))
        label = f"Enter word here: "
        label_surface = self.font.render(label, True, (0, 0, 0))
        self.display.blit(label_surface, (115, 630))  # Adjust text position accordingly

    def draw_lifebar(self, current_value, max_value, x, y, width, height, fill_color, border_color=(255, 255, 255),
                     background_color=(50, 50, 50)):
        # Draw the background for the lifebar
        pygame.draw.rect(self.display, background_color, (x, y, width, height))  # Background rectangle
        # Draw the border
        pygame.draw.rect(self.display, border_color, (x -1, y -1, width +2, height +2), 2)  # Border with thickness of 2
        # Calculate the width of the lifebar based on the current value
        bar_width = (current_value / max_value) * width
        # Draw the filled lifebar
        pygame.draw.rect(self.display, fill_color, (x, y, bar_width, height))

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:  # Enter key
                self.check_input()
                self.current_text = ""
            elif event.key == pygame.K_BACKSPACE:
                if self.current_text:  # Check if there is text to remove
                    self.current_text = self.current_text[:-1] # Remove the last character
            else:
                self.current_text += event.unicode  # Add typed character to input

    def check_input(self):
        # Check if player typed the correct word
        if self.current_text.lower() == self.current_word.lower():
            print("Correct answer:", self.current_text)
            self.syllables = []  # Destroy current syllables
            self.spawn_next_word()  # Spawn the next word's syllables
        else:
            print("Wrong answer:", self.current_text)

    def update(self):
        # Spawn new syllables if none are on the screen
        if not self.syllables:
            self.spawn_next_word()

        # Create a list to hold syllables that need to be removed
        syllables_to_remove = []

        # Update syllable positions
        for syllable in self.syllables:
            syllable.fall(1)  # Move syllables down
            if syllable.rect.y > self.HEIGHT:  # If a syllable hits the bottom
                self.LIVES -= 4
                print(f"Lives left: {self.LIVES}")
                syllables_to_remove.append(syllable)  # Mark the syllable for removal

                # Show the shield broke image for 0.2 seconds
                self.show_shield_broke = True
                self.shield_broke_timer = pygame.time.get_ticks()  # Start the timer

                if self.LIVES <= 0:
                    self.game_over()

        # Remove the syllables that were marked for removal
        for syllable in syllables_to_remove:
            if syllable in self.syllables:  # Check if syllable still exists
                self.syllables.remove(syllable)

        # Check for win condition
        if self.energy_level <= 0:
            print("You win!")
            self.win = True
            self.gameStateManager.set_state('final-level')  # Transition to final level

        # Check if the shield-broke image should be hidden
        if self.show_shield_broke and (pygame.time.get_ticks() - self.shield_broke_timer > 200):  # 200 ms
            self.show_shield_broke = False

    def spawn_next_word(self):
        # Choose a random word and its syllables
        word_data = random.choice(self.SYLLABLES)
        self.current_word = word_data["word"]  # Set current word
        syllables = word_data["syllables"]

        # Define a minimum distance between syllables
        min_distance = 50  # Adjust this value as needed

        for syllable_text in syllables:
            # Generate a position for the new syllable
            while True:
                x = random.randint(0, self.WIDTH - self.FONT_SIZE * len(syllable_text))
                y = -self.FONT_SIZE

                # Check if the new syllable overlaps with existing syllables
                overlap = False
                for existing_syllable in self.syllables:
                    if abs(existing_syllable.rect.x - x) < min_distance and abs(existing_syllable.rect.y - y) < min_distance:
                        overlap = True
                        break

                # If no overlap, break the loop and add the syllable
                if not overlap:
                    break

            # Add the new syllable to the list, using the scaled boulder image
            self.syllables.append(self.Syllable(syllable_text, x, y, self.FONT_SIZE, self.boulder_image))
            self.energy_level -= 2  # Deduct energy level

    def draw_syllables(self):
        for syllable in self.syllables:
            syllable.draw(self.display, self.font)

    def draw_lives(self):
        self.draw_lifebar(self.LIVES, 100, 110, 40, 300, 15, (154, 213, 33),
                          (255, 255, 255))  # Green lifebar with white border
        lives_text = f"Shield Health:       {self.LIVES} %"
        lives_surface = self.font.render(lives_text, True, (0, 0, 0))
        self.display.blit(lives_surface, (110, 10))  # Adjust text position accordingly

    def draw_energy(self):
        self.draw_lifebar(self.energy_level, 100, 110, 110, 300, 15, (38, 46, 124),
                          (255, 255, 255))  # Blue energy bar with white border
        energy_text = f"Confusion's Energy: {self.energy_level} %"
        energy_surface = self.font.render(energy_text, True, (0, 0, 0))
        self.display.blit(energy_surface, (110, 80))  # Adjust text position accordingly

    def draw_end_screen(self):
        # Draw a semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))  # Use the specified screen size
        overlay.fill((0, 0, 0, 180))  # Semi-transparent black
        self.display.blit(overlay, (0, 0))

        # Draw the game over text
        game_over_text = self.font.render("Your Shield broke.", True, (255, 0, 0))
        text_rect = game_over_text.get_rect(center=(640, 300))  # Center horizontally at 640 (1280 / 2)
        self.display.blit(game_over_text, text_rect)

        # Draw the restart button
        restart_button_rect = pygame.Rect(640 - 75, 360, 150, 40)  # Center the button at 640
        pygame.draw.rect(self.display, (0, 255, 0), restart_button_rect)
        restart_text = self.font.render("Restart", True, (0, 0, 0))
        restart_text_rect = restart_text.get_rect(center=restart_button_rect.center)  # Center the text in the button
        self.display.blit(restart_text, restart_text_rect)

        pygame.display.flip()

        return restart_button_rect

    def game_over(self):
        running = True
        while running:
            restart_button_rect= self.draw_end_screen()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if restart_button_rect.collidepoint(mouse_pos):
                        self.reset_game()
                        running = False

            # Keep the screen updated
            pygame.display.flip()

    def reset_game(self):
        self.LIVES = 100
        self.energy_level = 100
        self.current_word = ""
        self.syllables = []
        self.current_text = ""
        self.win = False
        self.show_shield_broke = False
        self.shield_broke_timer = 0
        self.spawn_timer = 0
        self.spawn_next_word()  # Optionally start with a new word
        self.is_restart = True

    def run(self):
        pygame.mixer.init()
        clock = pygame.time.Clock()

        if not self.is_restart:
            self.run_dialogue_strip()
            pygame.mixer.music.unload()
            pygame.mixer.music.load(os.path.join('audio', '05 Reflect.mp3'))
            pygame.mixer.music.set_volume(0.1)
            pygame.mixer.music.play(-1)
            self.run_dialogue_strip_1()
            self.run_dialogue_strip_2()
            pygame.mixer.music.stop()
        else:
                self.is_restart = False
        pygame.mixer.music.unload()
        pygame.mixer.music.load(os.path.join('audio', '03 Invasion.mp3'))
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self.handle_input(event)  # Handle input events

            # Handle continuous backspace removal
            if self.backspace_pressed:
                if self.current_text:  # Only remove if there's text
                    self.current_text = self.current_text[:-1]

            # Update game state
            self.update()
            if self.win:
                self.gameStateManager.set_state('final-level')
                running = False
            self.update_animation()
            self.display.blit(self.background_image, (0, 0))  # Background color
            self.display.blit(self.shield_image, (0, 0))
            self.draw_confusion()
            self.draw_text_box()  # Draw the text box
            self.draw_syllables()  # Draw the syllables
            self.display.blit(self.shieldlogo_image, (30, 10))
            self.display.blit(self.enemylogo_image, (30, 75))
            self.draw_lives()  # Draw lives
            self.draw_energy()  # Draw energy level
            # Inside the run method, after drawing the background
            if self.show_shield_broke:
                self.display.blit(self.shield_broke_image, (0, 0))  # Draw shield broke image
            pygame.display.flip()  # Update the display
            clock.tick(FPS)  # Limit to 60 frames per second
        pygame.mixer.music.stop()

class FinalLevel:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager
        self.frames = []
        background_image_path_2 = os.path.join('graphics', 'confusion-stronger-bg.png')
        self.background_image_2 = pygame.image.load(background_image_path_2).convert_alpha()
        self.background_image_2 = pygame.transform.scale(self.background_image_2,
                                                         (self.display.get_width(), self.display.get_height()))

        self.load_spritesheets()

        self.questions = [
            {"question": "Which word begins with the same sound as dog?", "options": ["Door", "Cat", "Fish", "Top"], "correct": "Door", "background": "graphics/still_image-1.png"},
            {"question": "Which word rhymes with cap", "options": ["Cup", "Soup", "Map", "Kit"], "correct": "Map",
             "background": "graphics/still_image-2.png"},
            {"question": "Which word ends with the same sound as frog?", "options": ["Dog", "Cat", "Hat", "Fox"], "correct": "Dog",
             "background": "graphics/still_image-3.png"},
            {"question": "Which word has the same middle sound as sun?", "options": ["Sit", "Run", "Bag", "Net"], "correct": "Run",
             "background": "graphics/still_image-4.png"},
            {"question": "If you say the sounds /c/ - /a/ - /t/ together, what word do you get?", "options": ["Tap", "Cap", "Rat", "Cat"], "correct": "Cat",
             "background": "graphics/still_image-5.png"},
        ]

    def load_spritesheet(self, filename, frame_width, frame_height, scale_factor):
        # Load the sprite sheet image
        spritesheet = pygame.image.load(os.path.join('graphics', filename)).convert_alpha()
        # Get the width and height of the entire sprite sheet
        sheet_width, sheet_height = spritesheet.get_size()

        # Create a list to hold individual frames
        frames = []
        for y in range(0, sheet_height, frame_height):
            for x in range(0, sheet_width, frame_width):
                # Extract each frame by using a sub-surface
                frame = spritesheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
                # Scale the frame to make it larger
                scaled_frame = pygame.transform.scale(frame, (
                    int(frame_width * scale_factor), int(frame_height * scale_factor)))
                frames.append(scaled_frame)

        return frames

    def run_dialogue_strip(self):
        self.dialogue_font = pygame.font.Font(None, 36)

        # Dialogue list (narrating the FourthLevel)
        self.dialogue_lines = [
            "Their plan worked as Confusion was defeated and was fully tired.",
            "After a few seconds, Confusion stood up, all dizzy, with his face already exposed.",
            "Both Lexi and the adventurer noticed it as they were both shocked and feared to death.",
            "Confusion's face was revealed. He was a boy, sinister-looking, and with a black hair.",
            "Due to the fact that he was defeated, Confusion now powers up to his full extent and\n he will try to end this all.",

        ]

        # Corresponding images for each dialogue line
        self.dialogue_images = [
            pygame.image.load(os.path.join('graphics', 'Confusion-Reveal-1.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'Confusion-Reveal-2.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'Confusion-Reveal-3.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'Confusion-Reveal-4.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'Confusion-Reveal-5.png')).convert_alpha(),

        ]

        # Corresponding narration files for each dialogue line
        self.dialogue_sounds = [
            pygame.mixer.Sound(os.path.join('audio', 'confusion-reveal-1.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'confusion-reveal-2.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'confusion-reveal-3.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'confusion-reveal-4.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'confusion-reveal-5.mp3')),

        ]

        # Scale the images to fit the screen
        self.dialogue_images = [
            pygame.transform.scale(img, (self.display.get_width(), self.display.get_height() - 150)) for img in
            self.dialogue_images
        ]

        self.dialogue_index = 0
        running = True

        # Initialize the mixer for playing audio
        pygame.mixer.init()

        # Flag to check if narration is playing
        self.narration_playing = False

        def play_narration():
            """Play the narration for the current dialogue line."""
            self.narration_playing = True
            self.dialogue_sounds[self.dialogue_index].play()
            pygame.time.set_timer(pygame.USEREVENT, int(self.dialogue_sounds[self.dialogue_index].get_length() * 1000))

        # Play the first narration automatically
        play_narration()

        while running:
            self.display.fill((0, 0, 0))  # Black background for the dialogue screen

            # Display the corresponding image
            self.display.blit(self.dialogue_images[self.dialogue_index], (0, 0))

            # Create and display the dialogue box
            dialogue_box_rect = pygame.Rect(0, self.display.get_height() - 150, self.display.get_width(), 150)
            pygame.draw.rect(self.display, (0, 0, 0), dialogue_box_rect)

            # Render the current dialogue line
            dialogue_text = self.dialogue_font.render(self.dialogue_lines[self.dialogue_index], True,
                                                      (255, 255, 255))  # White font
            dialogue_rect = dialogue_text.get_rect(
                center=(self.display.get_width() // 2, self.display.get_height() - 75))
            self.display.blit(dialogue_text, dialogue_rect)

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    sys.exit()

                # Allow the player to skip the narration and move to the next slide with the spacebar
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.dialogue_sounds[self.dialogue_index].stop()  # Stop the current narration
                        self.narration_playing = False
                        self.dialogue_index += 1
                        if self.dialogue_index >= len(self.dialogue_lines):
                            running = False  # End the dialogue and start the game
                        else:
                            play_narration()  # Play the next narration

                # Check if narration finished
                if event.type == pygame.USEREVENT and self.narration_playing:
                    self.narration_playing = False
                    self.dialogue_index += 1
                    if self.dialogue_index >= len(self.dialogue_lines):
                        running = False  # End the dialogue and start the game
                    else:
                        play_narration()  # Play the next narration

            pygame.display.update()

    def run_dialogue_strip_1(self):
        # Initialize pygame's mixer for audio (if needed)
        pygame.mixer.init()

        # Load the owl sprite sheet and extract frames for animation
        owl_frames = self.load_spritesheet('owl-flying.png', 48, 48, scale_factor=6)
        owl_frame_index = 0  # Start with the first frame of the animation
        owl_animation_speed = 5  # Change the frame every 5 frames of the game loop

        # Load character images (only one image for the player)
        char1_image = pygame.image.load(os.path.join('graphics', 'character-avatar.png'))
        char1_image = pygame.transform.scale(char1_image, (200, 200))

        dialogue_data = [
            {"name": "You", "text": "Confusion is getting stronger and our shield is getting weaker!", "image": char1_image},
            {"name": "You", "text": "Is there anything we can do to end this fight?", "image": char1_image},
            {"name": "Magical Owl", "text": "Actually, there is one. But it may be our final chance."},
            {"name": "You", "text": "What is it? Tell me!", "image": char1_image},
            {"name": "Magical Owl", "text": "Your life will be at risk if we do this!. I can't let that happen."},
            {"name": "You", "text": "JUST TELL ME!", "image": char1_image},
            {"name": "Magical Owl", "text": "Okay. I will tell you this once so listen closely."},
            {"name": "Magical Owl", "text": "I will use my REMAINING magic power to help you deliver the FINAL\n BLOW to Confusion using your sword."},
            {"name": "Magical Owl", "text": "i will then use FORESIGHT and foresee the future to ELIMINATE ALL\n POSSIBLE OUTCOMES of you being defeated by him."},
            {"name": "Magical Owl", "text": "Using all of my magic will put me to sleep and if you fail, you may\n lose your life, in this world and yours."},
            {"name": "Magical Owl", "text": "I don't want you to die, adventurer."},
            {"name": "You", "text": "I dont care, Lexi. We’ve come this far to save your world.", "image": char1_image},
            {"name": "You", "text": "I trust you. I know you won't let me die.", "image": char1_image},
            {"name": "Magical Owl", "text": "Let's defeat this monster."},

        ]

        # Preload audio files
        audio_files = {}
        for dialogue in dialogue_data:
            if "audio" in dialogue:
                audio_file = dialogue["audio"]
                audio_files[audio_file] = pygame.mixer.Sound(os.path.join("audio", audio_file))

        dialogue_box_height = 150  # Height of the dialogue box surface
        dialogue_font = pygame.font.Font(None, 32)  # Font for dialogue text
        name_font = pygame.font.Font(None, 36)  # Font for character names
        space_prompt_font = pygame.font.Font(None, 28)  # Font for "Press SPACE to continue"

        current_line = 0
        text_displayed = ""
        text_index = 0
        text_speed = 2  # Speed of text animation
        audio_played = False  # Flag to track if audio has been played for the current line
        current_sound = None  # Track the currently playing sound

        running = True
        clock = pygame.time.Clock()

        while running:
            self.display.blit(self.background_image_2, (0, 0))

            # Create the dialogue box at the bottom
            dialogue_box = pygame.Surface((self.display.get_width(), dialogue_box_height))
            dialogue_box.fill((255, 219, 172))  # Light background for the dialogue box
            dialogue_box_rect = dialogue_box.get_rect(topleft=(0, self.display.get_height() - dialogue_box_height))

            # Draw the brown border around the dialogue box
            border_color = (139, 69, 19)  # Brown color (RGB)
            border_thickness = 20  # Thickness of the border
            pygame.draw.rect(self.display, border_color, dialogue_box_rect.inflate(border_thickness, border_thickness),
                             border_thickness)

            # Get the current dialogue data
            current_dialogue = dialogue_data[current_line]
            character_name = current_dialogue["name"]
            character_text = current_dialogue["text"]
            antagonist = "Magical Owl"

            # Play the audio file if it exists and hasn't been played yet
            if "audio" in current_dialogue and not audio_played:
                audio_file = current_dialogue["audio"]
                if current_sound is not None:
                    current_sound.stop()  # Stop the currently playing sound if it exists
                current_sound = audio_files[audio_file]  # Get the new sound
                current_sound.play()  # Play the new audio
                audio_played = True  # Set the flag to True to prevent replaying the audio

            # Update owl animation (cycle through the frames)
            if character_name == antagonist or character_name == "Lexi the Owl":
                owl_frame_index = (owl_frame_index + 1) % (len(owl_frames) * owl_animation_speed)
                current_owl_frame = owl_frames[owl_frame_index // owl_animation_speed]
                self.display.blit(current_owl_frame, (950, self.display.get_height() - dialogue_box_height - 300))

            # Render the character image (player) if it's the player's turn
            else:
                self.display.blit(char1_image, (50, self.display.get_height() - dialogue_box_height - 200))

            # Render the character name inside the dialogue box (above the text)
            name_surface = name_font.render(character_name, True, (0,0,0))
            dialogue_box.blit(name_surface, (20, 10))  # Draw name near the top inside the dialogue box

            # Text animation (add one letter at a time)
            if text_index < len(character_text):
                text_index += text_speed  # Control how fast letters are added
                text_displayed = character_text[:text_index]
            else:
                text_displayed = character_text

            # Render the dialogue text below the name
            text_surface = dialogue_font.render(text_displayed, True, (0,0,0))
            dialogue_box.blit(text_surface, (20, 60))  # Draw the text inside the dialogue box below the name

            # Add "Press SPACE to continue." prompt at the bottom right
            if text_index >= len(character_text):  # Show prompt only if the text is fully displayed
                space_prompt_surface = space_prompt_font.render("Press SPACE to continue.", True, (100, 100, 100))
                dialogue_box.blit(space_prompt_surface,
                                  (dialogue_box.get_width() - space_prompt_surface.get_width() - 20,
                                   dialogue_box.get_height() - space_prompt_surface.get_height() - 10))

            # Draw the dialogue box on the screen with the brown border
            self.display.blit(dialogue_box, dialogue_box_rect.topleft)

            # Event handling for advancing the dialogue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:  # Only proceed on SPACE key
                        if text_index >= len(character_text):
                            # Move to the next line of dialogue if the text is fully displayed
                            current_line += 1
                            text_index = 0
                            text_displayed = ""
                            audio_played = False  # Reset the audio flag for the next line
                            if current_line >= len(dialogue_data):
                                running = False  # Exit dialogue when all lines are done

            pygame.display.flip()
            clock.tick(60)  # Control the frame rate

    def run_dialogue_strip_2(self):
        self.dialogue_font = pygame.font.Font(None, 36)

        # Dialogue list (narrating the FourthLevel)
        self.dialogue_lines = [
            "Lexi starts pouring every power he has left onto the traveler's weapon.",
            "Then he uses FORESIGHT to foresee the future and ELIMINATE unneccesary \n outcomes for the final attack to be successful.",
            "Full of uncertainty, Lexi still pushes through as he remembers how the adventurer trusts him.",
        ]

        # Corresponding images for each dialogue line
        self.dialogue_images = [
            pygame.image.load(os.path.join('graphics', 'power-transfer-to-sword.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'foresight.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'foresight.png')).convert_alpha(),
        ]

        # Corresponding narration files for each dialogue line
        self.dialogue_sounds = [
            pygame.mixer.Sound(os.path.join('audio', 'final-narrator-1.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'final-narrator-2.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'final-narrator-3.mp3')),
        ]

        # Scale the images to fit the screen
        self.dialogue_images = [
            pygame.transform.scale(img, (self.display.get_width(), self.display.get_height() - 150)) for img in
            self.dialogue_images
        ]

        self.dialogue_index = 0
        running = True

        # Initialize the mixer for playing audio
        pygame.mixer.init()

        # Flag to check if narration is playing
        self.narration_playing = False

        def play_narration():
            """Play the narration for the current dialogue line."""
            self.narration_playing = True
            self.dialogue_sounds[self.dialogue_index].play()
            pygame.time.set_timer(pygame.USEREVENT, int(self.dialogue_sounds[self.dialogue_index].get_length() * 1000))

        # Play the first narration automatically
        play_narration()

        while running:
            self.display.fill((0, 0, 0))  # Black background for the dialogue screen

            # Display the corresponding image
            self.display.blit(self.dialogue_images[self.dialogue_index], (0, 0))

            # Create and display the dialogue box
            dialogue_box_rect = pygame.Rect(0, self.display.get_height() - 150, self.display.get_width(), 150)
            pygame.draw.rect(self.display, (0, 0, 0), dialogue_box_rect)

            # Render the current dialogue line
            dialogue_text = self.dialogue_font.render(self.dialogue_lines[self.dialogue_index], True,
                                                      (255, 255, 255))  # White font
            dialogue_rect = dialogue_text.get_rect(
                center=(self.display.get_width() // 2, self.display.get_height() - 75))
            self.display.blit(dialogue_text, dialogue_rect)

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    sys.exit()

                # Allow the player to skip the narration and move to the next slide with the spacebar
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.dialogue_sounds[self.dialogue_index].stop()  # Stop the current narration
                        self.narration_playing = False
                        self.dialogue_index += 1
                        if self.dialogue_index >= len(self.dialogue_lines):
                            running = False  # End the dialogue and start the game
                        else:
                            play_narration()  # Play the next narration

                # Check if narration finished
                if event.type == pygame.USEREVENT and self.narration_playing:
                    self.narration_playing = False
                    self.dialogue_index += 1
                    if self.dialogue_index >= len(self.dialogue_lines):
                        running = False  # End the dialogue and start the game
                    else:
                        play_narration()  # Play the next narration

            pygame.display.update()

    def run_dialogue_strip_3(self):
        self.dialogue_font = pygame.font.Font(None, 36)

        # Dialogue list (narrating the FourthLevel)
        self.dialogue_lines = [
            "I GOT THEM ALL CORRECT, ADVENTURER! NOW IS YOUR TIME!!",
            "Lexi shouts as he tells the adventurer to now fight. There is already a bright future ahead.",
            "The adventurer rushes forward, without second thought. This is the final moment of the final battle.",
        ]

        # Corresponding images for each dialogue line
        self.dialogue_images = [
            pygame.image.load(os.path.join('graphics', 'final-cutscene-1.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'final-cutscene-2.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'final-cutscene-3.png')).convert_alpha(),
        ]

        # Corresponding narration files for each dialogue line
        self.dialogue_sounds = [
            pygame.mixer.Sound(os.path.join('audio', 'final-owl-1.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'final-narrator-4.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'final-narrator-5.mp3')),
        ]

        # Scale the images to fit the screen
        self.dialogue_images = [
            pygame.transform.scale(img, (self.display.get_width(), self.display.get_height() - 150)) for img in
            self.dialogue_images
        ]

        self.dialogue_index = 0
        running = True

        # Initialize the mixer for playing audio
        pygame.mixer.init()

        # Flag to check if narration is playing
        self.narration_playing = False

        def play_narration():
            """Play the narration for the current dialogue line."""
            self.narration_playing = True
            self.dialogue_sounds[self.dialogue_index].play()
            pygame.time.set_timer(pygame.USEREVENT, int(self.dialogue_sounds[self.dialogue_index].get_length() * 1000))

        # Stop any currently playing narration before starting the new one
        for sound in self.dialogue_sounds:
            sound.stop()

        # Play the first narration automatically
        play_narration()

        while running:
            self.display.fill((0, 0, 0))  # Black background for the dialogue screen

            # Display the corresponding image
            self.display.blit(self.dialogue_images[self.dialogue_index], (0, 0))

            # Create and display the dialogue box
            dialogue_box_rect = pygame.Rect(0, self.display.get_height() - 150, self.display.get_width(), 150)
            pygame.draw.rect(self.display, (0, 0, 0), dialogue_box_rect)

            # Render the current dialogue line
            dialogue_text = self.dialogue_font.render(self.dialogue_lines[self.dialogue_index], True,
                                                      (255, 255, 255))  # White font
            dialogue_rect = dialogue_text.get_rect(
                center=(self.display.get_width() // 2, self.display.get_height() - 75))
            self.display.blit(dialogue_text, dialogue_rect)

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    sys.exit()

                # Allow the player to skip the narration and move to the next slide with the spacebar
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.dialogue_sounds[self.dialogue_index].stop()  # Stop the current narration
                        self.narration_playing = False
                        self.dialogue_index += 1
                        if self.dialogue_index >= len(self.dialogue_lines):
                            running = False  # End the dialogue and start the game
                        else:
                            play_narration()  # Play the next narration

                # Check if narration finished
                if event.type == pygame.USEREVENT and self.narration_playing:
                    self.narration_playing = False
                    self.dialogue_index += 1
                    if self.dialogue_index >= len(self.dialogue_lines):
                        running = False  # End the dialogue and start the game
                    else:
                        play_narration()  # Play the next narration

            pygame.display.update()

    def load_spritesheets(self):
        for i in range(1, 14):  # Load sheets from 1 to 13
            sheet_name = f'Final-Scene-Dyscape-Sheet-{i}.png'
            sheet_path = os.path.join('graphics', sheet_name)
            spritesheet = pygame.image.load(sheet_path).convert_alpha()
            self.extract_frames(spritesheet)

    def extract_frames(self, spritesheet):
        # Frame size
        frame_width = 1280
        frame_height = 720
        sheet_width, sheet_height = spritesheet.get_size()

        # Extract frames from the spritesheet
        for y in range(0, sheet_height, frame_height):
            for x in range(0, sheet_width, frame_width):
                # Ensure we don't go out of bounds
                if x + frame_width <= sheet_width and y + frame_height <= sheet_height:
                    frame = spritesheet.subsurface((x, y, frame_width, frame_height))
                    self.frames.append(frame)

    def animate_frames(self):
        # This method will handle the animation of frames
        clock = pygame.time.Clock()
        frame_index = 0
        total_frames = len(self.frames)

        while frame_index < total_frames:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            self.display.fill(FERN_GREEN)
            self.display.blit(self.frames[frame_index], (0, 0))  # Display frame at (0, 0)
            pygame.display.flip()
            frame_index += 1
            clock.tick(11)  # Control the speed of the animation (frames per second)

        pygame.time.delay(1700)
        self.gameStateManager.set_state('ending')

    def run_qa_session(self):
        font = pygame.font.Font(None, 36)
        question_index = 0
        correct_answers = 0
        total_questions = len(self.questions)
        running = True

        while running:
            question_data = self.questions[question_index]

            # Load and display the background for the current question
            background_image = pygame.image.load(question_data["background"]).convert()
            self.display.blit(background_image, (0, 0))  # Display background image

            # Render and display question text
            question_text = font.render(question_data["question"], True, (255, 255, 255))
            question_rect = question_text.get_rect(
                center=(self.display.get_width() // 2, self.display.get_height() // 2 - 50))  # Center the question text
            self.display.blit(question_text, question_rect.topleft)  # Blit question text on top of the background

            # Display options and keep track of their rects for clicking
            y_offset = 50  # Start position for options below the question
            option_rects = []  # To store the rectangles for options
            button_color = (40, 107, 120)  # Blue color for the button
            hover_color = (190, 69, 27)  # Darker blue for hover effect

            for idx, option in enumerate(question_data["options"]):
                # Calculate button position and size
                button_rect = pygame.Rect(
                    (self.display.get_width() // 2 - 100, self.display.get_height() // 2 + y_offset - 20),
                    (200, 40))  # Centered button
                option_rects.append(button_rect)  # Store the rect for this option

                # Check for mouse hover
                mouse_pos = pygame.mouse.get_pos()
                if button_rect.collidepoint(mouse_pos):
                    pygame.draw.rect(self.display, hover_color, button_rect)  # Draw darker button on hover
                else:
                    pygame.draw.rect(self.display, button_color, button_rect)  # Draw normal button

                # Render option text and center it within the button
                option_text = font.render(f"{option}", True, (255, 255, 255))
                text_rect = option_text.get_rect(center=button_rect.center)  # Center text in button
                self.display.blit(option_text, text_rect.topleft)  # Blit option text on top of the button
                y_offset += 50  # Increment y_offset for the next option

            # Event handling for selecting an answer
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        mouse_pos = pygame.mouse.get_pos()  # Get the mouse position
                        for idx, button_rect in enumerate(option_rects):
                            if button_rect.collidepoint(mouse_pos):  # Check if mouse is over this option
                                selected_option = question_data["options"][idx]
                                if selected_option == question_data["correct"]:
                                    correct_answers += 1
                                    question_index += 1
                                else:
                                    # Reset on incorrect answer
                                    question_index = 0
                                    correct_answers = 0

                                # Check if all questions were answered correctly
                                if correct_answers == total_questions:
                                    running = False
                                    # self.animate_frames()  # Uncomment if you have an animation function
                                elif question_index >= total_questions:
                                    question_index = 0
                                    correct_answers = 0

            pygame.display.flip()
            pygame.time.Clock().tick(60)

    def run(self):
        pygame.mixer.init()
        pygame.mixer.music.unload()
        pygame.mixer.music.load(os.path.join('audio', '02 Wonderin.mp3'))
        pygame.mixer.music.set_volume(0.05)
        pygame.mixer.music.play(-1)
        self.run_dialogue_strip()
        self.run_dialogue_strip_1()
        self.run_dialogue_strip_2()
        pygame.mixer.music.stop()

        # Load and play the background music
        pygame.mixer.init()
        pygame.mixer.music.unload()
        pygame.mixer.music.load(os.path.join('audio', 'final-battle-ost.wav'))
        pygame.mixer.music.set_volume(0.05)
        pygame.mixer.music.play(-1)  # Loop the music indefinitely

        self.run_qa_session()
        self.run_dialogue_strip_3()
        pygame.mixer.music.stop()

        pygame.mixer.music.load(os.path.join('audio', 'final-battle-ost(fight-part).wav'))
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(-1)
        # Stop the background music after the animation
        self.animate_frames()
        pygame.mixer.music.stop()

class Ending:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager

    def run_dialogue_strip(self):
        self.dialogue_font = pygame.font.Font(None, 36)

        # Dialogue list (narrating the FourthLevel)
        self.dialogue_lines = [
            "After the intense battle, Confusion was finally thrown out of the tower and starts vanishing to thin air.",
            "Freed from the curses of Confusion, the people regained their knowledge that was taken from them.",
            "While everyone was rejoicing, the Traveler rushed towards Lexi, who was lying on the ground after\n his power was exhausted from the battle.",
            "As Lexi’s eyes are getting heavier, he then explained that the cost of lending his power is falling\n into deep slumber.",
            "As the tears fell from the Traveler’s eyes,  he noticed the glowing particles coming out of his body,\n like the glistening stars in the night.",
            "Lexi smiled weakly towards him, and before he knew it, he left the world of Dyscape without a trace.",
            " ",
            "Months have passed since he returned to his world, but the Traveler could not forget for a second every\n adventure he had experienced.",
            "Hopeful for another encounter, he kept coming back to the same spot where it all began.",
            "On one fateful day, where the calm breeze kissed his cheek, he heard a familiar voice coming from the lake,\n as if an old friend calling him.",
            "The glowing water reflected the rays of the sun, and with a smile on his face, his heart leapt for joy.",
            "He ran towards the lake and jumped into the water, knowing that another adventure awaits him\n in the world of Dyscape."
        ]

        # Corresponding images for each dialogue line
        self.dialogue_images = [
            pygame.image.load(os.path.join('graphics', 'Confusion-Defeated-1.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'Confusion-Defeated-2.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'Confusion-Defeated-3.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'Confusion-Defeated-4.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'Confusion-Defeated-5.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'Confusion-Defeated-6.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'black-screen.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'Confusion-Defeated-7.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'Confusion-Defeated-8.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'Confusion-Defeated-9.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'Confusion-Defeated-10.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'Confusion-Defeated-11.png')).convert_alpha(),

        ]

        # Corresponding narration files for each dialogue line
        self.dialogue_sounds = [
            pygame.mixer.Sound(os.path.join('audio', 'ending-narrator-1.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'ending-narrator-2.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'ending-narrator-3.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'ending-narrator-4.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'ending-narrator-5.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'ending-narrator-6.mp3')),
            pygame.mixer.Sound(os.path.join('audio', '500-milliseconds-of-silence.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'ending-narrator-7.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'ending-narrator-8.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'ending-narrator-9.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'ending-narrator-10.mp3')),
            pygame.mixer.Sound(os.path.join('audio', 'ending-narrator-11.mp3')),

        ]

        # Scale the images to fit the screen
        self.dialogue_images = [
            pygame.transform.scale(img, (self.display.get_width(), self.display.get_height() - 150)) for img in
            self.dialogue_images
        ]

        self.dialogue_index = 0
        running = True

        # Initialize the mixer for playing audio
        pygame.mixer.init()

        # Flag to check if narration is playing
        self.narration_playing = False

        def play_narration():
            """Play the narration for the current dialogue line."""
            self.narration_playing = True
            self.dialogue_sounds[self.dialogue_index].play()
            pygame.time.set_timer(pygame.USEREVENT, int(self.dialogue_sounds[self.dialogue_index].get_length() * 1000))

        # Stop any currently playing narration before starting the new one
        for sound in self.dialogue_sounds:
            sound.stop()

        # Play the first narration automatically
        play_narration()

        while running:
            self.display.fill((0, 0, 0))  # Black background for the dialogue screen

            # Display the corresponding image
            self.display.blit(self.dialogue_images[self.dialogue_index], (0, 0))

            # Create and display the dialogue box
            dialogue_box_rect = pygame.Rect(0, self.display.get_height() - 150, self.display.get_width(), 150)
            pygame.draw.rect(self.display, (0, 0, 0), dialogue_box_rect)

            # Render the current dialogue line
            dialogue_text = self.dialogue_font.render(self.dialogue_lines[self.dialogue_index], True,
                                                      (255, 255, 255))  # White font
            dialogue_rect = dialogue_text.get_rect(
                center=(self.display.get_width() // 2, self.display.get_height() - 75))
            self.display.blit(dialogue_text, dialogue_rect)

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    sys.exit()

                # Allow the player to skip the narration and move to the next slide with the spacebar
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.dialogue_sounds[self.dialogue_index].stop()  # Stop the current narration
                        self.narration_playing = False
                        self.dialogue_index += 1
                        if self.dialogue_index >= len(self.dialogue_lines):
                            running = False  # End the dialogue and start the game
                        else:
                            play_narration()  # Play the next narration

                # Check if narration finished
                if event.type == pygame.USEREVENT and self.narration_playing:
                    self.narration_playing = False
                    self.dialogue_index += 1
                    if self.dialogue_index >= len(self.dialogue_lines):
                        running = False  # End the dialogue and start the game
                    else:
                        play_narration()  # Play the next narration

            pygame.display.update()

    def display_ending_screen(self):
        running = True
        self.display.fill((0, 0, 0))  # Set black background

        # Set fonts for the main text and subtext
        main_font = pygame.font.Font(None, 60)
        sub_font = pygame.font.Font(None, 36)

        # Render the main text
        main_text = main_font.render("YOU HAVE COMPLETED YOUR DYSCAPE ADVENTURE!", True, (255, 255, 255))
        main_rect = main_text.get_rect(center=(self.display.get_width() // 2, self.display.get_height() // 2 - 20))

        # Render the subtext
        sub_text = sub_font.render("You can still play all levels though.", True, (255, 255, 255))
        sub_rect = sub_text.get_rect(center=(self.display.get_width() // 2, self.display.get_height() // 2 + 40))

        # Create a button rectangle
        button_rect = pygame.Rect(self.display.get_width() // 2 - 75, self.display.get_height() // 2 + 100, 150, 50)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and button_rect.collidepoint(event.pos):
                        running = False  # Exit the loop to go back to main menu
                        self.gameStateManager.set_state('main-menu')

            # Fill the background
            self.display.fill((0, 0, 0))

            # Draw the main text and subtext
            self.display.blit(main_text, main_rect)
            self.display.blit(sub_text, sub_rect)

            # Draw the button
            pygame.draw.rect(self.display, (100, 100, 100), button_rect)  # Gray button
            button_text = sub_font.render("Main Menu", True, (255, 255, 255))
            button_text_rect = button_text.get_rect(center=button_rect.center)
            self.display.blit(button_text, button_text_rect)

            pygame.display.update()

    def run(self):
        pygame.mixer.init()
        pygame.mixer.music.unload()
        pygame.mixer.music.load(os.path.join('audio', '04 Aftermath.mp3'))
        pygame.mixer.music.set_volume(0.05)
        pygame.mixer.music.play(-1)
        self.run_dialogue_strip()
        pygame.mixer.music.stop()

        self.display_ending_screen()






class GameStateManager:
    def __init__(self, currentState):
        self.currentState = currentState

    def get_state(self):
        return self.currentState

    def set_state(self, state):
        print(f"Switching to state: {state}")  # Debugging line
        self.currentState = state


if __name__ == "__main__":
    game = Game()
    game.run()
