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

        self.gameStateManager = GameStateManager('fifth-level')
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

class FifthLevel:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager
        self.font = pygame.font.Font(None, 36)
        self.white = WHITE
        self.black = BLACK

        # Number of lives the player has
        self.lives = 3

        background_image_path = os.path.join('graphics','cave-background.png')
        self.background_image = pygame.image.load(background_image_path).convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image, (self.display.get_width(), self.display.get_height()))

        # Questions with multiple choices and the correct answer
        self.qa_dict = {
            "The big brown fox jumps over the lazy dog.": {
                "choices": ["5 (Five)", "6 (Six)", "8 (Eight)", "9 (Nine)"],
                "answer": "9 (Nine)"
            },
            "My house is big and painted blue.": {
                "choices": ["5 (Five)", "6 (Six)", "7 (Seven)", "8 (Eight)"],
                "answer": "7 (Seven)"
            },
            "I love my mom very much.": {
                "choices": ["4 (Four)", "3 (Three)", "10 (Ten)", "6 (Six)"],
                "answer": "6 (Six)"
            },
            "My cat likes to climb.": {
                "choices": ["5 (Five)", "6 (Six)", "7 (Seven)", "8 (Eight)"],
                "answer": "5 (Five)"
            },
            "I like to drink chocolate milk.": {
                "choices": ["4 (Four)", "3 (Three)", "10 (Ten)", "6 (Six)"],
                "answer": "6 (Six)"
            },
            "Mark goes to school every morning.": {
                "choices": ["4 (Four)", "6 (Six)", "10 (Ten)", "8 (Eight)"],
                "answer": "6 (Six)"
            },
            "I fell asleep.": {
                "choices": ["4 (Four)", "3 (Three)", "1 (One)", "9 (Nine)"],
                "answer": "3 (Three)"
            },
            "They ate all the pizza.": {
                "choices": ["5 (Five)", "3 (Three)", "10 (Ten)", "1 (One)"],
                "answer": "5 (Five)"
            },
        }

        self.questions = list(self.qa_dict.keys())  # List of questions
        self.choice_rects = []

        # Shuffle questions when the level starts
        self.shuffle_questions()

        # Use the imported word_colors dictionary
        self.word_colors = word_colors

    def shuffle_questions(self):
        """Shuffles the questions and resets the current question index."""
        random.shuffle(self.questions)
        self.current_question_index = 0  # Reset index after shuffle

    def reset_level(self):
        """Resets the level by shuffling questions and resetting lives."""
        print("Restarting level...")  # Optional debug message
        self.lives = 3  # Reset lives to 3
        self.shuffle_questions()  # Shuffle the questions again

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

        # Load character images (example placeholders)
        char1_image = pygame.image.load(os.path.join('graphics', 'character-avatar.png'))
        char2_image = pygame.image.load(os.path.join('graphics', 'frog-avatar.png'))

        # Resize character images (adjust size as needed)
        char1_image = pygame.transform.scale(char1_image, (200, 200))
        char2_image = pygame.transform.scale(char2_image, (300, 300))

        dialogue_data = [
            {"name": "Unknown Toad", "text": "Good Day, Traveler! May you have safe travels ahead!", "image": char2_image, "audio": "frog-dialogue-1.mp3"},
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
            {"name": "You", "text": "An unknown being named Confusion started to invade our world and has caused us to lose clarity for texts.", "image": char1_image},
            {"name": "You", "text": "I was called to protect Dyscape and restore it to what it was before.", "image": char1_image},
            {"name": "You", "text": "Dyscape is on the brink of full destruction. Confusion is here, and he is planning something evil.", "image": char1_image},
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

        current_line = 0
        text_displayed = ""
        text_index = 0
        text_speed = 2  # Speed of text animation
        audio_played = False  # Track if audio has been played for the current dialogue

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

            # Draw the dialogue box on the screen with the brown border
            self.display.blit(dialogue_box, dialogue_box_rect.topleft)

            # Event handling for advancing the dialogue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
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

    def run(self):
        # Load the paper scroll image
        scroll_image = pygame.image.load(os.path.join('graphics', 'paper-scroll.png'))

        # Resize the scroll image if needed
        scroll_width, scroll_height = 700, 700  # Adjust these values as needed
        scroll_image = pygame.transform.scale(scroll_image, (scroll_width, scroll_height))

        # Center the scroll image
        scroll_x = (self.display.get_width() - scroll_width) // 2
        scroll_y = 10  # Y position for the scroll (adjust as needed)

        # self.run_title_animation()
        # self.run_dialogue_strip()

        running = True
        while running:
            self.display.blit(self.background_image, (0, 0))

            # Display the number of lives
            lives_surface = self.font.render(f"Lives: {self.lives}", True, self.black)
            self.display.blit(lives_surface, (50, 20))

            # Blit the scroll image in the center
            self.display.blit(scroll_image, (scroll_x, scroll_y))

            # Center the question text on the scroll
            main_question = "How many words are in this sentence?"
            question_surface = self.font.render(main_question, True, self.black)

            # Get the rectangle of the question surface to center it
            question_rect = question_surface.get_rect(
                center=(scroll_x + scroll_width // 2, 250))
            self.display.blit(question_surface, question_rect.topleft)

            # Get the current question and choices
            question = self.questions[self.current_question_index]
            choices = self.qa_dict[question]["choices"]

            # Split the question into words
            words = question.split()

            # Calculate total width of all words
            total_words_width = sum([self.font.render(word, True, self.black).get_width() for word in words]) + (
                        10 * (len(words) - 1))

            # Set the initial x_offset to center the words
            x_offset = (self.display.get_width() - total_words_width) // 2
            y_offset = scroll_y + 300  # Y position relative to the scroll

            # Render each word with its assigned color, centered
            for word in words:
                color = self.word_colors.get(word, self.black)
                word_surface = self.font.render(word, True, color)
                self.display.blit(word_surface, (x_offset, y_offset))
                x_offset += word_surface.get_width() + 10  # Add some space between words

            # Render the choices and create rectangles for mouse collision detection
            self.choice_rects = []

            # Calculate total height for choices (if you'd like to center them vertically)
            choices_height = len(choices) * 40  # Assuming each choice has 40px height

            # Calculate the initial y_offset for choices to center them under the question
            y_offset_choices = y_offset + 75  # Adjust as needed for spacing below the question

            for i, choice in enumerate(choices):
                choice_surface = self.font.render(choice, True, self.black)
                choice_width = choice_surface.get_width()

                # Calculate x_offset to center the choices horizontally
                x_offset_choice = (self.display.get_width() - choice_width) // 2
                choice_rect = choice_surface.get_rect(
                    topleft=(x_offset_choice, y_offset_choices + i * 40))  # Adjust vertical spacing (40px per choice)
                self.display.blit(choice_surface, choice_rect.topleft)
                self.choice_rects.append(choice_rect)

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    for i, rect in enumerate(self.choice_rects):
                        if rect.collidepoint(mouse_pos):
                            selected_choice = choices[i]
                            correct_answer = self.qa_dict[question]["answer"]

                            if selected_choice == correct_answer:
                                print("Correct!")
                                self.current_question_index += 1  # Move to next question
                            else:
                                print("Incorrect!")
                                self.lives -= 1  # Lose a life
                                if self.lives <= 0:
                                    self.reset_level()  # Restart level if no lives left
                                    break

                            # If all questions are answered, end the level
                            if self.current_question_index >= len(self.questions):
                                print("All questions answered. Ending level.")
                                running = False
                            break

            pygame.display.update()  # Ensure the display updates with the latest changes
        sys.exit()


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
