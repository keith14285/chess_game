# This is our main driver file.  It is responsible for handling user input
# and displaying the current GameState object

import pygame
from chess_backend.constants import *
from chess_backend.ChessEngine import GameState, Move, castle_rights

pygame.display.set_caption("Chess")

# Initialise a global dictionary of images - This will be called exactly once
# in the main

def load_Images():
    pieces = ["wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        IMAGES[piece] = pygame.transform.scale(pygame.image.load("images_chess/set_1/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

def get_row_col_from_mouse(pos):
    x, y = pos
    row = y // SQ_SIZE
    col = x // SQ_SIZE
    return row, col


# Handles user input and updating the graphics

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess")
    clock = pygame.time.Clock()
    screen.fill(pygame.Color(WHITE))
    gs = GameState()
    validMoves = gs.valid_moves()
    movesMade = False # flag variable for when a move is made
    animate = False
    load_Images()
    running = True
    sqSelected = () # keeps track of last click of the user (tuple: (row, col))
    playerClicks = []
    gameOver = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Mouse handler
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = pygame.mouse.get_pos()
                    row, col = get_row_col_from_mouse(location)
                    if sqSelected == (row, col):
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2: # after second click
                        move = Move(playerClicks[0], playerClicks[1], gs.board)
                        # print(move.GetChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                movesMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []
                        if not movesMade:
                            playerClicks = [sqSelected]
            
            # Key handler
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    gs.undoMove()
                    movesMade = True
                    animate = False
                if event.key == pygame.K_r: # reset board
                    gs = GameState()
                    validMoves = gs.valid_moves()
                    sqSelected = ()
                    playerClicks = []
                    movesMade = False
                    animate = False
            
        if movesMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.valid_moves()
            movesMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected)

        if gs.checkmate:
            gameOver = True
            if gs.white_to_move:
                display_message('Black wins by checkmate')
            else:
                display_message('White wins by checkmate')
        elif gs.stalemate:
            gameOver = True
            display_message('Stalemate')

        clock.tick(MAX_FPS)
        pygame.display.flip()


# Highlight squares selected and moves for piece selected

def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.white_to_move else 'b'):
            # highlight selected square
            s = pygame.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) # transparency value
            s.fill(pygame.Color(BLUE))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            # highlight moves from that square
            s.fill(pygame.Color(YELLOW))
            for move in validMoves:
                if move.start_row == r and move.start_column == c:
                    screen.blit(s, (SQ_SIZE * move.end_column, SQ_SIZE * move.end_row))

# Responsible for all the graphics within a current game state

def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    DrawPieces(screen, gs.board)

# Draw the squares on the board.  Top left square is always light

def drawBoard(screen):
    colors = [WHITE, GRAY]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            pygame.draw.rect(screen, color, pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
            
def DrawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def animateMove(move, screen, board, clock):
    colors = [WHITE, GRAY]
    coords = [] # list of rows and columns where animation will move through
    deltaRow = move.end_row - move.start_row
    deltaCol = move.end_column - move.start_column
    framesPerSquare = 10 # frames to move one square of animation
    frameCount = (abs(deltaRow) + abs(deltaCol)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.start_row + deltaRow * frame / frameCount, move.start_column + deltaCol * frame / frameCount)
        drawBoard(screen)
        DrawPieces(screen, board)
        # erase the piece moved from its ending square
        color = colors[(move.end_row + move.end_column) % 2]
        endSquare = pygame.Rect(move.end_column * SQ_SIZE, move.end_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        pygame.draw.rect(screen, color, endSquare)
        # draw captured piece onto rectangle
        if move.captured_piece != '--':
            screen.blit(IMAGES[move.captured_piece], endSquare)
        # draw moving piece
        screen.blit(IMAGES[move.moved_piece], pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        pygame.display.flip()
        clock.tick(60)

def display_message(text):
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    font = pygame.font.SysFont('Helvetica', 20, True, False)
    pygame.time.delay(100)
    screen.fill(WHITE)
    text = font.render(text, 1, BLACK)
    screen.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/2 - text.get_height()/2))
    pygame.display.update()
    pygame.time.delay(1000)

if __name__ == "__main__":
    main()
     