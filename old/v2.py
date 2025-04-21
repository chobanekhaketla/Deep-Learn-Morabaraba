#!/usr/bin/env python3
import pygame, sys, random

# Initialize pygame and set up the window.
pygame.init()
BOARD_WIDTH, BOARD_HEIGHT = 550, 550
INFO_WIDTH = 150
INFO_MARGIN = 10
DEFAULT_WIDTH = BOARD_WIDTH + INFO_WIDTH + 2 * INFO_MARGIN  # 720
DEFAULT_HEIGHT = BOARD_HEIGHT + 2 * INFO_MARGIN              # 570
screen = pygame.display.set_mode((DEFAULT_WIDTH, DEFAULT_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Morabararaba with AI Learning")

# Define colors and font.
WHITE = (245, 222, 179)  # Light brown background
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 200, 0)
font = pygame.font.SysFont(None, 24)

# Global layout variables.
board_offset_x = 0
board_offset_y = 0
info_x = 0
restart_button_rect = None
exit_button_rect = None

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
current_player = 'X'
pieces_placed = {'X': 0, 'O': 0}
TOTAL_PIECES = 12
removed_count = {'X': 0, 'O': 0}
phase = "placing"   # "placing", "moving", or "removal"
removal_mode = False
selected_piece = None
selected_from = None
info_message = ""
game_over = False

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
    
    message_render = font.render(info_message, True, BLACK)
    screen.blit(message_render, (info_x, board_offset_y + 90))
    
    if game_over:
        over_text = "Game Over!"
        over_render = font.render(over_text, True, BLACK)
        screen.blit(over_render, (info_x, board_offset_y + 120))
        restart_button_rect = pygame.Rect(info_x, board_offset_y + 160, 100, 40)
        pygame.draw.rect(screen, GREEN, restart_button_rect)
        restart_text = font.render("Restart", True, BLACK)
        screen.blit(restart_text, (info_x + 10, board_offset_y + 170))
        exit_button_rect = pygame.Rect(info_x, board_offset_y + 210, 100, 40)
        pygame.draw.rect(screen, RED, exit_button_rect)
        exit_text = font.render("Exit", True, BLACK)
        screen.blit(exit_text, (info_x + 25, board_offset_y + 220))

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
    current_player = 'X'
    pieces_placed = {'X': 0, 'O': 0}
    removed_count = {'X': 0, 'O': 0}
    phase = "placing"
    removal_mode = False
    selected_piece = None
    selected_from = None
    info_message = ""
    game_over = False
    draw_board()

# ------------------ AI Learning (Q-Learning) Implementation ------------------
AI_MODE = True  # Set to True for AI self-play

class QLearningAgent:
    def __init__(self, player, alpha=0.1, gamma=0.9, epsilon=0.2):
        self.player = player
        self.alpha = alpha      # Learning rate
        self.gamma = gamma      # Discount factor
        self.epsilon = epsilon  # Exploration rate
        self.q_values = {}      # Q-value table
        self.last_state = None
        self.last_phase = None
        self.last_action = None

    def get_state(self):
        # Encode board as a tuple over sorted positions; '-' for empty.
        return tuple(board_state[pos] if board_state[pos] is not None else '-' for pos in sorted(positions.keys()))

    def get_possible_actions(self, phase):
        actions = []
        if phase == "placing":
            actions = [pos for pos in positions if board_state[pos] is None]
        elif phase == "moving":
            for pos in positions:
                if board_state[pos] == self.player:
                    for next_pos in adjacent[pos]:
                        if board_state[next_pos] is None:
                            actions.append((pos, next_pos))
        return actions

    def choose_action(self, phase):
        state = self.get_state()
        actions = self.get_possible_actions(phase)
        if not actions:
            return None
        # ε-greedy: with probability epsilon choose random.
        if random.random() < self.epsilon:
            action = random.choice(actions)
        else:
            q_state = self.q_values.get((state, phase), {})
            best_val = -float('inf')
            best_action = None
            for a in actions:
                q_val = q_state.get(a, 0)
                if q_val > best_val:
                    best_val = q_val
                    best_action = a
            action = best_action if best_action is not None else random.choice(actions)
        self.last_state = state
        self.last_phase = phase
        self.last_action = action
        return action

    def update(self, reward, new_phase):
        new_state = self.get_state()
        actions = self.get_possible_actions(new_phase)
        max_q_next = 0
        q_new = self.q_values.get((new_state, new_phase), {})
        if actions:
            max_q_next = max(q_new.get(a, 0) for a in actions)
        key = (self.last_state, self.last_phase)
        if key not in self.q_values:
            self.q_values[key] = {}
        old_q = self.q_values[key].get(self.last_action, 0)
        new_q = old_q + self.alpha * (reward + self.gamma * max_q_next - old_q)
        self.q_values[key][self.last_action] = new_q

# Create an agent for each player.
agent_x = QLearningAgent('X')
agent_o = QLearningAgent('O')

def ai_decide_and_move():
    global phase, current_player, info_message, selected_from
    # In removal phase, choose a valid opponent piece randomly.
    if phase == "removal":
        opponent = 'O' if current_player == 'X' else 'X'
        valid_removals = [pos for pos in positions if board_state[pos] == opponent and can_remove(pos, opponent)]
        if valid_removals:
            action = random.choice(valid_removals)
            remove_piece(action)
            # Reward a small bonus for removal.
            if current_player == 'X':
                agent_x.update(0.1, phase)
            else:
                agent_o.update(0.1, phase)
        return

    if phase == "placing":
        agent = agent_x if current_player == 'X' else agent_o
        action = agent.choose_action(phase)
        if action is not None:
            place_piece(action)
            agent.update(0, phase)
    elif phase == "moving":
        agent = agent_x if current_player == 'X' else agent_o
        action = agent.choose_action(phase)
        if action is not None and isinstance(action, tuple):
            valid_moves = []
            for pos in positions:
                if board_state[pos] == current_player:
                    for next_pos in adjacent[pos]:
                        if board_state[next_pos] is None:
                            valid_moves.append((pos, next_pos))
            if action not in valid_moves and valid_moves:
                action = random.choice(valid_moves)
            if action:
                move_piece(action[0], action[1])
                agent.update(0, phase)

# Set a timer event to trigger AI moves every 500 milliseconds.
if AI_MODE:
    pygame.time.set_timer(pygame.USEREVENT, 500)

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
                elif event.key == pygame.K_ESCAPE:
                    running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not AI_MODE and not game_over:
                x, y = pygame.mouse.get_pos()
                # Check if clicking on restart or exit buttons when game is over.
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

        elif event.type == pygame.USEREVENT and AI_MODE and not game_over:
            ai_decide_and_move()

    if not game_over:
        for player in ['X', 'O']:
            if count_pieces(player) < 3 and pieces_placed[player] == TOTAL_PIECES:
                win_player = 'O' if player == 'X' else 'X'
                info_message = f"Player {win_player} wins!"
                game_over = True
                draw_board()
                # Terminal rewards.
                if win_player == 'X':
                    agent_x.update(1, phase)
                    agent_o.update(-1, phase)
                else:
                    agent_x.update(-1, phase)
                    agent_o.update(1, phase)
                break

pygame.quit()
sys.exit()
