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

        self.gameStateManager = GameStateManager('final-level')
        self.mainMenu = MainMenu(self.screen, self.gameStateManager)
        self.options = Options(self.screen, self.gameStateManager)
        self.firstLevel = FirstLevel(self.screen, self.gameStateManager)
        self.eighthlevel = EighthLevel(self.screen, self.gameStateManager)
        self.ninthlevel = NinthLevel(self.screen, self.gameStateManager)
        self.finallevel = FinalLevel(self.screen, self.gameStateManager)
        self.ending = Ending(self.screen, self.gameStateManager)
        self.states = {'main-menu': self.mainMenu, 'options': self.options, 'first-level': self.firstLevel, 'eighth-level': self.eighthlevel, 'ninth-level': self.ninthlevel, 'final-level': self.finallevel, 'ending': self.ending}

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
