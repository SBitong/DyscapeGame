import pygame
import sys
import os
import random
import time
import pyttsx3
import pronouncing
import database
import settings
import sqlite3
import datetime
import re
from settings import *

# Initialize Pygame
pygame.init()
engine = pyttsx3.init()
rate = 150
engine.setProperty('rate', rate)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("DyscapeTheGame")

        # Initialize Database first, with gameStateManager temporarily set to None
        self.database = Database(self.screen, None)

        # Now initialize GameStateManager with the database
        self.gameStateManager = GameStateManager('main-menu', self.database)

        # Update the database's reference to gameStateManager
        self.database.gameStateManager = self.gameStateManager

        # Initialize other components with the gameStateManager
        self.mainMenu = MainMenu(self.screen, self.gameStateManager)
        self.options = Options(self.screen, self.gameStateManager)
        self.firstLevel = TheBrokenBridge(self.screen, self.gameStateManager, game_id=1)

        # Define the states with the initialized objects
        self.states = {
            'main-menu': self.mainMenu,
            'database': self.database,
            'options': self.options,
            # 'first-level': self.firstLevel,
            # Add other levels if needed
        }

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


def show_new_game_popup(database, gameStateManager, display):
    running = True
    input_box = pygame.Rect(display.get_width() // 2 - 100, 300, 200, 50)
    user_text = ""
    font = pygame.font.Font(None, 36)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    user_text = user_text.strip()  # Ensure no leading/trailing whitespace
                    if user_text:  # If the user entered a name
                        # Save to games table
                        game_id = database.create_and_start_new_game(user_text)
                        if game_id:
                            print(f"New game created with ID {game_id}")
                            # Go directly to TheBrokenBridge level
                            gameStateManager.set_state(TheBrokenBridge(display, gameStateManager, game_id))
                            running = False  # Exit the loop
                            return
                        else:
                            print("Game name already exists. Choose a different name.")
                elif event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                else:
                    user_text += event.unicode

        display.fill((0, 0, 0))  # Clear screen or use background image
        pygame.draw.rect(display, (255, 200, 0), input_box, border_radius=10)
        text_surface = font.render(user_text, True, (0, 0, 0))
        display.blit(text_surface, (input_box.x + 5, input_box.y + 10))
        prompt = font.render("Name your saved Game:", True, (255, 255, 255))
        display.blit(prompt, (input_box.x, input_box.y - 40))

        pygame.display.flip()  # Update the display



class GameStart:
    def __init__(self, database, gameStateManager, display, loadGamePage):
        self.database = database
        self.gameStateManager = gameStateManager
        self.display = display
        self.loadGamePage = loadGamePage  # Reference to the load game page for updating

    def start_new_game(self, game_name):
        # Create a new game in the games table
        game_id = self.database.create_and_start_new_game(game_name)
        if game_id is not None:
            print(f"Starting new game with Game ID {game_id} at TheBrokenBridge.")
            # Pass game_id as the identifier here
            self.gameStateManager.set_state(TheBrokenBridge(self.display, self.gameStateManager, game_id))
            # Save initial progress with the game_id
            self.database.save_progress(game_id, 'first-level', lives=3, draggable_images=[], ladder_slots=[])
            # Update load game page to reflect new game
            self.loadGamePage.refresh_profiles()  # Use this method to refresh the list
        else:
            print("Game name already exists. Choose a different name.")



class Database:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager

        # Initialize SQLite database
        self.conn = sqlite3.connect('game_data.db')
        self.cursor = self.conn.cursor()
        self.create_table()
        self.create_tables()

        # Load the background image for the database page
        background_image_path = os.path.join('graphics', 'main-menu-background-1.jpg')
        self.background_image = pygame.image.load(background_image_path).convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image, (self.display.get_width(), self.display.get_height()))

        # Font for text display
        font_path = os.path.join('fonts', 'ARIAL.TTF')
        self.font = pygame.font.Font(font_path, 30)

        # "New Game" button properties
        self.new_game_button = pygame.Rect((self.display.get_width() // 2 - 100, 50), (200, 50))
        self.button_color = (255, 200, 0)

        # Dictionary to store delete buttons and continue buttons for each saved game
        self.delete_buttons = {}
        self.continue_buttons = {}

    def create_table(self):
        # Create the games table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY,
                name TEXT,
                creation_date TEXT,
                last_played_date TEXT, -- Ensure this column is created
                current_level TEXT
            )
        ''')
        self.conn.commit()
        # Ensure last_played_date column exists
        self.add_column_if_not_exists("last_played_date", "TEXT")

    def create_tables(self):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS games (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT UNIQUE,
                                creation_date TEXT,
                                last_played_date TEXT,
                                current_level TEXT
                              )''')

            self.conn.commit()

    def create_and_start_new_game(self, name, level="The Broken Bridge"):
        with self.conn:
            cursor = self.conn.cursor()
            # Check if the game name already exists in the games table
            cursor.execute('SELECT id FROM games WHERE name = ?', (name,))
            existing_game = cursor.fetchone()
            if existing_game:
                print("Game name already exists.")
                return None

            # Insert a new record into the games table with initial values
            creation_date = datetime.datetime.now().strftime('%Y-%m-%d')
            cursor.execute('INSERT INTO games (name, creation_date, last_played, current_level) VALUES (?, ?, ?, ?)',
                           (name, creation_date, creation_date, level))
            self.conn.commit()
            print("New game created with ID:", cursor.lastrowid)  # Debug statement
            return cursor.lastrowid  # Return the ID of the newly created game

    def get_profiles(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name FROM profiles")
        profiles = cursor.fetchall()
        return [{'id': profile[0], 'name': profile[1]} for profile in profiles]

    def save_game(self, name, level="first-level"):
        creation_date = datetime.datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute('''
            INSERT INTO games (name, creation_date, last_played_date, current_level)
            VALUES (?, ?, ?, ?)
        ''', (name, creation_date, creation_date, level))
        self.conn.commit()
        print("Game saved with name:", name)

    def delete_game(self, game_id):
        self.cursor.execute('DELETE FROM games WHERE id = ?', (game_id,))
        self.conn.commit()

    def get_saved_games(self):
        self.cursor.execute('SELECT * FROM games')
        saved_games = self.cursor.fetchall()
        return saved_games

    def update_last_played(self, game_id, next_level):
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute('''
            UPDATE games
            SET last_played_date = ?, current_level = ?
            WHERE id = ?
        ''', (current_date, next_level, game_id))
        self.conn.commit()
        print(f"Updated game ID {game_id} to level {next_level}")

    def update_progress_in_database(self, game_id, new_level):
        with self.conn:
            self.cursor.execute('''
                UPDATE games
                SET current_level = ?, last_played_date = ?
                WHERE id = ?
            ''', (new_level, datetime.datetime.now().strftime('%Y-%m-%d'), game_id))
            self.conn.commit()

    def display_page(self):
        # Draw the background image
        if self.background_image:
            self.display.blit(self.background_image, (0, 0))
        else:
            print("Background image not loaded")

        # Draw the "New Game" button
        pygame.draw.rect(self.display, self.button_color, self.new_game_button, border_radius=10)
        new_game_text = self.font.render("New Game", True, (0, 0, 0))
        new_game_text_rect = new_game_text.get_rect(center=self.new_game_button.center)
        self.display.blit(new_game_text, new_game_text_rect)

        # Clear previous buttons and initialize new ones for each saved game
        self.delete_buttons = {}
        self.continue_buttons = {}

        saved_games = self.get_saved_games()

        if not saved_games:
            print("No saved games found.")

        y_offset = 150

        # Draw rectangles and buttons for each saved game entry
        for game in saved_games:
            # Create a container rectangle for each saved game
            game_rect = pygame.Rect(50, y_offset, self.display.get_width() - 100, 60)
            pygame.draw.rect(self.display, (200, 200, 200), game_rect, border_radius=10)

            # Display game details within the rectangle
            game_text = f"{game[1]} - Last Played: {game[3]} - Current Level: {game[4]}"
            game_text_surface = self.font.render(game_text, True, (0, 0, 0))
            game_text_rect = game_text_surface.get_rect(midleft=(game_rect.x + 20, game_rect.centery))
            self.display.blit(game_text_surface, game_text_rect)

            # Create and display the "Continue" button
            continue_button = pygame.Rect((game_rect.right - 270, y_offset + 10), (130, 40))
            pygame.draw.rect(self.display, (0, 128, 0), continue_button, border_radius=5)
            continue_text = self.font.render("Continue", True, (255, 255, 255))
            continue_text_rect = continue_text.get_rect(center=continue_button.center)
            self.display.blit(continue_text, continue_text_rect)
            self.continue_buttons[game[0]] = continue_button

            # Create and display the "Delete" button
            delete_button = pygame.Rect((game_rect.right - 130, y_offset + 10), (100, 40))
            pygame.draw.rect(self.display, (255, 0, 0), delete_button, border_radius=5)
            delete_text = self.font.render("Delete", True, (255, 255, 255))
            delete_text_rect = delete_text.get_rect(center=delete_button.center)
            self.display.blit(delete_text, delete_text_rect)
            self.delete_buttons[game[0]] = delete_button

            # Move to the next y position for the next saved game entry
            y_offset += 80


        # Update the display
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.new_game_button.collidepoint(event.pos):
                    show_new_game_popup(self, self.gameStateManager, self.display)

                for game_id, delete_button in self.delete_buttons.items():
                    if delete_button.collidepoint(event.pos):
                        self.delete_game(game_id)
                        print(f"Game with ID {game_id} deleted.")
                        return

                for game_id, continue_button in self.continue_buttons.items():
                    if continue_button.collidepoint(event.pos):
                        self.continue_game(game_id)
                        return

                clicked_game = self.get_clicked_game(event.pos)
                if clicked_game:
                    game_id, name, creation_date, last_played_date, current_level = clicked_game
                    max_unlocked_level = int(current_level.split('-')[1])

                    level_selection_page = LevelSelectionPage(
                        self.display,
                        self.gameStateManager,
                        'graphics/main-menu-background-1.jpg',
                        'graphics/back_button.png',
                        {i: pygame.image.load(f'graphics/N{i}.png') for i in range(1, 8)},
                        'graphics/lock.png'
                    )
                    level_selection_page.run(max_unlocked_level)

    def get_clicked_game(self, mouse_pos):
        y_offset = 150
        saved_games = self.get_saved_games()

        for game in saved_games:
            game_rect = pygame.Rect(50, y_offset, self.display.get_width() - 100, 60)
            if game_rect.collidepoint(mouse_pos):
                return game
            y_offset += 80
        return None

    def load_saved_game(self, game_id):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('SELECT current_level FROM games WHERE id = ?', (game_id,))
            result = cursor.fetchone()
            if result:
                return {'current_level': result[0]}
        return None

    def add_column_if_not_exists(self, column_name, column_type):
        # Check if the column exists
        self.cursor.execute(f"PRAGMA table_info(games)")
        columns = [col[1] for col in self.cursor.fetchall()]
        if column_name not in columns:
            # Add the column if it doesn’t exist
            self.cursor.execute(f"ALTER TABLE games ADD COLUMN {column_name} {column_type}")
            self.conn.commit()
            print(f"Added missing column: {column_name}")

    def continue_game(self, game_id):
        # Retrieve the saved games list
        saved_games = self.get_saved_games()

        # Find the game data with the matching game_id
        game_data = next((game for game in saved_games if game[0] == game_id), None)

        if game_data:
            current_level_str = game_data[4]
            level_mapping = {'first-level': 1, 'second-level': 2}
            max_unlocked_level = level_mapping.get(current_level_str, 1)
            level_selection_page = LevelSelectionPage(self.display, self.gameStateManager, game_id, max_unlocked_level)
            level_selection_page.run()
        else:
            print(f"Error: No saved game found for game ID {game_id}")

    def run(self):
        running = True
        while running:
            self.display_page()  # Display the database page
            self.handle_events()  # Handle interactions like starting or deleting games
            pygame.display.flip()  # Update the screen

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:  # Optionally allow quitting with the escape key
                        running = False
    def __del__(self):
        self.conn.close()


def level_class(display, gameStateManager, game_id):
    pass


class LoadGamePage:
    def __init__(self, display, database, gameStateManager, game_id):
        self.game_id = game_id
        self.display = display
        self.database = database
        self.gameStateManager = gameStateManager
        self.profiles = self.database.get_profiles()  # Fetch profiles from the database

        # Define layout and button properties
        self.rect_color = (200, 200, 200)
        self.text_color = (0, 0, 0)
        self.button_color = (255, 204, 102)
        self.rect_width, self.rect_height = 300, 80
        self.padding = 10
        self.start_x, self.start_y = 100, 150

    def refresh_profiles(self):
        """Refresh the list of profiles from the database."""
        self.profiles = self.database.get_profiles()

    def display_page(self):
        self.display.fill((255, 255, 204))  # Background color for the load game page

        # Draw each profile in a rectangle
        for index, profile in enumerate(self.profiles):
            y_position = self.start_y + index * (self.rect_height + self.padding)
            rect = pygame.Rect(self.start_x, y_position, self.rect_width, self.rect_height)
            pygame.draw.rect(self.display, self.rect_color, rect)

            # Display profile information
            font = pygame.font.Font(None, 24)
            name_text = font.render(profile['name'], True, self.text_color)
            date_text = font.render(f"Date Created: {profile['date_created']}", True, self.text_color)
            level_text = font.render(f"Recent Level: {profile['recent_level']}", True, self.text_color)

            # Position text within the rectangle
            self.display.blit(name_text, (self.start_x + 10, y_position + 10))
            self.display.blit(date_text, (self.start_x + 10, y_position + 30))
            self.display.blit(level_text, (self.start_x + 10, y_position + 50))

            # Continue button
            continue_button = pygame.Rect(self.start_x + 220, y_position + 10, 70, 25)
            pygame.draw.rect(self.display, self.button_color, continue_button)
            continue_text = font.render("Continue", True, self.text_color)
            self.display.blit(continue_text, (continue_button.x + 5, continue_button.y + 5))

            # Delete button
            delete_button = pygame.Rect(self.start_x + 220, y_position + 40, 70, 25)
            pygame.draw.rect(self.display, (255, 100, 100), delete_button)
            delete_text = font.render("Delete", True, self.text_color)
            self.display.blit(delete_text, (delete_button.x + 5, delete_button.y + 5))

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for index, profile in enumerate(self.profiles):
                    y_position = self.start_y + index * (self.rect_height + self.padding)

                    # Define rects for continue and delete buttons
                    continue_button = pygame.Rect(self.start_x + 220, y_position + 10, 70, 25)
                    delete_button = pygame.Rect(self.start_x + 220, y_position + 40, 70, 25)

                    if continue_button.collidepoint(event.pos):
                        # Load the game at the last saved level
                        last_level_class = self.gameStateManager.get_level_class(profile['recent_level'])
                        self.gameStateManager.set_state(level_class(self.display, self.gameStateManager, self.game_id))
                    elif delete_button.collidepoint(event.pos):
                        # Delete profile and refresh list
                        self.database.delete_profile(profile['id'])
                        self.refresh_profiles()

    def run(self):
        running = True
        while running:
            self.display_page()
            self.handle_events()
            pygame.display.update()


class LevelSelectionPage:
    def __init__(self, display, gameStateManager, game_id, max_unlocked_level):
        self.display = display
        self.gameStateManager = gameStateManager
        self.game_id = game_id
        self.tile_size = 100  # Size of each level tile
        self.max_unlocked_level = max_unlocked_level

        # Load background and images
        self.background_image = pygame.image.load('graphics/main-menu-background-1.jpg').convert()
        self.background_image = pygame.transform.scale(self.background_image,
                                                       (self.display.get_width(), self.display.get_height()))
        self.default_image = pygame.Surface((self.tile_size, self.tile_size))
        self.default_image.fill((100, 100, 100))
        self.level_images = {i: self.load_image(f'graphics/N{i}.png') for i in range(1, 9)}

        lock_image_raw = pygame.image.load('graphics/lock.png').convert_alpha()
        self.lock_image = pygame.transform.scale(lock_image_raw, (self.tile_size, self.tile_size))

        # Position levels in a 4x2 grid with centered alignment
        self.level_positions = [
            (self.display.get_width() // 2 - 280 + (i % 4) * 160, 200 + (i // 4) * 180)
            for i in range(8)
        ]

        # Back button setup
        self.back_button_image = pygame.image.load('graphics/back.png').convert_alpha()
        self.back_button = pygame.transform.scale(self.back_button_image, (180, 180))
        self.back_button_rect = self.back_button.get_rect(topleft=(50, 5))  # Top-left corner

    def load_image(self, path):
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, (self.tile_size, self.tile_size))
        except FileNotFoundError:
            return self.default_image

    def display_page(self):
        # Display background and back button
        self.display.blit(self.background_image, (0, 0))
        self.display.blit(self.back_button, self.back_button_rect)

        # Fetch and print the most recent max unlocked level for debugging
        self.max_unlocked_level = self.get_max_unlocked_level()

        # Draw level tiles (locked/unlocked) with debugging for each tile's status
        for i in range(1, 9):
            x, y = self.level_positions[i - 1]
            image = self.level_images[i] if i <= self.max_unlocked_level else self.lock_image
            self.display.blit(image, (x, y))

        pygame.display.flip()

    def get_max_unlocked_level(self):
        """Fetch the highest unlocked level from the database."""
        with sqlite3.connect('game_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT current_level FROM games WHERE id = ?', (self.game_id,))
            result = cursor.fetchone()
            if result:
                level_mapping = {"first-level": 1, "TheRhymeanGarden": 2,
                                 "third-level": 3}  # Ensure "third-level" exists
                return level_mapping.get(result[0], 1)
        return 1

    def handle_events(self):
        level_classes = {1: TheBrokenBridge, 2: TheRhymeanGarden, 3: ThirdLevel}
  # Extend with other levels as needed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if back button is clicked
                if self.back_button_rect.collidepoint(event.pos):
                    # Go back to the Database page
                    self.gameStateManager.set_state(Database(self.display, self.gameStateManager))
                    return

                # Check if any level tile is clicked
                for i in range(1, self.max_unlocked_level + 1):
                    x, y = self.level_positions[i - 1]
                    if pygame.Rect(x, y, self.tile_size, self.tile_size).collidepoint(event.pos):
                        level_class = level_classes.get(i, TheBrokenBridge)
                        # Ensure game_id is passed here
                        self.gameStateManager.set_state(level_class(self.display, self.gameStateManager, self.game_id))
                        return

    def run(self):
        while True:
            self.display_page()
            self.handle_events()
            pygame.display.update()



class MainMenu:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager
        self.database = database  # Store the database instance

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
                        self.gameStateManager.set_state('database')
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

class TheBrokenBridge:
        def __init__(self, display, gameStateManager, game_id):
            self.display = display
            self.gameStateManager = gameStateManager
            self.game_id = game_id
            self.database = Database(display, gameStateManager)
            self.win = False
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
            self.restart_button = pygame.Rect(self.display.get_width() // 2 - (250 // 2),
                                              self.display.get_height() // 2, 250, 50)
            self.exit_button = pygame.Rect(self.display.get_width() // 2 - (250 // 2),
                                           self.display.get_height() // 2 + 70, 250, 50)

            if self.win:
                self.update_progress_in_database("The Rhymean Garden")
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

            pygame.display.flip()  # Update the screen to show buttons

            # Handle events for the end screen
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if self.win and self.next_level_button.collidepoint(event.pos):
                            # Go to the next level
                            self.gameStateManager.set_state(
                                TheRhymeanGarden(self.display, self.gameStateManager, self.game_id))
                            return  # Exit the end screen function to transition to the next level
                        elif self.restart_button.collidepoint(event.pos):
                            # Restart the level
                            self.restart_level()
                            return
                        elif self.exit_button.collidepoint(event.pos):
                            # Return to main menu
                            self.exit_to_main_menu()
                            return

        def restart_level(self):
            # Reinitialize the level to reset all variables and the game state
            self.__init__(self.display, self.gameStateManager)
            self.gameStateManager.set_state('first-level')  # Set the game state back to 'first-level'

        def exit_to_main_menu(self):
            # Change the game state to 'main-menu'
            self.reset_level()
            self.gameStateManager.set_state('main-menu')

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

        def run_title_animation(self):
            title_heading = "Fifth Level:"
            title_text = "THE BROKEN BRIDGE"
            font_path = os.path.join('fonts', 'ARIALBLACKITALIC.TTF')
            title_font = pygame.font.Font(font_path, 50)  # Large font for the title

            alpha = 0  # Start fully transparent
            max_alpha = 255
            fade_speed = 5  # How fast the title fades in and out

            running = True
            while running:
                self.display.fill((0, 0, 0))

                # Render the title with fading effect
                title_surface = title_font.render(title_text, True, (255, 255, 255))
                title_surface.set_alpha(alpha)  # Set transparency level
                title_rect = title_surface.get_rect(
                    center=(self.display.get_width() // 2, self.display.get_height() // 2))
                self.display.blit(title_surface, title_rect)

                # Update the alpha to create fade-in effect
                alpha += fade_speed
                if alpha >= max_alpha:
                    alpha = max_alpha
                    pygame.time.delay(500)  # Pause for a short moment at full opacity

                    # Fade out effect
                    while alpha > 0:
                        self.display.fill((0, 0, 0))
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

        def update_progress_in_database(self, completed_level):
            """Update the database to unlock the next level."""
            level_mapping = {
                "first-level": "TheRhymeanGarden",  # Example mapping to next level
                "TheRhymeanGarden": "third-level"  # Adjust as necessary for next level
            }
            next_level = level_mapping.get(completed_level, completed_level)
            self.database.update_last_played(self.game_id, next_level)

        def run(self):
            """Main game loop for the first level."""

            correct_answer_sound = pygame.mixer.Sound(os.path.join('audio', 'correct-answer.mp3'))
            wrong_answer_sound = pygame.mixer.Sound(os.path.join('audio', 'wrong-answer.mp3'))

            speaker_icon = pygame.image.load(os.path.join('graphics', 'audio-logo.png')).convert_alpha()
            speaker_icon = pygame.transform.scale(speaker_icon, (30, 30))  # Resize the speaker icon to fit on the ladder

            # Only run the dialogue strip the first time the level is played
            if not self.dialogue_played:
                # self.run_dialogue_strip_1()
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

class TheRhymeanGarden:
    def __init__(self, display, gameStateManager, game_id):
        self.display = display
        self.gameStateManager = gameStateManager
        self.database = Database(display, gameStateManager)
        self.game_id = game_id
        self.win = False
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
        # Fill the screen with a black overlay
        self.display.fill((0, 0, 0))

        # Display win or game over message
        message = "You Win!" if self.rounds_completed >= self.max_rounds else "Game Over!"
        text_surface = self.font.render(message, True, (255, 255, 255))
        self.display.blit(text_surface,
                          (self.screen_width // 2 - text_surface.get_width() // 2, self.screen_height // 3))

        # Define buttons
        self.restart_button = pygame.Rect(self.screen_width // 2 - 100, self.screen_height // 2, 200, 50)
        self.exit_button = pygame.Rect(self.screen_width // 2 - 100, self.screen_height // 2 + 70, 200, 50)

        # If the player wins, add the "Next Level" button
        if self.rounds_completed >= self.max_rounds:
            self.next_level_button = pygame.Rect(self.screen_width // 2 - 100, self.screen_height // 2 - 70, 200, 50)

            # Draw the Next Level button
            pygame.draw.rect(self.display, (0, 0, 255), self.next_level_button)
            next_level_text = self.font.render("Next Level", True, (255, 255, 255))
            self.display.blit(next_level_text, (self.next_level_button.x + 50, self.next_level_button.y + 10))

            # Update progress in the database to unlock the next level
            self.update_progress_in_database("third-level")  # Replace "third-level" with the actual next level name

        # Draw the Restart button
        pygame.draw.rect(self.display, (0, 128, 0), self.restart_button)
        restart_text = self.font.render("Restart", True, (255, 255, 255))
        self.display.blit(restart_text, (self.restart_button.x + 50, self.restart_button.y + 10))

        # Draw the Exit button
        pygame.draw.rect(self.display, (128, 0, 0), self.exit_button)
        exit_text = self.font.render("Exit", True, (255, 255, 255))
        self.display.blit(exit_text, (self.exit_button.x + 70, self.exit_button.y + 10))

        pygame.display.flip()  # Update the screen to show buttons

    def update_progress_in_database(self, next_level):
        """Updates the game's progress in the database to unlock the next level."""
        self.database.update_last_played(self.game_id, next_level)

    def run(self):
        self.run_title_animation()
        self.current_time = self.time_limit
        self.last_time = pygame.time.get_ticks()  # Initialize last_time here
        running = True
        self.game_over = False
        self.win = False  # Track if the player has won

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
                                if self.rounds_completed >= self.max_rounds:  # Check if player completed all rounds
                                    self.win = True
                                    self.game_over = True
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
                    # Handle clicks on the restart, exit, or next level buttons after the game is over
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
                            self.win = False  # Reset win status
                        elif self.exit_button.collidepoint(event.pos):
                            self.gameStateManager.set_state('main-menu')
                            running = False
                        elif self.win and self.next_level_button.collidepoint(event.pos):
                            # Unlock the next level by updating the database
                            self.update_progress_in_database('third-level')
                            self.gameStateManager.set_state('third-level')
                            running = False

            # Update the warrior animation frame
            self.warrior_frame_time += self.clock.get_time() / 1000.0  # Increment frame time
            if self.warrior_frame_time >= self.warrior_animation_speed:  # Check if it's time to update the frame
                self.warrior_current_frame = (self.warrior_current_frame + 1) % len(
                    self.warrior_frames)  # Move to the next frame
                self.warrior_frame_time = 0  # Reset frame time

            if not self.game_over:
                if self.timer_started:  # Check if the timer has started
                    self.time_passed = pygame.time.get_ticks() - self.last_time
                    self.current_time -= self.time_passed / 1000.0
                    self.last_time = pygame.time.get_ticks()
                    if self.current_time <= 0:
                        self.lives -= 1
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
    def __init__(self, display, gameStateManager, game_id):
        self.display = display
        self.gameStateManager = gameStateManager
        self.game_id = game_id
        self.screen_width, self.screen_height = self.display.get_size()

        # Set up the font for displaying text
        font_path = 'fonts/ARIAL.TTF'  # Adjust if you have a different path or font
        self.font = pygame.font.Font(font_path, 30)

        # Background color
        self.background_color = (50, 150, 50)

    def display_message(self, text):
        """Display a message in the center of the screen."""
        self.display.fill(self.background_color)
        text_surface = self.font.render(text, True, (255, 255, 255))
        self.display.blit(text_surface, (
            self.screen_width // 2 - text_surface.get_width() // 2,
            self.screen_height // 2 - text_surface.get_height() // 2
        ))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.gameStateManager.set_state('main-menu')
                        running = False

            # Display the placeholder level message
            self.display_message("Welcome to Third Level! Press ESC to return to Main Menu.")

            # Update the display
            pygame.display.flip()
            pygame.time.delay(100)  # Limit the frame rate for a simple loop







class GameStateManager:
    def __init__(self, currentState, database):
        self.currentState = currentState
        self.database = database  # Store reference to the database

    def get_state(self):
        return self.currentState

    def set_state(self, state):
        print(f"Switching to state: {state}")  # Debugging line
        if isinstance(state, str):
            self.currentState = state
        else:
            # Handle direct class instances as game state (like TheBrokenBridge instance)
            self.currentState = state
            self.currentState.run()  # Run the level directly if a class instance is passed


if __name__ == "__main__":
    game = Game()
    game.run()
