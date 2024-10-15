import pygame
import sys
import os
import random
import pyttsx3
import sqlite3
import json
import pronouncing
from settings import *
from database import create_tables, save_progress, load_progress, reset_progress, create_profile, load_profiles
from database import connect



# Initialize Pygame
pygame.init()
engine = pyttsx3.init()


class Game:
    def __init__(self):
        create_tables()  # Ensure the database tables are created

        # Initialize the active profile to None
        self.active_profile = None

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("DyscapeTheGame")

        # Pass 'self' to allow levels and menus to access the Game instance
        self.gameStateManager = GameStateManager('main-menu')
        self.mainMenu = MainMenu(self.screen, self.gameStateManager, self)  # Pass self
        self.nameInputScreen = NameInputScreen(self.screen, self)  # New screen for entering name
        self.options = Options(self.screen, self.gameStateManager)
        self.firstLevel = FirstLevel(self.screen, self.gameStateManager, self)  # Pass self
        self.secondLevel = SecondLevel(self.screen, self.gameStateManager, self)  # Pass self

        self.states = {
            'main-menu': self.mainMenu,
            'name-input': self.nameInputScreen,  # Add the name input screen
            'options': self.options,
            'first-level': self.firstLevel,
            'second-level': self.secondLevel
        }
        self.clock = pygame.time.Clock()

    def create_new_profile(self, name):
        if name:  # Check if a valid name was given
            self.active_profile = create_profile(name)
            if self.active_profile:
                print(f"Created new profile: {self.active_profile['name']}")
            else:
                print("Error creating profile")

    def load_profile(self):
        # Logic to load an existing profile
        self.active_profile = load_profiles()
        if self.active_profile:
            print(f"Loaded profile: {self.active_profile['name']}")

    def get_profile(self):
        return self.active_profile

    def run(self):
        while True:
            # Event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # Handle the event for the current state
                self.states[self.gameStateManager.get_state()].handle_event(event)

            # Run the current state
            self.states[self.gameStateManager.get_state()].run()

            # Update the display
            pygame.display.flip()

            # Cap the frame rate
            self.clock.tick(FPS)


