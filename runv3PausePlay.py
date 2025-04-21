#!/usr/bin/env python3
import pygame, sys, random
from ai_dqn import DeepQAgent  # Import the Deep Q-learning agent

# Initialize pygame and set up the window.
pygame.init()
BOARD_WIDTH, BOARD_HEIGHT = 550, 550
INFO_WIDTH = 150
INFO_MARGIN = 10
DEFAULT_WIDTH = BOARD_WIDTH + INFO_WIDTH + 2 * INFO_MARGIN  # 720
DEFAULT_HEIGHT = BOARD_HEIGHT + 2 * INFO_MARGIN              # 570
screen = pygame.display.set_mode((DEFAULT_WIDTH, DEFAULT_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Morabararaba with Deep Q-Learning AI")

# Define colors and font.
WHITE = (245, 222, 179)  # Light brown background
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 200, 0)
font = pygame.font.SysFont(None, 24)

# Define a custom event for auto-restarting the game.
AUTO_RESTART_EVENT = pygame.USEREVENT + 1

# Global layout variables.
board_offset_x = 0
board_offset_y = 0
info_x = 0
restart_button_rect = None
exit_button_rect = None

# Win counters for each player.
win_counts = {'X': 0, 'O': 0}

def update_layout():
    global board_offset_x, board_offset_y, info_x
    current_width, current_height = screen.get_size()
    total_width = BOARD_WIDTH + INFO_WIDTH + INFO_MARGIN
    board_offset_x = max((current_width - total_width) // 2, 0)
    board_offset_y = max((current_height - BOARD_HEIGHT) // 2, 0)
    info_x = board_offset_x + BOARD_WIDTH + INFO_MARGIN

# Board positions, mills, connections, and adjacent spots.
positions = {
    "a1": (39, 511), "a4": (39, 275), "a7": (39, 39),
    "b2": (118, 432), "b4": (118, 275), "b6": (118, 118),
    "c3": (196, 353), "c4": (196, 275), "c5": (196, 196),
    "d1": (275, 511), "d2": (275, 432), "d3": (275, 353),
          "d5": (275, 196), "d6": (275, 118), "d7": (275, 39),
    "e3": (353, 353), "e4": (353, 275), "e5": (353, 196),
    "f2": (432, 432), "f4": (432, 275), "f6": (432, 118),
    "g1": (511, 511), "g4": (511, 275), "g7": (511, 39)
}

mills = [
    ["a1", "a4", "a7"],
    ["b2", "b4", "b6"],
    ["c3", "c4", "c5"],
    ["d1", "d2", "d3"],
    ["d5", "d6", "d7"],
    ["e3", "e4", "e5"],
    ["f2", "f4", "f6"],
    ["g1", "g4", "g7"],
    ["a1", "d1", "g1"],
    ["a4", "b4", "c4"],
    ["a7", "d7", "g7"],
    ["b2", "d2", "f2"],
    ["b6", "d6", "f6"],
    ["c3", "d3", "e3"],
    ["c5", "d5", "e5"],
    ["e4", "f4", "g4"]
]

connections = [
    ("a1", "a4"), ("a4", "a7"), ("a1", "d1"), ("a7", "d7"),
    ("b2", "b4"), ("b4", "b6"), ("b2", "d2"), ("b6", "d6"),
    ("c3", "c4"), ("c4", "c5"), ("c3", "d3"), ("c5", "d5"),
    ("d1", "d2"), ("d2", "d3"),
    ("d5", "d6"), ("d6", "d7"),
    ("e3", "e4"), ("e4", "e5"), ("e3", "d3"), ("e5", "d5"),
    ("f2", "f4"), ("f4", "f6"), ("f2", "d2"), ("f6", "d6"),
    ("g1", "g4"), ("g4", "g7"), ("g1", "d1"), ("g7", "d7"),
    ("a4", "b4"), ("b4", "c4"),
    ("e4", "f4"), ("f4", "g4"),
    ("b2", "c3"), ("c3", "e3"), ("e3", "f2"),
    ("b6", "c5"), ("c5", "e5"), ("e5", "f6"),
    ("a7", "b6"), ("g7", "f6"), ("a1", "b2"), ("g1", "f2")
]

adjacent = {
    "a1": ["a4", "d1", "b2"],
    "a4": ["a1", "a7", "b4"],
    "a7": ["a4", "d7", "b6"],
    "b2": ["b4", "d2", "c3", "a1"],
    "b4": ["b2", "b6", "a4", "c4"],
    "b6": ["b4", "d6", "c5", "a7"],
    "c3": ["c4", "b2", "d3"],
    "c4": ["c3", "c5", "b4"],
    "c5": ["c4", "b6", "d5"],
    "d1": ["a1", "d2", "g1"],
    "d2": ["d1", "d3", "b2", "f2"],
    "d3": ["d2", "c3", "e3"],
    "d5": ["d6", "c5", "e5"],
    "d6": ["d5", "d7", "b6", "f6"],
    "d7": ["d6", "a7", "g7"],
    "e3": ["e4", "d3", "f2"],
    "e4": ["e3", "e5", "f4"],
    "e5": ["e4", "d5", "f6"],
    "f2": ["f4", "d2", "e3", "g1"],
    "f4": ["f2", "f6", "e4", "g4"],
    "f6": ["f4", "d6", "e5", "g7"],
    "g1": ["g4", "d1", "f2"],
    "g4": ["g1", "g7", "f4"],
    "g7": ["g4", "d7", "f6"]
}

# Game state variables.
board_state = {key: None for key in positions}
current_player = random.choice(['X', 'O'])
pieces_placed = {'X': 0, 'O': 0}
TOTAL_PIECES = 12
removed_count = {'X': 0, 'O': 0}
phase = "placing"   # "placing", "moving", or "removal"
removal_mode = False
selected_piece = None
selected_from = None
info_message = ""
game_over = False
paused = False


def draw_info():
    global restart_button_rect, exit_button_rect
    turn_text = f"Turn: Player {current_player} ({'Red' if current_player=='X' else 'Blue'})"
    turn_render = font.render(turn_text, True, BLACK)
    screen.blit(turn_render, (info_x, board_offset_y))
    
    red_active = count_pieces('X')
    blue_active = count_pieces('O')
    count_text = f"Active: Red {red_active} Blue {blue_active}"
    count_render = font.render(count_text, True, BLACK)
    screen.blit(count_render, (info_x, board_offset_y + 30))
    
    removed_text = f"Removed: Red {removed_count['X']} Blue {removed_count['O']}"
    removed_render = font.render(removed_text, True, BLACK)
    screen.blit(removed_render, (info_x, board_offset_y + 60))
    
    wins_text = f"Wins: Red {win_counts['X']} Blue {win_counts['O']}"
    wins_render = font.render(wins_text, True, BLACK)
    screen.blit(wins_render, (info_x, board_offset_y + 90))
    
    message_render = font.render(info_message, True, BLACK)
    screen.blit(message_render, (info_x, board_offset_y + 120))
    
    if game_over:
        if paused:
            pause_render = font.render("Paused - Press Space to Resume", True, RED)
            screen.blit(pause_render, (info_x, board_offset_y + 180))

            over_text = "Game Over!"
            over_render = font.render(over_text, True, BLACK)
            screen.blit(over_render, (info_x, board_offset_y + 150))
            restart_button_rect = pygame.Rect(info_x, board_offset_y + 190, 100, 40)
            pygame.draw.rect(screen, GREEN, restart_button_rect)
            restart_text = font.render("Restart", True, BLACK)
            screen.blit(restart_text, (info_x + 10, board_offset_y + 200))
            exit_button_rect = pygame.Rect(info_x, board_offset_y + 240, 100, 40)
            pygame.draw.rect(screen, RED, exit_button_rect)
            exit_text = font.render("Exit", True, BLACK)
            screen.blit(exit_text, (info_x + 25, board_offset_y + 250))



def draw_heatmap(agent):
    q_values = agent.get_q_values(board_state, positions)
    pos_list = sorted(positions.keys())
    max_q = max(q_values)
    min_q = min(q_values)

    for i, pos in enumerate(pos_list):
        if board_state[pos] is not None:
            continue
        norm = (q_values[i] - min_q) / (max_q - min_q + 1e-6)
        intensity = int(255 * norm)
        heat_color = (0, 255, 0, intensity)  # green with alpha

        surface = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(surface, heat_color, (10, 10), 10)
        coord = positions[pos]
        screen.blit(surface, (coord[0] + board_offset_x - 10, coord[1] + board_offset_y - 10))

        prob_text = font.render(f"{norm:.2f}", True, BLACK)
        screen.blit(prob_text, (coord[0] + board_offset_x + 10, coord[1] + board_offset_y - 10))
    pos_list = sorted(positions.keys())
    max_q = max(q_values)
    min_q = min(q_values)

    for i, pos in enumerate(pos_list):
        if board_state[pos] is not None:
            continue
        norm = (q_values[i] - min_q) / (max_q - min_q + 1e-6)
        intensity = int(255 * norm)
        heat_color = (255, 0, 0, intensity)  # red with alpha

        surface = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(surface, heat_color, (10, 10), 10)
        coord = positions[pos]
        screen.blit(surface, (coord[0] + board_offset_x - 10, coord[1] + board_offset_y - 10))

def draw_board():
    update_layout()
    screen.fill(WHITE)
    # Draw board lines.
    for start, end in connections:
        start_pos = (positions[start][0] + board_offset_x, positions[start][1] + board_offset_y)
        end_pos = (positions[end][0] + board_offset_x, positions[end][1] + board_offset_y)
        pygame.draw.line(screen, BLACK, start_pos, end_pos, 3)
    
    # Draw board positions and any placed pieces.
    for pos, coord in positions.items():
        pos_coord = (coord[0] + board_offset_x, coord[1] + board_offset_y)
        pygame.draw.circle(screen, BLACK, pos_coord, 8, 2)
        if phase == "moving" and selected_piece == pos:
            pygame.draw.circle(screen, GREEN, pos_coord, 12, 3)
        if board_state[pos]:
            color = RED if board_state[pos]=='X' else BLUE
            pygame.draw.circle(screen, color, pos_coord, 6)
    
    draw_info()

    # 🔥 Draw heatmap if AI is active
    if AI_MODE:
        agent = deep_agent_x if current_player == 'X' else deep_agent_o
        draw_heatmap(agent)

    pygame.display.flip()

def is_mill_formed(pos, player):
    for mill in mills:
        if pos in mill:
            if all(board_state[p] == player for p in mill):
                return True
    return False

def can_remove(pos, opponent):
    if board_state[pos] != opponent:
        return False
    opponent_positions = [p for p in board_state if board_state[p] == opponent]
    if any(not is_mill_formed(p, opponent) for p in opponent_positions):
        return not is_mill_formed(pos, opponent)
    return True

def place_piece(pos):
    global paused
    paused = True
    global current_player, phase, removal_mode, info_message
    if board_state[pos] is None:
        board_state[pos] = current_player
        pieces_placed[current_player] += 1
        if is_mill_formed(pos, current_player):
            info_message = f"Player {current_player} formed a mill! Remove opponent piece."
            phase = "removal"
            removal_mode = True
        else:
            info_message = ""
            switch_player()
            if pieces_placed['X'] == TOTAL_PIECES and pieces_placed['O'] == TOTAL_PIECES:
                phase = "moving"
    draw_board()

def move_piece(from_pos, to_pos):
    global paused
    paused = True
    global current_player, phase, removal_mode, info_message
    if board_state[from_pos] == current_player and board_state[to_pos] is None:
        if count_pieces(current_player) > 3:
            if not are_adjacent(from_pos, to_pos):
                info_message = "Invalid move: destination not adjacent!"
                draw_board()
                return
        board_state[from_pos] = None
        board_state[to_pos] = current_player
        if is_mill_formed(to_pos, current_player):
            info_message = f"Player {current_player} formed a mill! Remove opponent piece."
            phase = "removal"
            removal_mode = True
        else:
            info_message = ""
            switch_player()
    draw_board()

def remove_piece(pos):
    global paused
    paused = True
    global current_player, phase, removal_mode, info_message, removed_count
    opponent = 'O' if current_player == 'X' else 'X'
    if can_remove(pos, opponent):
        board_state[pos] = None
        removed_count[opponent] += 1
        info_message = f"Player {current_player} removed opponent's piece at {pos}."
        removal_mode = False
        if pieces_placed['X'] == TOTAL_PIECES and pieces_placed['O'] == TOTAL_PIECES:
            phase = "moving"
        else:
            phase = "placing"
        switch_player()
    else:
        info_message = "Cannot remove that piece!"
    draw_board()

def switch_player():
    global current_player
    current_player = 'O' if current_player == 'X' else 'X'

def count_pieces(player):
    return sum(1 for p in board_state if board_state[p] == player)

def are_adjacent(pos1, pos2):
    return pos2 in adjacent.get(pos1, [])

def reset_game():
    global board_state, current_player, pieces_placed, removed_count, phase, removal_mode, selected_piece, selected_from, info_message, game_over
    board_state = {key: None for key in positions}
    current_player = random.choice(['X', 'O'])
    pieces_placed = {'X': 0, 'O': 0}
    removed_count = {'X': 0, 'O': 0}
    phase = "placing"
    removal_mode = False
    selected_piece = None
    selected_from = None
    info_message = ""
    game_over = False
    paused = False

    draw_board()

# ------------------ New: Reward Shaping for Mill Setups ------------------
def calculate_mill_setup_reward(player):
    """
    Checks the current board configuration for each mill possibility.
    If there is a mill (three in a row) where the player has exactly two pieces and one empty spot,
    return a bonus reward (e.g., 0.3 for each such setup).
    """
    bonus = 0.0
    for mill in mills:
        player_count = sum(1 for pos in mill if board_state[pos] == player)
        empty_count = sum(1 for pos in mill if board_state[pos] is None)
        if player_count == 2 and empty_count == 1:
            bonus += 0.3
    return bonus

# ------------------ Deep Q-Learning AI Integration ------------------
AI_MODE = True  # Enable AI self-play

# Create a Deep Q-Learning agent for each player (for the placing phase).
deep_agent_x = DeepQAgent('X')
deep_agent_o = DeepQAgent('O')

def ai_decide_and_move():
    global phase, current_player, info_message, selected_from
    # If in removal phase, perform a random valid removal.
    if phase == "removal":
        opponent = 'O' if current_player == 'X' else 'X'
        valid_removals = [pos for pos in positions if board_state[pos] == opponent and can_remove(pos, opponent)]
        if valid_removals:
            action = random.choice(valid_removals)
            remove_piece(action)
        return

    # For the "placing" phase, use the deep Q-learning agent.
    if phase == "placing":
        agent = deep_agent_x if current_player == 'X' else deep_agent_o
        # Save the current board state before making the move.
        old_state = board_state.copy()
        action_index = agent.select_action(old_state, positions)
        if action_index is not None:
            pos_list = sorted(positions.keys())
            chosen_pos = pos_list[action_index]
            place_piece(chosen_pos)
            # Calculate bonus for setting up a mill.
            reward_bonus = calculate_mill_setup_reward(agent.player)
            agent.store_transition(old_state, positions, action_index, reward_bonus, board_state, False)
            agent.optimize_model()
    elif phase == "moving":
        # For the moving phase, use a simple random legal move.
        valid_moves = []
        for pos in positions:
            if board_state[pos] == current_player:
                for next_pos in adjacent[pos]:
                    if board_state[next_pos] is None:
                        valid_moves.append((pos, next_pos))
        if valid_moves:
            move = random.choice(valid_moves)
            move_piece(move[0], move[1])

# Set a timer event to trigger AI moves every 500 milliseconds.
if AI_MODE:
    pygame.time.set_timer(pygame.USEREVENT, 250)

# ----------------------- Main Game Loop -----------------------
update_layout()
draw_board()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
            update_layout()
            draw_board()

        elif event.type == pygame.KEYDOWN:
            if not game_over and not AI_MODE:
                if event.key == pygame.K_r:
                    reset_game()

            if event.key == pygame.K_SPACE:
                paused = not paused
                info_message = "Paused" if paused else ""
                draw_board()

            elif event.key == pygame.K_ESCAPE:
                    running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not AI_MODE and not game_over:
                x, y = pygame.mouse.get_pos()
                if game_over:
                    if restart_button_rect and restart_button_rect.collidepoint(x, y):
                        reset_game()
                        continue
                    elif exit_button_rect and exit_button_rect.collidepoint(x, y):
                        running = False
                        continue
                clicked_pos = None
                for pos, coord in positions.items():
                    pos_coord = (coord[0] + board_offset_x, coord[1] + board_offset_y)
                    if (x - pos_coord[0])**2 + (y - pos_coord[1])**2 <= 64:
                        clicked_pos = pos
                        break
                if clicked_pos is None:
                    continue
                if removal_mode:
                    remove_piece(clicked_pos)
                    continue
                if phase == "placing":
                    place_piece(clicked_pos)
                elif phase == "moving":
                    if selected_from is None:
                        if board_state[clicked_pos] == current_player:
                            selected_from = clicked_pos
                            info_message = f"Selected piece at {selected_from} for moving."
                        else:
                            info_message = "Select one of your own pieces to move."
                    else:
                        if board_state[clicked_pos] is None:
                            move_piece(selected_from, clicked_pos)
                        else:
                            info_message = "Destination occupied, choose an empty spot."
                        selected_from = None
                    draw_board()

        elif event.type == pygame.USEREVENT and AI_MODE and not game_over and not paused:
            ai_decide_and_move()
            
        # Handle the auto-restart event.
        elif event.type == AUTO_RESTART_EVENT and game_over:
            reset_game()
            pygame.time.set_timer(AUTO_RESTART_EVENT, 0)

    # Check for win condition.
    if not game_over:
        for player in ['X', 'O']:
            if count_pieces(player) < 3 and pieces_placed[player] == TOTAL_PIECES:
                win_player = 'O' if player == 'X' else 'X'
                info_message = f"Player {win_player} wins!"
                win_counts[win_player] += 1
                game_over = True
                draw_board()
                # Terminal rewards update using deep agents.
                if win_player == 'X':
                    deep_agent_x.update(1, board_state, positions)
                    deep_agent_o.update(-1, board_state, positions)
                else:
                    deep_agent_x.update(-1, board_state, positions)
                    deep_agent_o.update(1, board_state, positions)
                # Set timer to auto-restart after 2000 milliseconds.
                pygame.time.set_timer(AUTO_RESTART_EVENT, 2000)
                break

pygame.quit()
sys.exit()
