import pygame
import sys
import os
import random
import time
import pyttsx3
import pronouncing
import settings
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
        self.secondLevel = SecondLevel(self.screen, self.gameStateManager)
        self.thirdLevel = ThirdLevel(self.screen, self.gameStateManager)
        self.fourthLevel = FourthLevel(self.screen, self.gameStateManager)
        self.fifthLevel = FifthLevel(self.screen, self.gameStateManager)
        self.states = {'main-menu': self.mainMenu, 'options': self.options, 'first-level': self.firstLevel, 'second-level': self.secondLevel, 'third-level': self.thirdLevel, 'fourth-level': self.fourthLevel, 'fifth-level': self.fifthLevel}

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
            overlay.set_alpha(150)  # Set transparency level
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
            self.gameStateManager.set_state('first-level')  # Set the game state back to 'first-level'

        def exit_to_main_menu(self):
            # Change the game state to 'main-menu'
            self.reset_level()
            self.gameStateManager.set_state('main-menu')

        def run_dialogue_strip_1(self):
            self.dialogue_font = pygame.font.Font(None, 36)

            # Dialogue list (narrating the FourthLevel)
            self.dialogue_lines = [
                "Dyscape was once a bright and wonderful place, a world full of words, learning, and light.", # 1
                "Its kingdom was amazingly ruled by a king. Its skies were vibrant, and the land was abundant \n and filled with knowledge.", # 2
                "Every citizen were living in prosper, and the community is thriving, showing the power of learning.", # 3
                "But something bad was coming. An unknown being called Confusion infiltrated Dyscape.", # 4
                "He destroyed the city, polluted the forest, and scrambled the landscapes.", # 5
                "He hypnotized every citizen in the kingdom and stole their capability to sustain knowledge", # 6
                "Under his will, Confusion took the king as his hostage and now resides in the tower", # 7
                "Now, the world of Dyscape is engulfed in chaos, and it's only a  matter of time before the world \n will drown into darkness.", # 8
                " ", # Pause
                "In an alternate world, there was a man who was camping in the woods near a lake.", # 9
                "He was setting up his campfire when he heard a strange sound from the lake.", # 10
                "He looked behind his back and saw a mysterious glow near the side of the lake.", # 11
                "He went near the lake, and as soon as he was close, he heard a voice.", # 12
                "'Help us, our world is in danger', the unknown voice said.", # 13
                "He touched the water out of curiosity and suddenly, the water pulled him into the depths." # 14
            ]

            # Corresponding images for each dialogue line
            self.dialogue_images = [
                pygame.image.load(os.path.join('graphics', 'dyscape-1.png')).convert_alpha(), # 1
                pygame.image.load(os.path.join('graphics', 'Dyscape-from-top.png')).convert_alpha(), # 2
                pygame.image.load(os.path.join('graphics', 'inside-dyscape.png')).convert_alpha(), # 3
                pygame.image.load(os.path.join('graphics', 'confusion-arrives.png')).convert_alpha(), # 4
                pygame.image.load(os.path.join('graphics', 'dyscape-under-attack.png')).convert_alpha(), # 5
                pygame.image.load(os.path.join('graphics', 'confusion-hypnotize.png')).convert_alpha(), # 6
                pygame.image.load(os.path.join('graphics', 'king-strangle.png')).convert_alpha(), # 7
                pygame.image.load(os.path.join('graphics', 'dyscape-in-chaos.png')).convert_alpha(), # 8
                pygame.image.load(os.path.join('graphics', 'black-screen.png')).convert_alpha(), # Pause
                pygame.image.load(os.path.join('graphics', 'character-camping.png')).convert_alpha(), # 9
                pygame.image.load(os.path.join('graphics', 'strange-sound.png')).convert_alpha(), # 10
                pygame.image.load(os.path.join('graphics', 'mysterious-glow.png')).convert_alpha(), # 11
                pygame.image.load(os.path.join('graphics', 'glow-closeup.png')).convert_alpha(), # 12
                pygame.image.load(os.path.join('graphics', 'the-glow-speaks.png')).convert_alpha(), # 13
                pygame.image.load(os.path.join('graphics', 'glow-pulled-the-character.png')).convert_alpha(), # 14
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
                pygame.mixer.Sound(os.path.join('audio', 'first-narrator-14.mp3'))
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

        def run(self):
            """Main game loop for the first level."""

            correct_answer_sound = pygame.mixer.Sound(os.path.join('audio', 'correct-answer.mp3'))
            wrong_answer_sound = pygame.mixer.Sound(os.path.join('audio', 'wrong-answer.mp3'))

            speaker_icon = pygame.image.load(os.path.join('graphics', 'audio-logo.png')).convert_alpha()
            speaker_icon = pygame.transform.scale(speaker_icon, (30, 30))  # Resize the speaker icon to fit on the ladder

            # Only run the dialogue strip the first time the level is played
            if not self.dialogue_played:
                self.run_dialogue_strip_1()
                self.dialogue_played = True  # Set flag so it doesn't run again
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
                                self.gameStateManager.set_state('second-level')
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

class SecondLevel:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager
        self.screen_width, self.screen_height = self.display.get_size()

        # Initialize player attributes
        self.lives = 3
        self.time_limit = 15.0
        self.current_time = 0
        self.timer_started = False
        self.game_over = False

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

    def run_title_animation(self):
        title_heading = "Fifth Level:"
        title_text = "THE RHYMEAN GARDEN"
        font_path = os.path.join('fonts', 'ARIALBLACKITALIC.TTF')
        title_font = pygame.font.Font(font_path, 50)  # Large font for the title

        alpha = 0  # Start fully transparent
        max_alpha = 255
        fade_speed = 5  # How fast the title fades in and out

        running = True
        while running:
            self.display.fill((0,0,0))

            # Render the title with fading effect
            title_surface = title_font.render(title_text, True, (255,255,255))
            title_surface.set_alpha(alpha)  # Set transparency level
            title_rect = title_surface.get_rect(center=(self.display.get_width() // 2, self.display.get_height() // 2))
            self.display.blit(title_surface, title_rect)

            # Update the alpha to create fade-in effect
            alpha += fade_speed
            if alpha >= max_alpha:
                alpha = max_alpha
                pygame.time.delay(500)  # Pause for a short moment at full opacity

                # Fade out effect
                while alpha > 0:
                    self.display.fill((0,0,0))
                    title_surface.set_alpha(alpha)  # Set transparency level
                    self.display.blit(title_surface, title_rect)
                    alpha -= fade_speed
                    if alpha < 0:
                        alpha = 0
                    pygame.display.flip()
                    pygame.time.delay(30)  # Control the fade-out speed
                pygame.time.delay(80)
                running = False  # Exit the animation loop after fade-out

            pygame.display.flip()
            pygame.time.delay(30)  # Control the fade-in speed

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
        self.run_title_animation()
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
                        if event.key == pygame.K_ESCAPE:
                            self.gameStateManager.set_state('main-menu')
                            running = False
                        elif event.key == pygame.K_RETURN:
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
                        elif self.exit_button.collidepoint(event.pos):
                            self.gameStateManager.set_state('main-menu')
                            running = False
                        elif self.next_level_button.collidepoint(event.pos):
                            self.gameStateManager.set_state('third-level')
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





class ThirdLevel:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager
        self.lives = 3
        self.timer = 10.0  # 15 seconds timer for each word
        self.win = False
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
             "syllables": ["-wer", "-ing", "-state", "-s"],
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
             "syllables": ["-ti", "-kled", "-tus", "-ing"],
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

    def run_title_animation(self):
        title_heading = "Fifth Level:"
        title_text = "SYLLE LAGOON"
        font_path = os.path.join('fonts', 'ARIALBLACKITALIC.TTF')
        title_font = pygame.font.Font(font_path, 50)  # Large font for the title

        alpha = 0  # Start fully transparent
        max_alpha = 255
        fade_speed = 5  # How fast the title fades in and out

        running = True
        while running:
            self.display.fill((0,0,0))

            # Render the title with fading effect
            title_surface = title_font.render(title_text, True, (255,255,255))
            title_surface.set_alpha(alpha)  # Set transparency level
            title_rect = title_surface.get_rect(center=(self.display.get_width() // 2, self.display.get_height() // 2))
            self.display.blit(title_surface, title_rect)

            # Update the alpha to create fade-in effect
            alpha += fade_speed
            if alpha >= max_alpha:
                alpha = max_alpha
                pygame.time.delay(500)  # Pause for a short moment at full opacity

                # Fade out effect
                while alpha > 0:
                    self.display.fill((0,0,0))
                    title_surface.set_alpha(alpha)  # Set transparency level
                    self.display.blit(title_surface, title_rect)
                    alpha -= fade_speed
                    if alpha < 0:
                        alpha = 0
                    pygame.display.flip()
                    pygame.time.delay(30)  # Control the fade-out speed
                pygame.time.delay(80)
                running = False  # Exit the animation loop after fade-out

            pygame.display.flip()
            pygame.time.delay(30)  # Control the fade-in speed

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

    def show_end_screen(self):
        # Set up screen
        self.display.fill((0, 0, 0))  # Black background
        font = pygame.font.Font(None, 30)

        # Display message based on win or lose
        message_text = "You Win!" if self.win else "You Lose"
        message_surface = font.render(message_text, True, (255, 255, 255))
        message_rect = message_surface.get_rect(center=(self.display.get_width() // 2, self.display.get_height() // 3))
        self.display.blit(message_surface, message_rect)

        # Button setup
        button_font = pygame.font.Font(None, 30)

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
                        self.gameStateManager.set_state('next-level')
                        waiting = False

    def run(self):
        self.run_title_animation()
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



class FourthLevel:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager
        self.light_radius = 100  # Define the radius of the light
        self.lives = 3  # Player starts with 3 lives
        self.words_to_find = ["firefly", "tower", "letter", "forest", "tree", "bush", "cave", "leaf", "word", "escape", "almost", "trap", "done"]  # Words to find
        self.word_index = 0  # Start with the first word
        self.correct_word = self.words_to_find[self.word_index]  # Word to find on screen
        self.engine = pyttsx3.init()  # Text-to-speech engine

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
        self.heart_image = pygame.transform.scale(self.heart_image, (50, 50))  # Resize heart

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
            self.gameStateManager.go_to_next_level()
        else:
            self.correct_word = self.words_to_find[self.word_index]
            self.word_position = (random.randint(100, self.display.get_width() - 200), random.randint(100, self.display.get_height() - 200))

    def lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            print("Game Over!")
            self.gameStateManager.set_state('main-menu')
        else:
            print(f"Lives remaining: {self.lives}")

    def run_title_animation(self):
        title_heading = "Fifth Level:"
        title_text = "THE FOREST OF NOLITE"
        font_path = os.path.join('fonts', 'ARIALBLACKITALIC.TTF')
        title_font = pygame.font.Font(font_path, 50)  # Large font for the title

        alpha = 0  # Start fully transparent
        max_alpha = 255
        fade_speed = 5  # How fast the title fades in and out

        running = True
        while running:
            self.display.fill(BLACK)

            # Render the title with fading effect
            title_surface = title_font.render(title_text, True, WHITE)
            title_surface.set_alpha(alpha)  # Set transparency level
            title_rect = title_surface.get_rect(center=(self.display.get_width() // 2, self.display.get_height() // 2))
            self.display.blit(title_surface, title_rect)

            # Update the alpha to create fade-in effect
            alpha += fade_speed
            if alpha >= max_alpha:
                alpha = max_alpha
                pygame.time.delay(500)  # Pause for a short moment at full opacity

                # Fade out effect
                while alpha > 0:
                    self.display.fill(BLACK)
                    title_surface.set_alpha(alpha)  # Set transparency level
                    self.display.blit(title_surface, title_rect)
                    alpha -= fade_speed
                    if alpha < 0:
                        alpha = 0
                    pygame.display.flip()
                    pygame.time.delay(30)  # Control the fade-out speed
                pygame.time.delay(80)
                running = False  # Exit the animation loop after fade-out

            pygame.display.flip()
            pygame.time.delay(30)  # Control the fade-in speed

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
            {"name": "Magical Owl", "text": "Yes. This is the only path to the tower."},
            {"name": "You", "text": "Man, this gives me the creepy vibes.", "image": char1_image},
            {"name": "Magical Owl", "text": "This is a vibrant forest, traveler. Confusion drove away the fireflies"},
            {"name": "Magical Owl", "text": "As a result, the bright forest became a dull one."},
            {"name": "Magical Owl", "text": "We have to save this forest, and its fireflies."},
            {"name": "Magical Owl", "text": "And we have to go through here."},
            {"name": "You", "text": "Thank God, I brought my flashlight.", "image": char1_image},
        ]

        dialogue_box_height = 150  # Height of the dialogue box surface
        dialogue_font = pygame.font.Font(None, 32)  # Font for dialogue text
        name_font = pygame.font.Font(None, 36)  # Font for character names
        space_prompt_font = pygame.font.Font(None, 28)  # Font for "Press SPACE to continue"

        current_line = 0
        text_displayed = ""
        text_index = 0
        text_speed = 2  # Speed of text animation

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
        """Displays the 'how to play' instructions with a continue button."""
        running = True
        while running:
            self.display.blit(self.background_image, (0, 0))
            overlay = pygame.Surface(self.display.get_size())
            overlay.set_alpha(100)  # Set transparency level
            overlay.fill((0, 0, 0))  # Black background
            self.display.blit(overlay, (0, 0))  # Fill the screen with black

            # Display instructions
            instructions = [
                "Welcome to the Fourth Level",
                "1. In this game, your task is to find the correct words hidden to escape the forest.",
                "2. Use the left and right arrows to select whether the word is on the left or right side.",
                "3. If you guess wrong, you'll lose a life! You have 3 lives in total.",
                "Good luck, adventurer!"
            ]

            for i, line in enumerate(instructions):
                instruction_surface = self.font.render(line, True, (255, 255, 255))
                self.display.blit(instruction_surface,
                                  (self.display.get_width() // 2 - instruction_surface.get_width() // 2, 100 + i * 50))

            # Draw the continue button
            pygame.draw.rect(self.display, (255, 165, 0), self.continue_button)  # Orange button
            continue_text = self.font.render("Continue", True, (0, 0, 0))  # Black text
            self.display.blit(continue_text, (self.continue_button.x + 35, self.continue_button.y + 10))

            # Event handling for button click
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.continue_button.collidepoint(event.pos):
                        self.start_countdown()  # Start the countdown before the game
                        return

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

        correct_answer_sound = pygame.mixer.Sound(os.path.join('audio', 'correct-answer.mp3'))
        wrong_answer_sound = pygame.mixer.Sound(os.path.join('audio', 'wrong-answer.mp3'))

        self.run_title_animation()
        self.run_dialogue_strip_1()
        self.run_dialogue_strip_2()
        self.show_how_to_play()

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

            pygame.display.update()


class FifthLevel:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager
        self.font = pygame.font.Font(None, 36)
        self.white = WHITE
        self.black = BLACK
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

    def run_title_animation(self):
        title_heading = "Fifth Level:"
        title_text = "THE UNKNOWN TOAD"
        font_path = os.path.join('fonts','ARIALBLACKITALIC.TTF')
        title_font = pygame.font.Font(font_path, 50)  # Large font for the title

        alpha = 0  # Start fully transparent
        max_alpha = 255
        fade_speed = 5  # How fast the title fades in and out

        running = True
        while running:
            self.display.fill(self.black)

            # Render the title with fading effect
            title_surface = title_font.render(title_text, True, self.white)
            title_surface.set_alpha(alpha)  # Set transparency level
            title_rect = title_surface.get_rect(center=(self.display.get_width() // 2, self.display.get_height() // 2))
            self.display.blit(title_surface, title_rect)

            # Update the alpha to create fade-in effect
            alpha += fade_speed
            if alpha >= max_alpha:
                alpha = max_alpha
                pygame.time.delay(500)  # Pause for a short moment at full opacity

                # Fade out effect
                while alpha > 0:
                    self.display.fill(self.black)
                    title_surface.set_alpha(alpha)  # Set transparency level
                    self.display.blit(title_surface, title_rect)
                    alpha -= fade_speed
                    if alpha < 0:
                        alpha = 0
                    pygame.display.flip()
                    pygame.time.delay(30)  # Control the fade-out speed
                pygame.time.delay(80)
                running = False  # Exit the animation loop after fade-out

            pygame.display.flip()
            pygame.time.delay(30)  # Control the fade-in speed

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

    def show_game_over_prompt(self):
        # Fill the background with a semi-transparent overlay
        overlay = pygame.Surface(self.display.get_size())
        overlay.set_alpha(200)  # Set transparency level
        overlay.fill((0, 0, 0))  # Black background
        self.display.blit(overlay, (0, 0))

        # Render the "You lost" message
        game_over_text = "YOU LOST"
        game_over_surface = self.font.render(game_over_text, True, (255, 255, 255))
        game_over_rect = game_over_surface.get_rect(center=(self.display.get_width() // 2, 200))
        self.display.blit(game_over_surface, game_over_rect)

        # Define button positions and sizes
        button_width, button_height = 200, 50
        restart_button_rect = pygame.Rect(
            (self.display.get_width() // 2 - button_width // 2, 300), (button_width, button_height))
        main_menu_button_rect = pygame.Rect(
            (self.display.get_width() // 2 - button_width // 2, 400), (button_width, button_height))

        # Render buttons
        pygame.draw.rect(self.display, (50, 255, 50), restart_button_rect)
        restart_text_surface = self.font.render("Restart", True, (0, 0, 0))
        restart_text_rect = restart_text_surface.get_rect(center=restart_button_rect.center)
        self.display.blit(restart_text_surface, restart_text_rect)

        pygame.draw.rect(self.display, (236, 112, 22), main_menu_button_rect)
        main_menu_text_surface = self.font.render("Main Menu", True, (0, 0, 0))
        main_menu_text_rect = main_menu_text_surface.get_rect(center=main_menu_button_rect.center)
        self.display.blit(main_menu_text_surface, main_menu_text_rect)



        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if restart_button_rect.collidepoint(mouse_pos):
                        engine.say("Restart")
                        self.reset_level()
                        engine.runAndWait()
                        running = False
                    elif main_menu_button_rect.collidepoint(mouse_pos):
                        engine.say("Return")
                        self.reset_level()
                        self.gameStateManager.set_state('main-menu')
                        engine.runAndWait()
                        running = False
            pygame.display.update()

    def show_how_to_play(self):
        """Displays the 'how to play' instructions with a continue button."""
        running = True
        while running:
            self.display.blit(self.background_image, (0, 0))
            overlay = pygame.Surface(self.display.get_size())
            overlay.set_alpha(150)  # Set transparency level
            overlay.fill((0, 0, 0))  # Black background
            self.display.blit(overlay, (0, 0))  # Fill the screen with black

            # Display instructions
            instructions = [
                "Welcome to the Fifth Level",
                "1. In this game, your task is to answer all of the toad's questions",
                "2. Pick one out of all the choices.",
                "3. If you guess wrong, you'll lose a life! You have 3 lives in total.",
                "Good luck, adventurer!"
            ]

            for i, line in enumerate(instructions):
                instruction_surface = self.font.render(line, True, (255, 255, 255))
                self.display.blit(instruction_surface,
                                  (self.display.get_width() // 2 - instruction_surface.get_width() // 2, 100 + i * 50))

            # Draw the continue button
            pygame.draw.rect(self.display, (255, 165, 0), self.continue_button)  # Orange button
            continue_text = self.font.render("Continue", True, (0, 0, 0))  # Black text
            self.display.blit(continue_text, (self.continue_button.x + 35, self.continue_button.y + 10))

            # Event handling for button click
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.continue_button.collidepoint(event.pos):
                        self.start_countdown()  # Start the countdown before the game
                        return

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

    def run(self):
        heart_image = pygame.image.load(os.path.join('graphics', 'heart.png'))
        heart_image = pygame.transform.scale(heart_image, (40, 40))  # Scale heart image as needed

        # Load the paper scroll image
        scroll_image = pygame.image.load(os.path.join('graphics', 'paper-scroll.png'))
        scroll_width, scroll_height = 1000, 700  # Adjust these values as needed
        scroll_image = pygame.transform.scale(scroll_image, (scroll_width, scroll_height))

        # Load the audio button image
        audio_button_image = pygame.image.load(os.path.join('graphics', 'audio-logo.png'))
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
            self.run_title_animation()
            self.run_dialogue_strip()
        else:
            self.is_restart = False  # Reset the flag

        self.show_how_to_play()
        self.init_water_droplets()  # Initialize water droplets when the level starts

        running = True
        while running:
            self.display.blit(self.background_image, (0, 0))
            self.update_water_droplets()
            self.draw_water_droplets()

            # Display the number of hearts for lives
            for i in range(self.lives):
                self.display.blit(heart_image, (50 + i * 45, 20))  # Position hearts with spacing

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
                                    self.show_game_over_prompt()
                                    running = False
                                    break

                            if self.current_question_index >= len(self.questions):
                                print("Level completed!")
                                self.gameStateManager.set_state('main-menu')
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
