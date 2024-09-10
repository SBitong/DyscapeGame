import pygame
import sys
import os
import random
import time
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
        self.thirdLevel = ThirdLevel(self.screen, self.gameStateManager)
        self.states = {'main-menu': self.mainMenu, 'options': self.options, 'first-level': self.firstLevel, 'third-level': self.thirdLevel}

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

        self.player_x, self.player_y = WIDTH // 2, HEIGHT // 2
        self.player_speed = 3.5  # Adjusted speed for better visibility
        self.level_complete = False

        # Button to proceed to third level (shown after level completion)
        self.next_level_button_rect = pygame.Rect(WIDTH // 2 - 75, HEIGHT // 2, 150, 50)
        self.next_button_hovered = False

        # Load the sprite sheets from the specified path
        self.sprite_sheet_path_Idle = os.path.join('graphics', 'Idle.png')
        self.sprite_sheet_Idle = pygame.image.load(self.sprite_sheet_path_Idle).convert_alpha()

        # Animation parameters
        self.frame_width = 48  # Width of a single frame in the sprite sheet
        self.frame_height = 48  # Height of a single frame in the sprite sheet
        self.scale = 1.5  # Scale factor for enlarging the sprite
        self.num_frames_Idle = 9  # Number of frames in the idle sprite sheet
        self.animation_speed = 0.1  # Seconds per frame
        self.current_frame = 0
        self.elapsed_time = 0
        self.last_time = pygame.time.get_ticks()
        self.clock = pygame.time.Clock()

        self.idle = True
        self.facing_right = True  # Assume the character starts facing right

        # Shadow parameters
        self.shadow_width = 30  # Width of the shadow ellipse
        self.shadow_height = 10  # Height of the shadow ellipse
        self.shadow_surface = pygame.Surface((self.shadow_width, self.shadow_height), pygame.SRCALPHA)
        pygame.draw.ellipse(self.shadow_surface, (0, 0, 0, 100), [0, 0, self.shadow_width, self.shadow_height])

    def get_frame(self, sheet, frame, width, height, scale, flip=False):
        frame_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        frame_surface.blit(sheet, (0, 0), (frame * width, 0, width, height))
        scaled_surface = pygame.transform.scale(frame_surface, (width * scale, height * scale))
        if flip:
            scaled_surface = pygame.transform.flip(scaled_surface, True, False)
        return scaled_surface

    def run(self):
        # If the level is complete, show the "Next Level" button
        if self.level_complete:
            self.display.fill((0, 0, 0))
            next_level_text = pygame.font.SysFont(FONT_NAME, 40).render("Next Level", True, (255, 255, 255))
            pygame.draw.rect(self.display, (0, 128, 0), self.next_level_button_rect)
            self.display.blit(next_level_text, (self.next_level_button_rect.x + 10, self.next_level_button_rect.y + 10))

            mouse_pos = pygame.mouse.get_pos()

            if self.next_level_button_rect.collidepoint(mouse_pos):
                if not self.next_button_hovered:
                    self.next_button_hovered = True
                next_button_color = (0, 150, 0)
            else:
                next_button_color = (0, 128, 0)
                self.next_button_hovered = False

            pygame.draw.rect(self.display, next_button_color, self.next_level_button_rect)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.next_level_button_rect.collidepoint(event.pos):
                        self.gameStateManager.set_state('third-level')
            return

        # If the level is not complete, continue the first level gameplay
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:  # If Escape key is pressed
            self.gameStateManager.set_state('main-menu')  # Return to the main menu

        while True:
            # Event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Get the current key presses
            keys = pygame.key.get_pressed()
            moving = False
            if keys[pygame.K_w]:
                self.player_y -= self.player_speed
                moving = True
            if keys[pygame.K_s]:
                self.player_y += self.player_speed
                moving = True
            if keys[pygame.K_a]:
                self.player_x -= self.player_speed
                moving = True
                self.facing_right = False
            if keys[pygame.K_d]:
                self.player_x += self.player_speed
                moving = True
                self.facing_right = True

            self.idle = not moving

            # Update the animation frame
            current_time = pygame.time.get_ticks()
            self.elapsed_time += (current_time - self.last_time) / 1000.0
            self.last_time = current_time

            if self.elapsed_time > self.animation_speed:
                self.current_frame = (self.current_frame + 1) % self.num_frames_Idle  # Loop to the next frame
                self.elapsed_time = 0

            sprite_sheet = self.sprite_sheet_Idle
            frame_image = self.get_frame(sprite_sheet, self.current_frame, self.frame_width, self.frame_height, self.scale, not self.facing_right)

            # Fill the screen with the background color
            self.display.fill((0, 128, 128))

            # Update shadow position
            shadow_offset_x = 37  # Adjust the shadow offset as needed
            shadow_offset_y = 65
            self.display.blit(self.shadow_surface, (self.player_x - self.shadow_width // 2 + shadow_offset_x, self.player_y + shadow_offset_y))

            # Blit the current animation frame onto the screen
            self.display.blit(frame_image, (self.player_x, self.player_y))

            pygame.display.update()

            # Check for level completion (for testing purposes, we'll assume it completes after a keypress)
            if keys[pygame.K_RETURN]:  # Press "Enter" to complete the level
                self.level_complete = True
                break

            # Cap the frame rate
            self.clock.tick(FPS)


class ThirdLevel:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager

        # Initialize the word and syllables for the level
        self.word = "ELEPHANT"
        self.pronunciation = "e·le·phant"
        self.syllables = ["-phant", "le", "tron", "-toom"]  # Example syllables
        self.correct_syllable = "-phant"  # The correct syllable for the word

        # Initialize the font
        self.font = pygame.font.SysFont(FONT_NAME, 40)  # Adjust FONT_NAME and size if needed
        self.timer_font = pygame.font.SysFont(FONT_NAME, 30)  # Font for the timer

        # Initialize the start_time attribute to None
        self.start_time = None
        self.time_limit = 5  # 5 seconds to make a choice

        # Load the new water splash sprite sheet
        self.splash_sprite_sheet = pygame.image.load(os.path.join('graphics', 'Water Splash 01 - Spritesheet.png')).convert_alpha()

        # Get the sprite sheet size
        sprite_sheet_width, sprite_sheet_height = self.splash_sprite_sheet.get_size()

        # Splash animation settings
        self.num_rows = 3  # The number of rows in the sprite sheet
        self.num_cols = 5   # Number of columns (adjust if needed)
        self.num_splash_frames = self.num_rows * self.num_cols  # Total frames
        self.splash_frame_width = sprite_sheet_width // self.num_cols  # Width of each frame
        self.splash_frame_height = sprite_sheet_height // self.num_rows  # Height of each frame

        self.splash_frames = self.extract_splash_frames()  # Extract the frames from the sprite sheet
        self.splash_animation_speed = 0.1  # Time in seconds between each frame
        self.current_splash_frame = 0
        self.splash_timer = 0
        self.splash_active = False
        self.splash_positions = []  # Store splash positions for incorrect syllables

        # Load character image (idle sprite)
        self.character_image = pygame.image.load(os.path.join('graphics', 'idle.png')).convert_alpha()
        self.character_position = [WIDTH // 2 - 32, HEIGHT - 150]  # Center initial position

        # Track if the player has already selected
        self.player_selected = False

        # Define the syllable positions in the center
        self.syllable_radius = 100  # Adjust the size
        self.syllable_positions = self.center_syllables()

    def center_syllables(self):
        """Centers the syllables horizontally and positions them properly."""
        syllable_positions = []
        total_width = len(self.syllables) * (self.syllable_radius * 2 + 20)  # Total width needed for the syllables
        x_start = (WIDTH - total_width) // 2  # Start from the center horizontally

        for i, syllable in enumerate(self.syllables):
            x_position = x_start + i * (self.syllable_radius * 2 + 20)
            y_position = HEIGHT // 2 + 50  # Adjust to place the syllables vertically
            syllable_positions.append((x_position + self.syllable_radius, y_position))

        return syllable_positions

    def extract_splash_frames(self):
        frames = []
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                # Extract each frame based on row and column
                frame = self.splash_sprite_sheet.subsurface(pygame.Rect(
                    col * self.splash_frame_width, row * self.splash_frame_height,
                    self.splash_frame_width, self.splash_frame_height))
                frames.append(frame)
        return frames

    def run(self):
        # Ensure the start_time is set once when the level starts
        if self.start_time is None:
            self.start_time = time.time()

        running = True
        while running:
            elapsed_time = time.time() - self.start_time
            remaining_time = max(0, self.time_limit - elapsed_time)  # Countdown timer

            self.display.fill((135, 206, 250))  # Light blue background

            # Display the word and pronunciation
            word_text = self.font.render(f"The word is: {self.word}", True, (255, 255, 0))
            pronunciation_text = self.font.render(f"Pronunciation: {self.pronunciation}", True, (255, 255, 0))
            self.display.blit(word_text, (WIDTH // 2 - word_text.get_width() // 2, 50))
            self.display.blit(pronunciation_text, (WIDTH // 2 - pronunciation_text.get_width() // 2, 100))

            # Display the syllables
            for i, syllable in enumerate(self.syllables):
                syllable_text = self.font.render(syllable, True, (255, 255, 255))
                syllable_rect = syllable_text.get_rect(center=self.syllable_positions[i])
                pygame.draw.circle(self.display, (0, 0, 255), syllable_rect.center, self.syllable_radius)
                self.display.blit(syllable_text, syllable_rect)

            # Display the countdown timer
            timer_text = self.timer_font.render(f"Time: {remaining_time:.1f}", True, (255, 255, 255))
            self.display.blit(timer_text, (WIDTH - 150, 10))

            # Display the character
            self.display.blit(self.character_image, self.character_position)

            # Trigger and animate the splash effect if time runs out or player makes a selection
            if remaining_time <= 0 and not self.player_selected:
                self.trigger_incorrect_splashes()
                self.splash_active = True

            if self.splash_active:
                self.animate_splash()

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and remaining_time > 0:
                    mouse_x, mouse_y = event.pos

                    # Move character to mouse click position
                    self.character_position = [mouse_x - 32, mouse_y - 64]

                    if not self.player_selected:
                        for i, syllable in enumerate(self.syllables):
                            syllable_rect = self.font.render(syllable, True, (255, 255, 255)).get_rect(center=self.syllable_positions[i])
                            if syllable_rect.collidepoint(event.pos):
                                if syllable == self.correct_syllable:
                                    print("Correct!")
                                    self.player_selected = True  # Player has made the correct choice
                                    running = False  # End the level
                                else:
                                    print("Incorrect!")
                                    self.splash_positions.append(self.syllable_positions[i])  # Set splash position on incorrect syllable
                                    self.splash_active = True  # Activate the splash animation
                                    self.player_selected = True  # Player has made a selection

            pygame.display.update()
            pygame.time.Clock().tick(FPS)

        if self.player_selected and remaining_time <= 0:
            self.gameStateManager.set_state('main-menu')  # Reset to main menu if the player failed

    def trigger_incorrect_splashes(self):
        """Triggers splash animation for all incorrect syllables."""
        for i, syllable in enumerate(self.syllables):
            if syllable != self.correct_syllable:
                self.splash_positions.append(self.syllable_positions[i])
        self.splash_active = True

    def animate_splash(self):
        # Update the timer for frame change
        self.splash_timer += self.splash_animation_speed
        if self.splash_timer >= self.splash_animation_speed:
            self.splash_timer = 0  # Reset timer
            self.current_splash_frame += 1  # Move to next frame

            if self.current_splash_frame >= len(self.splash_frames):
                self.current_splash_frame = 0  # Loop the animation
                self.splash_active = False  # Stop the splash animation when complete

        # Draw the current frame of the splash at the given positions
        for pos in self.splash_positions:
            self.display.blit(self.splash_frames[self.current_splash_frame], pos)





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
