import pygame
import sys
import os
import random
import pyttsx3
from settings import *

# Initialize Pygame
pygame.init()
engine = pyttsx3.init()

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("DyscapeTheGame")

        self.gameStateManager = GameStateManager('main-menu')
        self.mainMenu = MainMenu(self.screen, self.gameStateManager)
        self.options = Options(self.screen, self.gameStateManager)
        self.firstLevel = FirstLevel(self.screen, self.gameStateManager)
        self.states = {'main-menu': self.mainMenu, 'options': self.options, 'first-level': self.firstLevel}

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
        scale_factor = 2.5 #times two leaf size
        self.leaf_frames = self.extract_leaf_frames(self.springleaf_sprite, 5, scale_factor)
        self.leaves = [self.create_leaf() for x in range(30)]

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
        self.exitbutton_rect = pygame.Rect(((self.display.get_width() // 2) - (250 // 2), 600), (250, 70))

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
            "speed": random.uniform(1, 3),
            "animation_speed": random.uniform(0.1, 0.2),
            "animation_timer": 0,
            "horizontal_speed": random.uniform(-1, -0.5)
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
        if not self.main_menu_bgm_isplaying:
            self.main_menu_bgm.play(-1)
            print("bgm playing")
            self.main_menu_bgm_isplaying = True

        if not self.ambient_sound_isplaying:
            self.ambient_sound.play(-1)
            print("ambient sound playing")
            self.ambient_sound_isplaying = True
        # print("Running MainMenu state")  # Debugging line
        self.display.blit(self.background_image, (0, 0))

        self.display.blit(self.game_logo, ((WIDTH // 2)-(self.logo_width // 2), 90))


        mouse_pos = pygame.mouse.get_pos()

        if self.startbutton_rect.collidepoint(mouse_pos):
            if not self.start_button_hovered:
                self.hover_sound.play()
                self.start_button_hovered = True
            start_button_color = self.startbutton_hover_color
        else:
            start_button_color = self.startbutton_color
            self.start_button_hovered = False

        self.draw_button(self.startbutton_text, self.font, self.startbutton_rect, start_button_color, border_radius = 20)

        if self.optionbutton_rect.collidepoint(mouse_pos):
            if not self.option_button_hovered:
                self.hover_sound.play()
                self.option_button_hovered = True
            option_button_color = self.optionbutton_hover_color
        else:
            option_button_color = self.optionbutton_color
            self.option_button_hovered = False

        self.draw_button(self.optionbutton_text, self.font, self.optionbutton_rect, option_button_color, border_radius = 20)

        if self.exitbutton_rect.collidepoint(mouse_pos):
            if not self.exit_button_hovered:
                self.hover_sound.play()
                self.exit_button_hovered = True
            exit_button_color = self.exitbutton_hover_color
        else:
            exit_button_color = self.exitbutton_color
            self.exit_button_hovered = False

        self.draw_button(self.exitbutton_text, self.font, self.exitbutton_rect, exit_button_color, border_radius = 20)


        # Update and draw leaves
        for leaf in self.leaves:
            self.update_leaf(leaf)
            self.display.blit(self.leaf_frames[leaf["frame_index"]], (leaf["x"], leaf["y"]))

        # Example of adding a simple title
        # font = pygame.font.Font(None, 74)
        # title_text = font.render('Main Menu', True, (255, 255, 255))
        # self.display.blit(title_text, (100, 100))

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
                    print("Start Button Clicked!")
                    engine.say("Start")
                    engine.runAndWait()

                # Check if the options button is clicked
                elif self.optionbutton_rect.collidepoint(event.pos):
                    self.stop_sounds()
                    self.gameStateManager.set_state('options')
                    print("Options Button Clicked!")
                    engine.say("Options")
                    engine.runAndWait()

                elif self.exitbutton_rect.collidepoint(event.pos):
                    self.stop_sounds()
                    print("Exit Button Clicked!")
                    pygame.quit()
                    sys.exit()
        # keys = pygame.key.get_pressed()
        # if keys[pygame.K_RETURN]:  # If Enter key is pressed
        #     self.gameStateManager.set_state('first-level')  # Switch to the options menu

class Options:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager

        # Load the background image
        background_image_path = os.path.join('graphics', 'main-menu-background-1.jpg')
        self.background_image = pygame.image.load(background_image_path).convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image, (self.display.get_width(), self.display.get_height()))

        # Load the specified font
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)

        # Volume slider properties
        self.slider_length = 300
        self.slider_height = 10
        self.slider_color = (200, 200, 200)
        self.knob_color = (255, 255, 255)
        self.knob_radius = 10

        # Center the volume slider
        self.slider_x = (WIDTH - self.slider_length) // 2
        self.slider_y = HEIGHT // 3
        self.knob_position = self.slider_x + int(MASTER_VOLUME * self.slider_length)

        # TTS toggle button properties
        self.tts_toggle_rect = pygame.Rect((WIDTH - 150) // 2, self.slider_y + 100, 150, 50)
        self.tts_enabled = TTS_ENABLED

        # Font selection properties
        self.fonts = ["Arial", "Courier", "Comic Sans MS", "Georgia", "Times New Roman"]
        self.current_font_index = self.fonts.index(FONT_NAME) if FONT_NAME in self.fonts else 0
        self.font_rect = pygame.Rect((WIDTH - 300) // 2, self.tts_toggle_rect.y + 100, 300, 50)

    def run(self):
        running = True
        while running:
            self.display.blit(self.background_image, (0, 0))  # Draw the background image

            # Draw the volume slider
            pygame.draw.rect(self.display, self.slider_color, (self.slider_x, self.slider_y, self.slider_length, self.slider_height))
            pygame.draw.circle(self.display, self.knob_color, (self.knob_position, self.slider_y + self.slider_height // 2), self.knob_radius)

            # Display volume label
            volume_label = self.font.render("Master Volume", True, (255, 255, 255),)
            volume_label_rect = volume_label.get_rect(center=(WIDTH // 2, self.slider_y - 40))
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
        MASTER_VOLUME = (self.knob_position - self.slider_x) / self.slider_length
        pygame.mixer.music.set_volume(MASTER_VOLUME)

    def toggle_tts(self):
        self.tts_enabled = not self.tts_enabled
        TTS_ENABLED = self.tts_enabled

    def cycle_font(self):
        self.current_font_index = (self.current_font_index + 1) % len(self.fonts)
        FONT_NAME = self.fonts[self.current_font_index]
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)

    def save_settings(self):
        # Save the settings back to settings.py or some other persistent storage
        pass

class FirstLevel:
        def __init__(self, display, gameStateManager):
            self.display = display
            self.gameStateManager = gameStateManager
            self.screen_width, self.screen_height = self.display.get_size()  # Get screen size for responsiveness

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
                    ("ROOF", "POOF"), ("BAT", "CAT"), ("CROWN", "GOWN"), ("SEAT", "MEAT"), ("DOG", "HOG")
                ])
            ]

            # Draggable words scattered across the screen
            self.draggable_words = [
                {"word": word,
                 "rect": pygame.Rect(int(self.screen_width * (draggable_x_start_ratio + i * draggable_x_spacing_ratio)),
                                     int(self.screen_height * draggable_y_ratio), 150, 30),
                 "dragging": False,
                 "original_pos": (int(self.screen_width * (draggable_x_start_ratio + i * draggable_x_spacing_ratio)),
                                  int(self.screen_height * draggable_y_ratio)),
                 "placed": False}  # Add a 'placed' field to track if the word is correctly placed
                for i, word in enumerate(["ROOF", "BAT", "CROWN", "SEAT", "DOG"])
            ]

            # Load ladder (bridge) and heart images
            self.ladder_image = pygame.image.load(os.path.join('graphics', 'ladder-1.png')).convert_alpha()
            self.heart_image = pygame.image.load(os.path.join('graphics', 'heart.png')).convert_alpha()
            self.heart_image = pygame.transform.scale(self.heart_image, (80, 50))

            self.ladder_image = pygame.transform.scale(self.ladder_image,
                                                       (int(self.screen_width * 0.5), int(self.screen_height * 0.7)))

            # Game variables
            self.lives = 3
            self.selected_word = None
            self.offset_x = 0
            self.offset_y = 0

            # Game state variables
            self.game_over = False
            self.win = False

            # Load the Arial font
            font_path = os.path.join('fonts', 'ARIAL.TTF')
            self.font = pygame.font.Font(font_path, 20)

            # Initialize the Text-to-Speech engine
            self.tts_engine = pyttsx3.init()

        def speak_word(self, word):
            """Pronounce the word using Text-to-Speech (TTS)."""
            self.tts_engine.say(word)
            self.tts_engine.runAndWait()

        def show_end_screen(self):
            self.display.blit(self.bottom_platform, (0, 0))  # Draw the bottom platform
            self.display.blit(self.green_platform, (0, 320))  # Draw the green platform
            self.display.blit(self.ladder_image, (self.screen_width * 0.25, 0))  # Draw the ladder image
            overlay = pygame.Surface(self.display.get_size())
            overlay.set_alpha(150)  # Set transparency level
            overlay.fill((0, 0, 0))  # Black background
            self.display.blit(overlay, (0, 0))  # Fill the screen with black

            # Display the appropriate message based on win or loss
            message = "You Win!" if self.win else "Game Over!"
            text_surface = self.font.render(message, True, (255, 255, 255))
            self.display.blit(text_surface, (
                self.display.get_width() // 2 - text_surface.get_width() // 2, self.display.get_height() // 3))

            # Define Restart and Exit buttons
            self.restart_button = pygame.Rect(self.display.get_width() // 2 - 100, self.display.get_height() // 2, 200, 50)
            self.exit_button = pygame.Rect(self.display.get_width() // 2 - 100, self.display.get_height() // 2 + 70, 200, 50)

            # Draw the Restart button (Green)
            pygame.draw.rect(self.display, (0, 128, 0), self.restart_button)
            restart_text = self.font.render("Restart", True, (255, 255, 255))
            self.display.blit(restart_text, (self.restart_button.x + 50, self.restart_button.y + 10))

            # Draw the Exit button (Red)
            pygame.draw.rect(self.display, (128, 0, 0), self.exit_button)
            exit_text = self.font.render("Exit", True, (255, 255, 255))
            self.display.blit(exit_text, (self.exit_button.x + 70, self.exit_button.y + 10))

        def restart_level(self):
            # Reinitialize the level to reset all variables and the game state
            self.__init__(self.display, self.gameStateManager)
            self.gameStateManager.set_state('first-level')  # Set the game state back to 'first-level'

        def exit_to_main_menu(self):
            # Change the game state to 'main-menu'
            self.gameStateManager.set_state('main-menu')

        def run_dialogue_strip_1(self):
            self.dialogue_font = pygame.font.Font(None, 36)

            # Dialogue list (narrating the FourthLevel)
            self.dialogue_lines = [
                "Dyscape was once a bright and wonderful place, a world full of words, learning, and light.",
                "Its kingdom was amazingly ruled by a king. Its skies were vibrant, and the land was abundant and filled with knowledge.",
                "Every citizen were living in prosper, and the community is thriving, showing the power of learning.",
                "But something bad was coming. An unknown being called Confusion infiltrated Dyscape.",
                "He destroyed the city, polluted the forest, and scrambled the landscapes.",
                "He hypnotized every citizen in the kingdom and stole their capability to sustain knowledge",
                "Under his will, Confusion took the king as the hostage and now resides in the tower",
                "Now, the world of Dyscape is engulfed in chaos, and it's only a matter of time before the world will drown into darkness.",
                "In an alternate world, there was a man who was camping in the woods near a lake.",
                "He was setting up his campfire when he heard a strange sound from the lake.",
                "He looked behind his back and saw a mysterious glow near the side of the lake.",
                "He went near the lake, and as soon as he was close, he heard a voice.",
                "'Help us, our world is in danger', the unknown voice said.",
                "He touched the water out of curiosity and suddenly, the water pulled him into the depths."
            ]

            # Corresponding images for each dialogue line
            self.dialogue_images = [
                pygame.image.load(os.path.join('graphics', 'Dyscape-from-top.png')).convert_alpha(),
                pygame.image.load(os.path.join('graphics', 'Dyscape-from-top.png')).convert_alpha(),
                pygame.image.load(os.path.join('graphics', 'Dyscape-from-top.png')).convert_alpha(),
                pygame.image.load(os.path.join('graphics', 'Dyscape-from-top.png')).convert_alpha(),
                pygame.image.load(os.path.join('graphics', 'Dyscape-from-top.png')).convert_alpha(),
                pygame.image.load(os.path.join('graphics', 'Dyscape-from-top.png')).convert_alpha(),
                pygame.image.load(os.path.join('graphics', 'Dyscape-from-top.png')).convert_alpha(),
                pygame.image.load(os.path.join('graphics', 'Dyscape-from-top.png')).convert_alpha(),
                pygame.image.load(os.path.join('graphics', 'Dyscape-from-top.png')).convert_alpha(),
                pygame.image.load(os.path.join('graphics', 'Dyscape-from-top.png')).convert_alpha(),
                pygame.image.load(os.path.join('graphics', 'Dyscape-from-top.png')).convert_alpha(),
                pygame.image.load(os.path.join('graphics', 'Dyscape-from-top.png')).convert_alpha(),
                pygame.image.load(os.path.join('graphics', 'Dyscape-from-top.png')).convert_alpha(),
                pygame.image.load(os.path.join('graphics', 'Dyscape-from-top.png')).convert_alpha(),
            ]

            # Corresponding narration files for each dialogue line
            self.dialogue_sounds = [
                pygame.mixer.Sound(os.path.join('audio', 'fourth-narrator-1.mp3')),
                pygame.mixer.Sound(os.path.join('audio', 'fourth-narrator-2.mp3')),
                pygame.mixer.Sound(os.path.join('audio', 'fourth-narrator-3.mp3')),
                pygame.mixer.Sound(os.path.join('audio', 'fourth-narrator-4.mp3')),
                pygame.mixer.Sound(os.path.join('audio', 'fourth-narrator-5.mp3')),
                pygame.mixer.Sound(os.path.join('audio', 'fourth-narrator-6.mp3'))
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

        def run(self):
            """Main game loop for the first level."""

            correct_answer_sound = pygame.mixer.Sound(os.path.join('audio', 'correct-answer.mp3'))
            wrong_answer_sound = pygame.mixer.Sound(os.path.join('audio', 'wrong-answer.mp3'))

            # self.run_dialogue_strip_1()
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
                                running = False

                            # Check if the Exit button is clicked
                            elif self.exit_button.collidepoint(event.pos):
                                self.exit_to_main_menu()  # Exit to the main menu if clicked
                                running = False

                    continue  # Skip the rest of the game loop while in the end screen

                # Main game logic
                self.display.blit(self.bottom_platform, (0, 0))  # Draw the bottom platform
                self.display.blit(self.green_platform, (0, 320))  # Draw the green platform
                self.display.blit(self.ladder_image, (self.screen_width * 0.25, 0))  # Draw the ladder image

                # Display lives (hearts)
                for i in range(self.lives):
                    self.display.blit(self.heart_image, (10 + i * 45, 10))

                # Display ladder slots and draggable words
                for slot in self.ladder_slots:
                    # Draw slot rectangles
                    if slot["color"] == (143, 86, 59):
                        pygame.draw.rect(self.display, slot["color"], slot["rect"])  # Full brown for correct placement
                    else:
                        pygame.draw.rect(self.display, slot["color"], slot["rect"], 3)

                    # Display the correct word (if any) in the slot
                    if slot["word"]:
                        text_surface = self.font.render(slot["word"], True, (255, 255, 255))
                        self.display.blit(text_surface, (slot["rect"].x + 15, slot["rect"].y + 5))

                    # Display the pair words next to the slots
                    pair_word_surface = self.font.render(slot["pair_word"], True, (255, 255, 255))
                    self.display.blit(pair_word_surface, (slot["rect"].x + 50, slot["rect"].y + 50))

                # Display the draggable words
                for word_data in self.draggable_words:
                    pygame.draw.rect(self.display, (143, 86, 59), word_data["rect"])  # Draw word rectangles
                    text_surface = self.font.render(word_data["word"], True, (255, 255, 255))
                    self.display.blit(text_surface, (word_data["rect"].x + 35, word_data["rect"].y + 5))

                mouse_pos = pygame.mouse.get_pos()

                # Move the selected word along with the mouse cursor
                if self.selected_word:
                    self.selected_word["rect"].x = mouse_pos[0] + self.offset_x
                    self.selected_word["rect"].y = mouse_pos[1] + self.offset_y

                # Event handling
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        # Handle word dragging logic
                        if not self.selected_word:
                            for word_data in self.draggable_words:
                                if word_data["rect"].collidepoint(event.pos) and not word_data["placed"]:
                                    self.selected_word = word_data
                                    self.offset_x = word_data["rect"].x - event.pos[0]
                                    self.offset_y = word_data["rect"].y - event.pos[1]
                                    break

                        # Check if the pair words (next to blank rectangles) are clicked for TTS
                        for slot in self.ladder_slots:
                            pair_word_rect = pygame.Rect(slot["rect"].x + 50, slot["rect"].y + 50, 100, 30)
                            if pair_word_rect.collidepoint(event.pos):
                                self.speak_word(slot["pair_word"])




                    elif event.type == pygame.MOUSEBUTTONUP:

                        # Handle word placement logic

                        if self.selected_word:
                            placed_in_slot = False
                            wrong_slot = False  # Flag to track if the word was placed in the wrong slot
                            for slot in self.ladder_slots:
                                if slot["rect"].colliderect(self.selected_word["rect"]) and not slot["occupied"]:
                                    placed_in_slot = True
                                    if slot["correct_word"] == self.selected_word["word"]:
                                        # Snap word into place if correct
                                        correct_answer_sound.play()
                                        self.selected_word["rect"].center = slot["rect"].center
                                        slot["word"] = self.selected_word["word"]
                                        slot["occupied"] = True
                                        slot["color"] = (143, 86, 59)  # Change color to brown for correct placement
                                        self.selected_word["placed"] = True
                                    else:
                                        # Word was placed in a wrong slot
                                        wrong_answer_sound.play()
                                        wrong_slot = True
                                        self.selected_word["rect"].x, self.selected_word["rect"].y = self.selected_word[
                                            "original_pos"]
                            # If the word was placed in a slot but it's wrong, deduct a life
                            if wrong_slot:
                                self.lives -= 1
                            # If the word was not placed in any slot, snap it back to its original position (no life deduction)
                            if not placed_in_slot:
                                self.selected_word["rect"].x, self.selected_word["rect"].y = self.selected_word[
                                    "original_pos"]

                            self.selected_word = None
                # Reset the selected word after placement

                # Check game over conditions
                if self.lives <= 0:
                    self.game_over = True
                    print("Game Over!")

                # Check win condition (all slots occupied)
                if all(slot["occupied"] for slot in self.ladder_slots):
                    self.win = True
                    print("You Win!")

                pygame.display.update()  # Update the display


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
