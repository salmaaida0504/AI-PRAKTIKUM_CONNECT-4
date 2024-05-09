import numpy as np
import pygame
import sys
import math
import random

# Define colors
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

ROW_COUNT = 6
COLUMN_COUNT = 7

def create_board():
    board = np.zeros((ROW_COUNT, COLUMN_COUNT))
    return board

# Function to drop a piece into the board
def drop_piece(board, row, col, piece):
    board[row][col] = piece

# Function to check if a location is valid for dropping a piece
def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == 0

# Function to get the next open row in a column
def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

# Function to print the board
def print_board(board):
    print(np.flip(board, 0))

# Function to check for a winning move
def winning_move(board, piece):
    # Check horizontal locations for win
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c + 1] == piece and board[r][c + 2] == piece and board[r][c + 3] == piece:
                return True, [(r, c), (r, c+1), (r, c+2), (r, c+3)]

    # Check vertical locations for win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c] == piece and board[r + 2][c] == piece and board[r + 3][c] == piece:
                return True, [(r, c), (r+1, c), (r+2, c), (r+3, c)]

    # Check positively sloped diaganols
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c + 1] == piece and board[r + 2][c + 2] == piece and board[r + 3][c + 3] == piece:
                return True, [(r, c), (r+1, c+1), (r+2, c+2), (r+3, c+3)]

    # Check negatively sloped diaganols
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r - 1][c + 1] == piece and board[r - 2][c + 2] == piece and board[r - 3][c + 3] == piece:
                return True, [(r, c), (r-1, c+1), (r-2, c+2), (r-3, c+3)]
    return False, []