class NameInputScreen:
    def __init__(self, display, game):
        self.display = display
        self.game = game
        self.input_active = True
        self.name = ""
        self.font = pygame.font.Font(None, 74)
        self.color_active = pygame.Color('dodgerblue2')
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color = self.color_inactive

        # Input box dimensions
        self.input_box = pygame.Rect((self.display.get_width() // 2) - 150, self.display.get_height() // 2, 300, 50)
        self.text_surface = self.font.render(self.name, True, self.color)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Toggle the active variable based on click inside input box
            if self.input_box.collidepoint(event.pos):
                self.input_active = True
                self.color = self.color_active
            else:
                self.input_active = False
                self.color = self.color_inactive

        if event.type == pygame.KEYDOWN:
            if self.input_active:
                if event.key == pygame.K_RETURN:
                    # Once player presses Enter, create the profile and start the game
                    self.game.create_new_profile(self.name)
                    self.game.gameStateManager.set_state('first-level')  # Go to the first level
                elif event.key == pygame.K_BACKSPACE:
                    # Handle backspace
                    self.name = self.name[:-1]
                else:
                    # Add new character to name
                    self.name += event.unicode
                # Re-render the text.
                self.text_surface = self.font.render(self.name, True, self.color)

    def run(self):
        self.display.fill((30, 30, 30))  # Clear screen with dark background

        # Render text box
        txt_surface = self.font.render(self.name, True, self.color)
        self.display.blit(txt_surface, (self.input_box.x + 5, self.input_box.y + 5))
        pygame.draw.rect(self.display, self.color, self.input_box, 2)

        # Draw some static instruction text
        instruction_font = pygame.font.Font(None, 36)
        instruction_text = instruction_font.render("Enter your profile name and press Enter", True, (255, 255, 255))
        self.display.blit(instruction_text, ((self.display.get_width() // 2) - instruction_text.get_width() // 2, self.display.get_height() // 2 - 80))

        pygame.display.flip()  # Update the screen

class MainMenu:
    def __init__(self, display, gameStateManager, game):
        self.display = display
        self.gameStateManager = gameStateManager
        self.game = game  # Store a reference to the Game instance

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
        self.background_image = pygame.transform.scale(self.background_image, (self.display.get_width(), self.display.get_height()))

        # Load the game logo
        game_logo_path = os.path.join('graphics', 'DYSCAPE-LOGO2.png')
        self.game_logo = pygame.image.load(game_logo_path).convert_alpha()
        self.logo_width, self.logo_height = self.game_logo.get_size()

        # Load, extract, and multiply the leaves from the spring-leaf spritesheet
        springleaf_path = os.path.join('graphics', 'Spring-Leaf.png')
        self.springleaf_sprite = pygame.image.load(springleaf_path).convert_alpha()
        scale_factor = 3  # times two leaf size
        self.leaf_frames = self.extract_leaf_frames(self.springleaf_sprite, 5, scale_factor)
        self.leaves = [self.create_leaf() for x in range(40)]

        # Start Button properties
        self.startbutton_color = (255, 200, 0)
        self.startbutton_hover_color = (255, 170, 0)
        self.startbutton_text = "Start"
        self.startbutton_rect = pygame.Rect((self.display.get_width() // 2 - 150, 400), (300, 80))

        # New Game Button properties
        self.newgame_button_color = (255, 200, 0)
        self.newgame_button_hover_color = (255, 170, 0)
        self.newgame_button_text = "New Game"
        self.newgame_button_rect = pygame.Rect((self.display.get_width() // 2 - 150, 300), (300, 80))

        # Load Game Button properties
        self.loadgame_button_color = (255, 200, 0)
        self.loadgame_button_hover_color = (255, 170, 0)
        self.loadgame_button_text = "Load Game"
        self.loadgame_button_rect = pygame.Rect((self.display.get_width() // 2 - 150, 400), (300, 80))

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

    def handle_event(self, event):
        """Handle events like mouse clicks or key presses."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.newgame_button_rect.collidepoint(event.pos):
                # Create new game
                self.game.create_new_profile()
                self.gameStateManager.set_state('first-level')  # Start the game

            elif self.loadgame_button_rect.collidepoint(event.pos):
                # Load an existing game
                self.game.load_profile()
                self.gameStateManager.set_state('first-level')  # Start the game

            elif self.exitbutton_rect.collidepoint(event.pos):
                pygame.quit()
                sys.exit()

    def draw_button(self, text, font, rect, color, border_radius=20):
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
            start_button_color = self.startbutton_hover_color if self.startbutton_rect.collidepoint(mouse_pos) else self.startbutton_color
            self.draw_button(self.startbutton_text, self.font, self.startbutton_rect, start_button_color)

            newgame_button_color = self.newgame_button_hover_color if self.newgame_button_rect.collidepoint(
                mouse_pos) else self.newgame_button_color
            self.draw_button(self.newgame_button_text, self.font, self.newgame_button_rect, newgame_button_color)

            loadgame_button_color = self.loadgame_button_hover_color if self.loadgame_button_rect.collidepoint(
                mouse_pos) else self.loadgame_button_color
            self.draw_button(self.loadgame_button_text, self.font, self.loadgame_button_rect, loadgame_button_color)

            option_button_color = self.optionbutton_hover_color if self.optionbutton_rect.collidepoint(mouse_pos) else self.optionbutton_color
            self.draw_button(self.optionbutton_text, self.font, self.optionbutton_rect, option_button_color)

            exit_button_color = self.exitbutton_hover_color if self.exitbutton_rect.collidepoint(mouse_pos) else self.exitbutton_color
            self.draw_button(self.exitbutton_text, self.font, self.exitbutton_rect, exit_button_color)

            # Update and draw leaves
            for leaf in self.leaves:
                self.update_leaf(leaf)
                self.display.blit(self.leaf_frames[leaf["frame_index"]], (leaf["x"], leaf["y"]))

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
    def __init__(self, display, gameStateManager, game):
        self.display = display
        self.gameStateManager = gameStateManager
        self.game = game  # Store a reference to the Game instance

        self.screen_width, self.screen_height = self.display.get_size()

        # Load platforms and background
        green_platform_path = os.path.join('graphics', 'First-Level-Platform.png')
        self.green_platform = pygame.image.load(green_platform_path).convert_alpha()

        bottom_platform_path = os.path.join('graphics', 'First-Level-Bottom-Platform.png')
        self.bottom_platform = pygame.image.load(bottom_platform_path).convert_alpha()

        # Ladder slots
        self.ladder_slots = [
            {"word": "", "rect": pygame.Rect(int(self.screen_width * 0.435), int(self.screen_height * (0.03 + i * 0.131)), 175, 30),
             "correct_word": correct_word, "occupied": False, "color": (251, 242, 54), "pair_word": pair_word}
            for i, (correct_word, pair_word) in enumerate([
                ("SHOES", "SHOES"), ("DOG", "DOG"), ("CROWN", "CROWN"), ("BALL", "BALL"), ("CAT", "CAT")
            ])
        ]

        # Draggable images
        self.draggable_images = [
            {"word": word,
             "image": pygame.image.load(os.path.join('graphics', f'{word.lower()}.png')).convert_alpha(),
             "rect": pygame.Rect(int(self.screen_width * (0.15 + i * 0.152)), int(self.screen_height * 0.72), 150, 80),
             "dragging": False, "original_pos": (int(self.screen_width * (0.15 + i * 0.152)), int(self.screen_height * 0.72)),
             "placed": False}
            for i, word in enumerate(["CAT", "CROWN", "BALL", "SHOES", "DOG"])
        ]

        # Scale images to fit
        for image_data in self.draggable_images:
            image_data["image"] = pygame.transform.scale(image_data["image"], (100, 100))

        # Load ladder and heart images
        self.ladder_image = pygame.image.load(os.path.join('graphics', 'ladder-1.png')).convert_alpha()
        self.ladder_image = pygame.transform.scale(self.ladder_image, (int(self.screen_width * 0.5), int(self.screen_height * 0.7)))

        self.heart_image = pygame.image.load(os.path.join('graphics', 'heart.png')).convert_alpha()
        self.heart_image = pygame.transform.scale(self.heart_image, (80, 50))

        # Game variables
        self.lives = 3
        self.selected_word = None
        self.offset_x = 0
        self.offset_y = 0
        self.game_over = False
        self.win = False

        # Load the Arial font
        font_path = os.path.join('fonts', 'ARIAL.TTF')
        self.font = pygame.font.Font(font_path, 20)

        # TTS engine
        self.tts_engine = pyttsx3.init()

        # Load speaker icon for TTS
        self.speaker_icon = pygame.image.load(os.path.join('graphics', 'audio-logo.png')).convert_alpha()
        self.speaker_icon = pygame.transform.scale(self.speaker_icon, (30, 30))

        # Load saved progress
        self.load_progress()

    def load_progress(self):
        """Method to load saved progress from the database."""
        profile = self.game.get_profile()  # Get the active profile
        if profile:
            profile_id = profile['id']  # Retrieve the profile ID
            with connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT lives, draggable_images, ladder_slots FROM first_level_progress WHERE profile_id = ? ORDER BY id DESC LIMIT 1',
                    (profile_id,))
                progress = cursor.fetchone()
                if progress:
                    self.lives = progress[0]
                    self.draggable_images = json.loads(progress[1])  # Convert JSON back to list
                    self.ladder_slots = json.loads(progress[2])  # Convert JSON back to list
                else:
                    print("No saved progress found for this profile.")
        else:
            print("No active profile.")

    def save_progress(self):
        """Method to save progress into the database."""
        draggable_images_json = json.dumps(self.draggable_images)  # Convert list to JSON
        ladder_slots_json = json.dumps(self.ladder_slots)  # Convert list to JSON

        profile = self.game.get_profile()  # Get the active profile
        if profile:
            profile_id = profile['id']  # Retrieve the profile ID
            with connect() as conn:
                cursor = conn.cursor()
                cursor.execute('''INSERT INTO first_level_progress (profile_id, lives, draggable_images, ladder_slots)
                                  VALUES (?, ?, ?, ?)''',
                               (profile_id, self.lives, draggable_images_json, ladder_slots_json))
                conn.commit()

    def draw_hearts(self):
        for i in range(self.lives):
            self.display.blit(self.heart_image, (10 + i * 60, 10))

    def speak_word(self, word):
        """Pronounce the word using Text-to-Speech (TTS)."""
        self.tts_engine.say(word)
        self.tts_engine.runAndWait()

    def run(self):
        """Main game loop for the first level."""
        running = True
        correct_answer_sound = pygame.mixer.Sound(os.path.join('audio', 'correct-answer.mp3'))
        wrong_answer_sound = pygame.mixer.Sound(os.path.join('audio', 'wrong-answer.mp3'))

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.display.blit(self.bottom_platform, (0, 0))  # Draw bottom platform
            self.display.blit(self.green_platform, (0, 320))  # Draw green platform
            self.display.blit(self.ladder_image, (self.screen_width * 0.25, 0))  # Draw ladder image

            # Display lives
            self.draw_hearts()

            # Display ladder slots and draggable images
            for slot in self.ladder_slots:
                pygame.draw.rect(self.display, slot["color"], slot["rect"], 3)
                speaker_icon_rect = self.speaker_icon.get_rect(center=(slot["rect"].centerx, slot["rect"].centery + 45))
                self.display.blit(self.speaker_icon, speaker_icon_rect)

            for word_data in self.draggable_images:
                if not word_data["placed"]:
                    self.display.blit(word_data["image"], word_data["rect"])

            # Handle dragging logic and interaction
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.selected_word:  # Ensure no other word is currently selected
                        for word_data in self.draggable_images:
                            if word_data["rect"].collidepoint(event.pos) and not word_data["placed"]:
                                self.selected_word = word_data
                                self.offset_x = word_data["rect"].x - event.pos[0]  # Capture offset between the image and mouse
                                self.offset_y = word_data["rect"].y - event.pos[1]
                                break

                        for slot in self.ladder_slots:
                            speaker_icon_rect = self.speaker_icon.get_rect(center=(slot["rect"].centerx, slot["rect"].centery + 45))
                            if speaker_icon_rect.collidepoint(event.pos):
                                self.speak_word(slot["pair_word"])

                elif event.type == pygame.MOUSEBUTTONUP:
                    if self.selected_word:
                        placed_in_slot = False
                        for slot in self.ladder_slots:
                            if slot["rect"].colliderect(self.selected_word["rect"]) and not slot["occupied"]:
                                if slot["correct_word"] == self.selected_word["word"]:
                                    # Snap word into place
                                    self.selected_word["rect"].center = slot["rect"].center
                                    slot["occupied"] = True
                                    slot["color"] = (143, 86, 59)  # Brown for correct placement
                                    self.selected_word["placed"] = True
                                    placed_in_slot = True
                                    break

                        # If the word is not placed in any valid slot, reset it to its original position
                        if not placed_in_slot:
                            self.selected_word["rect"].x, self.selected_word["rect"].y = self.selected_word["original_pos"]

                        self.selected_word = None  # Release the selected word

            # Update the screen
            pygame.display.update()


class SecondLevel:
    def __init__(self, display, gameStateManager, game):
        self.display = display
        self.gameStateManager = gameStateManager
        self.game = game  # Store reference to the Game object to access profile

        self.screen_width, self.screen_height = self.display.get_size()

        # Load saved progress
        profile = self.game.get_profile()  # Get the active profile
        if profile:
            profile_id = profile['id']  # Retrieve the profile ID
            progress = load_progress(profile_id)  # Pass profile_id to load_progress
            if progress and progress.get('level') == 'second-level':
                self.lives = progress['lives']
                self.current_time = progress.get('current_time', 120.0)
                self.rounds_completed = progress.get('rounds_completed', 0)
            else:
                # Set default values if no saved progress exists
                self.lives = 3
                self.current_time = 120.0
                self.rounds_completed = 0
        else:
            # If no profile is found, use default values
            self.lives = 3
            self.current_time = 120.0
            self.rounds_completed = 0

        # Words for the game
        self.flower_words = ["Tree", "Box", "Ball", "Duck", "Cat", "Dog", "Fish", "Bird", "Bed", "House"]
        random.shuffle(self.flower_words)
        self.current_flower_word = self.flower_words[self.rounds_completed]

        # Dictionary to map words to images (Make sure these paths are correct)
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

        # Initialize other game variables
        self.input_text = ''
        self.clock = pygame.time.Clock()
        self.last_time = pygame.time.get_ticks()

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

        self.current_animation = 'idle'
        self.tts_engine = pyttsx3.init()

    def draw_hearts(self):
        for i in range(self.lives):
            self.display.blit(self.heart_image, (10 + i * 60, 10))

    def run(self):
        self.current_time = 120.0  # 2 minutes timer
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Update the game logic
            self.current_time -= self.clock.get_time() / 1000.0  # Decrease time

            if self.current_time <= 0 or self.lives <= 0:
                self.game_over = True
                break

            pygame.display.update()  # Update the display
            self.clock.tick(60)  # Cap frame rate at 60 FPS

        # Save progress when exiting the level
        profile = self.game.get_profile()  # Get the active profile
        if profile:
            save_progress(profile['id'], 'second-level', self.lives, self.current_time, self.rounds_completed)


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
