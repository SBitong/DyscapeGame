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

        self.gameStateManager = GameStateManager('eighth-level')
        self.mainMenu = MainMenu(self.screen, self.gameStateManager)
        self.options = Options(self.screen, self.gameStateManager)
        self.firstLevel = FirstLevel(self.screen, self.gameStateManager)
        self.eighthlevel = EighthLevel(self.screen, self.gameStateManager)
        self.states = {'main-menu': self.mainMenu, 'options': self.options, 'first-level': self.firstLevel, 'eighth-level': self.eighthlevel}

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


import pygame


class EighthLevel:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager
        self.lives = 3
        self.current_gate = 1
        self.sentence = "Iwenttothestore"  # Example sentence for the first gate
        self.words = ["I", "went", "to", "the", "store"]  # Words to be dragged
        self.word_slots = [None] * len(self.words)  # Empty slots for each word
        self.dragging_word = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.word_positions = [(50, 400), (150, 400), (250, 400), (350, 400), (450, 400)]
        self.slot_positions = [(50, 200), (150, 200), (250, 200), (350, 200), (450, 200)]

    def check_answer(self):
        # Check if all slots are filled correctly
        if self.word_slots == self.words:
            return True
        else:
            self.lives -= 1  # Deduct a life if the order is incorrect
            print(f"Incorrect! Lives remaining: {self.lives}")
            if self.lives <= 0:
                print("Game Over")
                pygame.quit()
                exit()
            return False

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos

            # Check if clicking on a placed word to remove it from the slot
            for i, (slot_word, slot_pos) in enumerate(zip(self.word_slots, self.slot_positions)):
                if slot_word is not None:
                    slot_x, slot_y = slot_pos
                    if slot_x <= mouse_x <= slot_x + 60 and slot_y <= mouse_y <= slot_y + 40:
                        # Remove word from slot and place it back to original area
                        self.word_slots[i] = None
                        self.word_positions[self.words.index(slot_word)] = (50 + 100 * i, 400)
                        return

            # Start dragging if clicking on a word in the draggable area
            for i, word in enumerate(self.words):
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
                        # Place word in slot if slot is empty
                        if self.word_slots[i] is None:
                            self.word_slots[i] = self.words[self.dragging_word]
                            self.word_positions[self.dragging_word] = (-100, -100)  # Temporarily move off screen
                        break
                self.dragging_word = None  # Stop dragging

        elif event.type == pygame.MOUSEMOTION and self.dragging_word is not None:
            mouse_x, mouse_y = event.pos
            # Update word position based on dragging offset
            self.word_positions[self.dragging_word] = (mouse_x - self.drag_offset_x, mouse_y - self.drag_offset_y)

    def draw(self):
        self.display.fill((255, 255, 255))

        # Draw slots for words
        for i, (slot_x, slot_y) in enumerate(self.slot_positions):
            pygame.draw.rect(self.display, (200, 200, 200), (slot_x, slot_y, 60, 40), 2)
            if self.word_slots[i] is not None:
                font = pygame.font.Font(None, 36)
                word_text = font.render(self.word_slots[i], True, (0, 0, 0))
                word_rect = word_text.get_rect(center=(slot_x + 30, slot_y + 20))
                self.display.blit(word_text, word_rect)

        # Draw draggable word boxes
        for i, word in enumerate(self.words):
            if i == self.dragging_word:
                continue  # Skip the word being dragged
            word_x, word_y = self.word_positions[i]
            if word_x >= 0:  # Only draw if not temporarily moved off screen
                pygame.draw.rect(self.display, (173, 216, 230), (word_x, word_y, 60, 40))
                font = pygame.font.Font(None, 36)
                word_text = font.render(word, True, (0, 0, 0))
                word_rect = word_text.get_rect(center=(word_x + 30, word_y + 20))
                self.display.blit(word_text, word_rect)

        # Draw the word box being dragged
        if self.dragging_word is not None:
            word_x, word_y = self.word_positions[self.dragging_word]
            pygame.draw.rect(self.display, (173, 216, 230), (word_x, word_y, 60, 40))
            font = pygame.font.Font(None, 36)
            word_text = font.render(self.words[self.dragging_word], True, (0, 0, 0))
            word_rect = word_text.get_rect(center=(word_x + 30, word_y + 20))
            self.display.blit(word_text, word_rect)

        # Draw lives
        font = pygame.font.Font(None, 36)
        lives_text = font.render(f"Lives: {self.lives}", True, (255, 0, 0))
        self.display.blit(lives_text, (10, 10))

        pygame.display.flip()

    # def run_dialogue_strip(self):
    #     # Initialize pygame's mixer for audio
    #     pygame.mixer.init()
    #
    #     # Load character images (example placeholders)
    #     char1_image = pygame.image.load(os.path.join('graphics', 'character-avatar.png'))
    #     char2_image = pygame.image.load(os.path.join('graphics', 'frog-avatar.png'))
    #
    #     # Resize character images (adjust size as needed)
    #     char1_image = pygame.transform.scale(char1_image, (200, 200))
    #     char2_image = pygame.transform.scale(char2_image, (300, 300))
    #
    #     dialogue_data = [
    #         {"name": "Unknown Toad", "text": "Good Day, Traveler! May you have safe travels ahead of you!",
    #          "image": char2_image, "audio": "frog-dialogue-1.mp3"},
    #         {"name": "You", "text": "Is this the way to the center of Dyscape??", "image": char1_image},
    #         {"name": "Unknown Toad", "text": "...", "image": char2_image},
    #         {"name": "Unknown Toad", "text": "Yes.. but I am afraid that I may not let you pass.", "image": char2_image,
    #          "audio": "frog-dialogue-2.mp3"},
    #         {"name": "You", "text": "WHAT??!?", "image": char1_image},
    #         {"name": "You", "text": "WHY???", "image": char1_image},
    #         {"name": "Unknown Toad",
    #          "text": "I don't know you, mister. And I don't know what business you have inside the tower.",
    #          "image": char2_image, "audio": "frog-dialogue-3.mp3"},
    #         {"name": "You", "text": "(Tower? Could it be...?)", "image": char1_image},
    #         {"name": "Unknown Toad", "text": "It is my job to protect the path to the Tower of Dyslexio and the King.",
    #          "image": char2_image, "audio": "frog-dialogue-4.mp3"},
    #         {"name": "You",
    #          "text": "(THAT'S IT! It is the tower of Dyslexio. So that is the name that the owl was murmuring about..)",
    #          "image": char1_image},
    #         {"name": "You",
    #          "text": "Mister Toad, I respect your values but the world is in danger. Dyscape is in danger.",
    #          "image": char1_image},
    #         {"name": "Unknown Toad", "text": "Danger? What are you talking about?", "image": char2_image,
    #          "audio": "frog-dialogue-5.mp3"},
    #         {"name": "You", "text": "Confusion invaded our world and removed the clarity for texts.",
    #          "image": char1_image},
    #         {"name": "You", "text": "I was called to protect Dyscape and restore it to what it was before.",
    #          "image": char1_image},
    #         {"name": "You", "text": "Dyscape is on slowly dying. Confusion is here, and he is planning something evil.",
    #          "image": char1_image},
    #         {"name": "Unknown Toad", "text": "Hmmm, I see. Well, it can't be helped.", "image": char2_image,
    #          "audio": "frog-dialogue-6.mp3"},
    #         {"name": "Unknown Toad", "text": "Fine, I'll let you pass.", "image": char2_image,
    #          "audio": "frog-dialogue-7.mp3"},
    #         {"name": "You", "text": "YES!!", "image": char1_image},
    #         {"name": "Unknown Toad", "text": "But on one condition, you must answer all my questions.",
    #          "image": char2_image, "audio": "frog-dialogue-8.mp3"},
    #         {"name": "Unknown Toad", "text": "This will assure me that you are not an enemy to us, but a friend.",
    #          "image": char2_image, "audio": "frog-dialogue-9.mp3"},
    #         {"name": "Unknown Toad", "text": "Are you ready, traveler?", "image": char2_image,
    #          "audio": "frog-dialogue-10.mp3"},
    #         {"name": "You", "text": "I am ready, Mr. Toad!", "image": char1_image},
    #     ]
    #
    #     dialogue_box_height = 150  # Height of the dialogue box surface
    #     dialogue_font = pygame.font.Font(None, 32)  # Font for dialogue text
    #     name_font = pygame.font.Font(None, 36)  # Font for character names
    #     space_prompt_font = pygame.font.Font(None, 28)  # Font for "Press SPACE to continue"
    #
    #     current_line = 0
    #     text_displayed = ""
    #     text_index = 0
    #     text_speed = 2  # Speed of text animation
    #     audio_played = False  # Track if audio has been played for the current dialogue
    #
    #     running = True
    #     clock = pygame.time.Clock()
    #
    #     while running:
    #         self.display.blit(self.background_image, (0, 0))
    #
    #         # Create the dialogue box at the bottom
    #         dialogue_box = pygame.Surface((self.display.get_width(), dialogue_box_height))
    #         dialogue_box.fill((255, 219, 172))  # Light background for the dialogue box
    #         dialogue_box_rect = dialogue_box.get_rect(topleft=(0, self.display.get_height() - dialogue_box_height))
    #
    #         # Draw the brown border around the dialogue box
    #         border_color = (139, 69, 19)  # Brown color (RGB)
    #         border_thickness = 20  # Thickness of the border
    #         pygame.draw.rect(self.display, border_color, dialogue_box_rect.inflate(border_thickness, border_thickness),
    #                          border_thickness)
    #
    #         # Get the current dialogue data
    #         current_dialogue = dialogue_data[current_line]
    #         character_name = current_dialogue["name"]
    #         character_text = current_dialogue["text"]
    #         character_image = current_dialogue["image"]
    #         character_audio = current_dialogue.get("audio", None)  # Get audio if available, otherwise None
    #         antagonist = "Unknown Toad"
    #
    #         # Play audio if it's the frog's turn and the audio hasn't been played yet
    #         if character_audio and not audio_played:
    #             pygame.mixer.music.load(os.path.join('audio', character_audio))  # Load the audio file
    #             pygame.mixer.music.play()  # Play the audio
    #             audio_played = True  # Ensure audio only plays once per dialogue line
    #
    #         # Render the character image on the left or right side of the dialogue box
    #         if character_name == antagonist:
    #             self.display.blit(character_image, (950, self.display.get_height() - dialogue_box_height - 300))
    #         else:
    #             self.display.blit(character_image, (50, self.display.get_height() - dialogue_box_height - 200))
    #
    #         # Render the character name inside the dialogue box (above the text)
    #         name_surface = name_font.render(character_name, True, self.black)
    #         dialogue_box.blit(name_surface, (20, 10))  # Draw name near the top inside the dialogue box
    #
    #         # Text animation (add one letter at a time)
    #         if text_index < len(character_text):
    #             text_index += text_speed  # Control how fast letters are added
    #             text_displayed = character_text[:text_index]
    #         else:
    #             text_displayed = character_text
    #
    #         # Render the dialogue text below the name
    #         text_surface = dialogue_font.render(text_displayed, True, self.black)
    #         dialogue_box.blit(text_surface, (20, 60))  # Draw the text inside the dialogue box below the name
    #
    #         # Add "Press SPACE to continue." prompt at the bottom right
    #         if text_index >= len(character_text):  # Show prompt only if the text is fully displayed
    #             space_prompt_surface = space_prompt_font.render("Press SPACE to continue.", True, (100, 100, 100))
    #             dialogue_box.blit(space_prompt_surface,
    #                               (dialogue_box.get_width() - space_prompt_surface.get_width() - 20,
    #                                dialogue_box.get_height() - space_prompt_surface.get_height() - 10))
    #
    #         # Draw the dialogue box on the screen with the brown border
    #         self.display.blit(dialogue_box, dialogue_box_rect.topleft)
    #
    #         # Event handling for advancing the dialogue
    #         for event in pygame.event.get():
    #             if event.type == pygame.QUIT:
    #                 pygame.quit()
    #                 sys.exit()
    #             elif event.type == pygame.KEYDOWN:
    #                 if event.key == pygame.K_SPACE:  # Only proceed on SPACE key
    #                     if text_index >= len(character_text):
    #                         # Move to the next line of dialogue if the text is fully displayed
    #                         current_line += 1
    #                         text_index = 0
    #                         text_displayed = ""
    #                         audio_played = False  # Reset audio flag for the next line
    #                         if current_line >= len(dialogue_data):
    #                             running = False  # Exit dialogue when all lines are done
    #
    #         pygame.display.flip()
    #         clock.tick(60)  # Control the frame rate

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    sys.exit()
                self.handle_events(event)

            # Check if answer is correct
            if all(slot is not None for slot in self.word_slots):  # All slots are filled
                if not self.check_answer():
                    # Optionally, add some delay here before allowing to retry
                    print("Retrying...")
                    self.word_slots = [None] * len(self.words)  # Reset slots for retry
                    self.word_positions = [(50, 400), (150, 400), (250, 400), (350, 400), (450, 400)]

            self.draw()


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
