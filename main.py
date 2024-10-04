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
        self.fifthLevel = FifthLevel(self.screen, self.gameStateManager)
        self.states = {'main-menu': self.mainMenu, 'options': self.options, 'first-level': self.firstLevel, 'fifth-level': self.fifthLevel}

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
                    self.gameStateManager.set_state('fifth-level')
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
            pass
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
