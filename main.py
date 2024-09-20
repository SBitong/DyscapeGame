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

        self.gameStateManager = GameStateManager('fourth-level')
        self.mainMenu = MainMenu(self.screen, self.gameStateManager)
        self.options = Options(self.screen, self.gameStateManager)
        self.firstLevel = FirstLevel(self.screen, self.gameStateManager)
        self.fourthLevel = FourthLevel(self.screen, self.gameStateManager)
        self.states = {'main-menu': self.mainMenu, 'options': self.options, 'first-level': self.firstLevel, 'fourth-level': self.fourthLevel}

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

        # Load the sprite sheets from the specified path
        self.sprite_sheet_path_Idle = os.path.join('graphics', 'Idle.png')
        self.sprite_sheet_path_Run = os.path.join('graphics', 'Run.png')
        # -- self.sprite_sheet_path_Run = r'C:\Users\hp\Documents\Dyscape\DyscapeTheGame\graphics\Run.png'
        self.sprite_sheet_Idle = pygame.image.load(self.sprite_sheet_path_Idle).convert_alpha()
        self.sprite_sheet_Run = pygame.image.load(self.sprite_sheet_path_Run).convert_alpha()

        # Animation parameters
        self.frame_width = 48  # Width of a single frame in the sprite sheet
        self.frame_height = 48  # Height of a single frame in the sprite sheet
        self.scale = 1.5  # Scale factor for enlarging the sprite
        self.num_frames_Idle = 9  # Number of frames in the idle sprite sheet
        self.num_frames_Run = 9  # Number of frames in the run sprite sheet
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

        # Function to extract frames from the sprite sheet


    def get_frame(self, sheet, frame, width, height, scale, flip=False):
        frame_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        frame_surface.blit(sheet, (0, 0), (frame * width, 0, width, height))
        scaled_surface = pygame.transform.scale(frame_surface, (width * scale, height * scale))
        if flip:
            scaled_surface = pygame.transform.flip(scaled_surface, True, False)
        return scaled_surface


    def run(self):

        # Example of handling user input to return to the main menu
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:  # If Escape key is pressed
            self.gameStateManager.set_state('main-menu')  # Return to the main menu

        while True:
            # Event loop
            # print("Running First Level state")
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
                self.current_frame = (self.current_frame + 1) % (
                    self.num_frames_Idle if self.idle else self.num_frames_Run)  # Loop to the next frame
                self.elapsed_time = 0

            sprite_sheet = self.sprite_sheet_Idle if self.idle else self.sprite_sheet_Run
            frame_image = self.get_frame(sprite_sheet, self.current_frame, self.frame_width, self.frame_height, self.scale,
                                         not self.facing_right)

            # Fill the screen with the background color
            self.display.fill(FERN_GREEN)

            # Update shadow position
            shadow_offset_x = 37  # Adjust the shadow offset as needed
            shadow_offset_y = 65
            self.display.blit(self.shadow_surface,
                             (self.player_x - self.shadow_width // 2 + shadow_offset_x, self.player_y + shadow_offset_y))

            # Blit the current animation frame onto the screen
            self.display.blit(frame_image, (self.player_x, self.player_y))

            # Update the display
            pygame.display.update()

            # Cap the frame rate
            self.clock.tick(FPS)


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
