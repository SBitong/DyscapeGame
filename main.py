import pygame
import sys
import os
import random
import pyttsx3
import threading
from settings import *

# Initialize Pygame
pygame.init()
engine = pyttsx3.init()
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("DyscapeTheGame")

        self.gameStateManager = GameStateManager('ninth-level')
        self.mainMenu = MainMenu(self.screen, self.gameStateManager)
        self.options = Options(self.screen, self.gameStateManager)
        self.firstLevel = FirstLevel(self.screen, self.gameStateManager)
        self.eighthlevel = EighthLevel(self.screen, self.gameStateManager)
        self.ninthlevel = NinthLevel(self.screen, self.gameStateManager)
        self.states = {'main-menu': self.mainMenu, 'options': self.options, 'first-level': self.firstLevel, 'eighth-level': self.eighthlevel, 'ninth-level': self.ninthlevel}

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


class EighthLevel:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager
        self.lives = 3
        self.current_gate = 1
        self.win = False
        self.game_over = False
        self.end_screen_displayed = False  # Flag to track if end screen has been displayed


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

    def initialize_correct_slots(self):
        """Return the correct slots for the current level based on the current round."""
        if self.current_round < len(self.rounds):
            return self.rounds[self.current_round]["words"]  # Ensure this retrieves the correct order
        return []

    def run(self):
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
                            self.load_next_level()  # Replace with your method to load the next level
                        # Check if the Restart button is clicked
                        elif self.restart_button.collidepoint(mouse_pos):
                            self.reset_game()
                            print("Reset button clicked!")
                        # Check if the Exit button is clicked
                        elif self.exit_button.collidepoint(mouse_pos):
                            self.gameStateManager.set_state('main-menu')
                            running = False  # Exit the game loop (or you could go to the main menu)

            if self.game_over or self.win:
                if not self.end_screen_displayed:  # Check if end screen is not yet displayed
                    self.show_end_screen()  # Display the end screen
                    pygame.display.update()  # Update the display
                    self.end_screen_displayed = True  # Set flag to indicate end screen has been displayed
            else:
                self.draw()  # Only draw if the game is not over or won
                pygame.display.update()  # Update the display


class NinthLevel:
    class Syllable:
        def __init__(self, text, x, y, font_size):
            self.text = text
            self.rect = pygame.Rect(x, y, font_size * len(text), font_size)  # Adjusted for font size

        def fall(self, speed):
            self.rect.y += speed

        def draw(self, surface, font):
            text_surface = font.render(self.text, True, (0, 0, 0))
            surface.blit(text_surface, (self.rect.x, self.rect.y))

    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager

        # Initialize Pygame
        pygame.init()

        # Game constants
        self.WIDTH, self.HEIGHT = 1000, 500
        self.SYLLABLES = [
            {"word": "hospital", "syllables": ["hos", "pi", "tal"]},
            {"word": "banana", "syllables": ["ba", "na", "na"]},
            {"word": "computer", "syllables": ["com", "pu", "ter"]},
            {"word": "watermelon", "syllables": ["wa", "ter", "me", "lon"]},
            {"word": "powerful", "syllables": ["po", "wer", "ful"]},
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

        # Set up font
        self.font = pygame.font.Font(None, self.FONT_SIZE)

        # Load background image
        background_image_path = os.path.join('graphics', 'tower-final-bg.png')
        self.background_image = pygame.image.load(background_image_path).convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image,
                                                       (self.display.get_width(), self.display.get_height()))

        # Load Enemy image
        confusion_image_path = os.path.join('graphics', 'Confusion-Final-Form.png')
        self.enemy_image = pygame.image.load(confusion_image_path).convert_alpha()
        self.enemy_image = pygame.transform.scale(self.enemy_image, (300, 300))

        # Input box properties
        self.input_box_width = 600
        self.input_box_height = 50
        self.input_box_x = (self.display.get_width() - self.input_box_width) // 2  # Center horizontally
        self.input_box_y = self.display.get_height() - 100
        self.input_box = pygame.Rect(self.input_box_x, self.input_box_y, self.input_box_width, self.input_box_height)
        self.input_color = (255, 255, 255)  # White
        self.text_color = (0, 0, 0)  # Black
        self.current_text = ""

        # Game properties
        self.syllables = []
        self.spawn_timer = 0
        self.spawn_interval = 1000  # milliseconds

    def draw_text_box(self):
        # Draw the input box
        pygame.draw.rect(self.display, self.input_color, self.input_box, 0)
        text_surface = self.font.render(self.current_text, True, self.text_color)
        self.display.blit(text_surface, (self.input_box.x + 5, self.input_box.y + 5))

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

        # Update syllable positions
        for syllable in self.syllables:
            syllable.fall(1)  # Move syllables down
            if syllable.rect.y > self.HEIGHT:  # If a syllable hits the bottom
                self.LIVES -= 5
                print(f"Lives left: {self.LIVES}")
                self.syllables.remove(syllable)  # Remove the syllable if it falls off the screen
                if self.LIVES <= 0:
                    self.game_over()

        # Check for win condition
        if self.energy_level <= 0:
            print("You win!")
            self.gameStateManager.game_won()

    def spawn_next_word(self):
        # Choose a random word and its syllables
        word_data = random.choice(self.SYLLABLES)
        self.current_word = word_data["word"]  # Set current word
        print("Next word:", self.current_word)
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
                    if abs(existing_syllable.rect.x - x) < min_distance and abs(
                            existing_syllable.rect.y - y) < min_distance:
                        overlap = True
                        break

                # If no overlap, break the loop and add the syllable
                if not overlap:
                    break

            # Add the new syllable to the list
            self.syllables.append(self.Syllable(syllable_text, x, y, self.FONT_SIZE))
            self.energy_level -= 1  # Deduct energy level

    def draw_syllables(self):
        for syllable in self.syllables:
            syllable.draw(self.display, self.font)

    def draw_lives(self):
        self.draw_lifebar(self.LIVES, 100, 10, 10, 300, 30, (154, 213, 33),
                          (255, 255, 255))  # Green lifebar with white border
        lives_text = f"{self.LIVES} %"
        lives_surface = self.font.render(lives_text, True, (255, 255, 255))
        self.display.blit(lives_surface, (320, 10))  # Adjust text position accordingly

    def draw_energy(self):
        self.draw_lifebar(self.energy_level, 100, (WIDTH // 2) - (1000 // 2), 550, 1000, 30, (242, 96, 97),
                          (255, 255, 255))  # Blue energy bar with white border
        # energy_text = f"Energy: {self.energy_level}"
        # energy_surface = self.font.render(energy_text, True, (255, 255, 255))
        # self.display.blit(energy_surface, (320, 50))  # Adjust text position accordingly

    def game_over(self):
        print("Game Over")
        self.gameStateManager.game_over()

    def run(self):
        clock = pygame.time.Clock()
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
            self.display.blit(self.background_image, (0, 0))  # Background color
            self.display.blit(self.enemy_image, (WIDTH // 2 - (300 // 2), -50))
            self.draw_text_box()  # Draw the text box
            self.draw_syllables()  # Draw the syllables
            self.draw_lives()  # Draw lives
            self.draw_energy()  # Draw energy level
            pygame.display.flip()  # Update the display
            clock.tick(FPS)  # Limit to 60 frames per second


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