# Function to draw the board
def draw_board(board, winning_pos=None):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), RADIUS)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == 1:
                pygame.draw.circle(screen, RED, (int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
            elif board[r][c] == 2:
                pygame.draw.circle(screen, YELLOW, (int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)

    # Draw winning position (if available)
    if winning_pos:
        for pos in winning_pos:
            # Calculate the center of the circle
            x = (pos[1] * SQUARESIZE) + SQUARESIZE // 2
            y = height - (pos[0] * SQUARESIZE + SQUARESIZE // 2)
            # Draw the X mark at the center of the circle
            pygame.draw.line(screen, BLACK, (x - 20, y - 20), (x + 20, y + 20), 5)
            pygame.draw.line(screen, BLACK, (x - 20, y + 20), (x + 20, y - 20), 5)

    pygame.display.update()

# Function to display the menu screen
def menu_screen():
    screen.fill((255, 255, 255))
    font = pygame.font.Font(None, 36)
    text_auto = font.render("Auto Mode", True, (0, 0, 0))
    text_manual = font.render("Manual Mode", True, (0, 0, 0))
    text_auto_rect = text_auto.get_rect(center=(width // 2, height // 2 - 50))
    text_manual_rect = text_manual.get_rect(center=(width // 2, height // 2 + 50))
    
    # Draw buttons with red background and black border
    pygame.draw.rect(screen, RED, text_auto_rect, 0)  # Red button for "Auto Mode"
    pygame.draw.rect(screen, RED, text_manual_rect, 0)  # Red button for "Manual Mode"
    
    # Check if cursor is hovering over the button
    if text_auto_rect.collidepoint(pygame.mouse.get_pos()):
        pygame.draw.rect(screen, BLACK, text_auto_rect, 2)  # Add black border if hovering
        pygame.mouse.set_cursor(*pygame.cursors.tri_left)  # Change cursor to indicate clickable
    else:
        pygame.draw.rect(screen, BLACK, text_auto_rect, 2)  # Black border for "Auto Mode" button

    if text_manual_rect.collidepoint(pygame.mouse.get_pos()):
        pygame.draw.rect(screen, BLACK, text_manual_rect, 2)  # Add black border if hovering
        pygame.mouse.set_cursor(*pygame.cursors.tri_left)  # Change cursor to indicate clickable
    else:
        pygame.draw.rect(screen, BLACK, text_manual_rect, 2)  # Black border for "Manual Mode" button
    
    screen.blit(text_auto, text_auto_rect)
    screen.blit(text_manual, text_manual_rect)
    pygame.display.update()
    return text_auto_rect, text_manual_rect

# Function to check if the board is full
def is_board_full(board):
    return all(board[ROW_COUNT - 1])

# Function to evaluate the score for a particular move
def evaluate_window(window, piece):
    score = 0
    opp_piece = 1 if piece == 2 else 2
    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(0) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(0) == 2:
        score += 2
    if window.count(opp_piece) == 3 and window.count(0) == 1:
        score -= 4
    return score

# Function to calculate the score of a position
def score_position(board, piece):
    score = 0
    # Score center column
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT // 2])]
    center_count = center_array.count(piece)
    score += center_count * 3
    # Score horizontal
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c:c + 4]
            score += evaluate_window(window, piece)
    # Score vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW_COUNT - 3):
            window = col_array[r:r + 4]
            score += evaluate_window(window, piece)
    # Score positively sloped diagonal
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + i][c + i] for i in range(4)]
            score += evaluate_window(window, piece)
    # Score negatively sloped diagonal
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + 3 - i][c + i] for i in range(4)]
            score += evaluate_window(window, piece)
    return score

# Function to find all valid locations for dropping a piece
def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

# Function to perform a minimax search
def minimax(board, depth, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    if depth == 0 or winning_move(board, 1)[0] or winning_move(board, 2)[0] or is_board_full(board):
        if winning_move(board, 2)[0]:
            return None, 100000000000000
        elif winning_move(board, 1)[0]:
            return None, -10000000000000
        else:
            return None, 0
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, 2)
            new_score = minimax(b_copy, depth - 1, False)[1]
            if new_score > value:
                value = new_score
                column = col
        return column, value
    else:
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, 1)
            new_score = minimax(b_copy, depth - 1, True)[1]
            if new_score < value:
                value = new_score
                column = col
        return column, value

# Function to display winner notification and return to menu
def winner_notification(winner, winning_pos):
    pygame.display.set_caption("Winner!")
    screen.fill((255, 255, 255))
    font = pygame.font.Font(None, 36)
    text_winner = font.render(f"{winner} wins!!!", True, BLACK)
    text_rect = text_winner.get_rect(center=(width // 2, SQUARESIZE // 2))
    screen.blit(text_winner, text_rect)
    
    # Draw winning positions
    draw_board(board, winning_pos)
    
    pygame.display.update()
    pygame.time.wait(3000)

    # Reset game variables
    return True


# Initialize Pygame
pygame.init()

# Set up the screen
SQUARESIZE = 100
width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT + 1) * SQUARESIZE
size = (width, height)
RADIUS = int(SQUARESIZE / 2 - 5)
screen = pygame.display.set_mode(size)

# Main loop
menu = True
mode = None
while menu:
    text_auto_rect, text_manual_rect = menu_screen()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if text_auto_rect.collidepoint(event.pos):
                mode = 'auto'
                menu = False
            elif text_manual_rect.collidepoint(event.pos):
                mode = 'manual'
                menu = False

while True:
    # Initialize game variables
    board = create_board()
    print_board(board)
    game_over = False
    turn = 0

    # Panggil draw_board di sini setelah mode dipilih
    draw_board(board)

    # Start game loop
    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                posx = event.pos[0]
                if turn == 0:
                    pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE / 2)), RADIUS)
                else:
                    pygame.draw.circle(screen, YELLOW, (posx, int(SQUARESIZE / 2)), RADIUS)
                pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                posx = event.pos[0]
                col = int(math.floor(posx / SQUARESIZE))

                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, 1 if turn == 0 else 2)

                    win, win_pos = winning_move(board, 1 if turn == 0 else 2)
                    if win:
                        if mode == 'manual':
                            game_over = winner_notification(f"Player {1 if turn == 0 else 2}", win_pos)
                        else:
                            game_over = winner_notification("Player" if turn == 0 else "Computer", win_pos)

                print_board(board)
                draw_board(board)

                turn += 1
                turn %= 2

                if game_over:
                    break

            if mode == 'auto' and turn == 1 and not game_over:
                col, _ = minimax(board, 4, True)  # You can adjust the depth for more or less difficult AI
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, 2)

                win, win_pos = winning_move(board, 2)
                if win:
                    game_over = winner_notification("Computer", win_pos)

                print_board(board)
                draw_board(board)

                turn += 1
                turn %= 2

                if game_over:
                    break

    # Back to menu
    menu = True
    while menu:
        text_auto_rect, text_manual_rect = menu_screen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if text_auto_rect.collidepoint(event.pos):
                    mode = 'auto'
                    menu = False  # Keluar dari loop menu setelah mode dipilih
                elif text_manual_rect.collidepoint(event.pos):
                    mode = 'manual'
                    menu = False  # Keluar dari loop menu setelah mode dipilih

