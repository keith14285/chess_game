# This class is responsible for storing all the information about the current state of the chess game.  It will also be responeble
# for determining the valid moves at the current state.  It will also keep a move log.

class GameState():

    def __init__(self):
        # Board is 8 by 8, 2 dimensional list.  Each element of the list has 2 characters.  The first character represents the color of the piece, and
        # second character represents the type of the piece. The string "--" represents an empty space.
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp" for i in range(8)],
            ["--" for i in range(8)],
            ["--" for i in range(8)],
            ["--" for i in range(8)],
            ["--" for i in range(8)],
            ["wp" for i in range(8)],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]

        self.moveFunctions = {'p': self.pawn_moves, 'R': self.rook_moves, 'N': self.knight_moves,
                            'B': self.bishop_moves, 'Q': self.queen_moves, 'K': self.king_moves}
        
        self.white_to_move = True
        self.moveLog = []
        self.pos_white_king = (7, 4)
        self.pos_black_king = (0, 4)
        self.in_check = False
        self.pins = []
        self.checks = []
        self.checkmate = False
        self.stalemate = False
        self.en_passant_possible = () # coordinates for where an en passant is possible
        self.wks_castle = True
        self.wqs_castle = True
        self.bks_castle = True
        self.bqs_castle = True
        self.castle_rightsLog = [castle_rights(self.wks_castle, self.wqs_castle, self.bks_castle, self.bqs_castle)]


    
    # Takes a move as a parameter and executes it.
    def makeMove(self, move):
        self.board[move.start_row][move.start_column] = "--"
        self.board[move.end_row][move.end_column] = move.moved_piece
        self.moveLog.append(move) # log the move
        self.white_to_move = not self.white_to_move
        # update the king's position if moved
        if move.moved_piece == "wK":
            self.pos_white_king = (move.end_row, move.end_column)
        elif move.moved_piece == "bK":
            self.pos_black_king = (move.end_row, move.end_column)
        
        # en passant
        # if pawn moves twice, then next move can capture en passant
        if move.moved_piece[1] == 'p' and abs(move.start_row - move.end_row) == 2:
            self.en_passant_possible = ((move.end_row + move.start_row) // 2, move.end_column)
        else:
            self.en_passant_possible = ()
        
        # if en passant move, then update the board to capture pawn
        if move.en_passant:
            self.board[move.start_row][move.end_column] = '--'
         
        # pawn promotion
        if move.pawn_promotion:
            promotedPiece = input("Promote to Q, R, B, N: ")
            self.board[move.end_row][move.end_column] = move.moved_piece[0] + promotedPiece
        
        # castle moves
        if move.castle:
            if move.end_column - move.start_column == 2: # king side castle
                self.board[move.end_row][move.end_column - 1] = self.board[move.end_row][move.end_column + 1] # moves the rook
                self.board[move.end_row][move.end_column + 1] = '--'
            else:
                self.board[move.end_row][move.end_column + 1] = self.board[move.end_row][move.end_column - 2]
                self.board[move.end_row][move.end_column - 2] = '--'

        
        # updating castling rights
        self.update_castle_rights(move)
        self.castle_rightsLog.append(castle_rights(self.wks_castle, self.wqs_castle, self.bks_castle, self.bqs_castle))
        
        
    
    # Undo the last move
    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.start_row][move.start_column] = move.moved_piece
            self.board[move.end_row][move.end_column] = move.captured_piece
            self.white_to_move = not self.white_to_move
            # update the king's position if needed
            if move.moved_piece == "wK":
                self.pos_white_king = (move.start_row, move.start_column)
            elif move.moved_piece == "bK":
                self.pos_black_king = (move.start_row, move.start_column)
            # undo en passant
            if move.en_passant:
                self.board[move.end_row][move.end_column] = "--" # removes pawn added in wrong square
                self.board[move.start_row][move.end_column] = move.captured_piece # puts the pawn back to previous uncaptured square
                self.en_passant_possible = (move.end_row, move.end_column) # allow en passant to happen next move
            # undo the two square pawn advance which would have made en passant possible
            if move.moved_piece[1] == 'p' and abs(move.start_row - move.end_row) == 2:
                self.en_passant_possible = ()

            # undo castle move
            if move.castle:
                if move.end_column - move.start_column == 2: # king side
                    self.board[move.end_row][move.end_column + 1] = self.board[move.end_row][move.end_column - 1]
                    self.board[move.end_row][move.end_column - 1] = '--'
                else:
                    self.board[move.end_row][move.end_column - 2] = self.board[move.end_row][move.end_column + 1]
                    self.board[move.end_row][move.end_column + 1] = '--'


            # undo the castle rights
            self.castle_rightsLog.pop() # get rid of new castle rights from the move that we are undoing
            castle_rights = self.castle_rightsLog[-1] # set current castle rights to the last one on the list
            self.wks_castle = castle_rights.wks
            self.wqs_castle = castle_rights.wqs
            self.bks_castle = castle_rights.bks
            self.bqs_castle = castle_rights.bqs

    
    # Update castle rights
    def update_castle_rights(self, move):
        if move.moved_piece == 'wK':
            self.wks_castle = False
            self.wqs_castle = False
        elif move.moved_piece == 'bK':
            self.bks_castle = False
            self.bqs_castle = False
        elif move.moved_piece == 'wR':
            if move.start_row == 7:
                if move.start_column == 0: # white rook on the queen side
                    self.wqs_castle = False
                elif move.start_column == 7:
                    self.wks_castle = False # white rook on the king side
        elif move.moved_piece == 'bR':
            if move.start_row == 0:
                if move.start_column == 0: # black rook on the queen side
                    self.bqs_castle = False
                elif move.start_column == 7: # black rook on the king side
                    self.bks_castle = False

    # Valid moves - all moves considering checks
    def valid_moves(self):
        moves = []
        self.in_check, self.pins, self.checks = self.check_pins_and_checks()
        if self.white_to_move:
            king_row = self.pos_white_king[0]
            king_column = self.pos_white_king[1]
        else:
            king_row = self.pos_black_king[0]
            king_column = self.pos_black_king[1]
        if self.in_check: 
            if len(self.checks) == 1: # Only one check, block check or move king
                moves = self.all_moves()
                # to block check, move piece into one of the squares between the opposition piece and the king
                check = self.checks[0]
                check_row = check[0]
                check_column = check[1]
                piece_checking = self.board[check_row][check_column]
                valid_squares = [] # squares that pieces can move to if the king is in check
                if piece_checking[1] == "N":
                    valid_squares = [(check_row, check_column)]
                else:
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i, king_column + check[3] * i)
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_column:
                            break
                # get rid of any moves that do not block check or move king
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].moved_piece[1] != "K": # move doesn't move king so it must block or capture
                        if not (moves[i].end_row, moves[i].end_column) in valid_squares: # move doesn't block check or capture piece
                            moves.remove(moves[i])
            
            else: # double check, king has to move
                self.king_moves(king_row, king_column, moves)
        
        else: # not in check so all moves are good
            moves = self.all_moves()
        
        if len(moves) == 0:
            if self.in_check:
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

    
        return moves


    # All moves - not considering checks
    def all_moves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == "w" and self.white_to_move) or (turn == "b" and not self.white_to_move):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)
        
        return moves

    # Get all pawn moves for pawn located in row, col.  Add these moves to list
    def pawn_moves(self, r, c, moves):
        pinned_piece = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                pinned_piece = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        if self.white_to_move:
            moveAmount = -1
            start_row = 6
            backRow = 0
            oppColor = 'b'
        
        else:
            moveAmount = 1
            start_row = 1
            backRow = 7
            oppColor = 'w'
        
        pawn_promotion = False

        if self.board[r + moveAmount][c] == "--":
            if not pinned_piece or pin_direction == (moveAmount, 0):
                if r + moveAmount == backRow:
                    pawn_promotion = True
                moves.append(Move((r,c), (r + moveAmount,c), self.board, pawn_promotion = pawn_promotion))
                if r == start_row and self.board[r + 2 * moveAmount][c] == "--":
                    moves.append(Move((r,c), (r + 2 * moveAmount,c), self.board))

        if c - 1 >= 0: # captures to the left
            if not pinned_piece or pin_direction == (moveAmount , -1):
                if self.board[r + moveAmount][c - 1][0] == oppColor:
                    if r + moveAmount == backRow:
                        pawn_promotion = True
                    moves.append(Move((r,c), (r + moveAmount,c-1), self.board, pawn_promotion = pawn_promotion))
                if (r + moveAmount, c - 1) == self.en_passant_possible:
                    moves.append(Move((r,c), (r + moveAmount,c-1), self.board, en_passant = True))
    
        if c + 1 <= len(self.board) - 1: # captures to the right
            if not pinned_piece or pin_direction == (moveAmount , 1):
                if self.board[r + moveAmount][c + 1][0] == oppColor:
                    if r + moveAmount == backRow:
                        pawn_promotion = True
                    moves.append(Move((r,c), (r + moveAmount,c+1), self.board, pawn_promotion = pawn_promotion))
                if (r + moveAmount, c + 1) == self.en_passant_possible:
                    moves.append(Move((r,c), (r + moveAmount,c+1), self.board, en_passant = True))
        

    # Get all rook moves for rook located in row, col.  Add these moves to list
    def rook_moves(self, r, c, moves):
        pinned_piece = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                pinned_piece = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != "Q":
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up, left, down, right
        opposingColor = "b" if self.white_to_move else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_column = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_column < 8: # on board
                    if not pinned_piece or pin_direction == d or pin_direction == (-d[0], -d[1]): # have to be able to move toward pin and away from pin
                        endPiece = self.board[end_row][end_column]
                        if endPiece == "--": # valid
                            moves.append(Move((r, c), (end_row, end_column), self.board))
                        elif endPiece[0] == opposingColor: # capture opposing piece
                            moves.append(Move((r,c), (end_row, end_column), self.board))
                            break
                        else: # friendly fire
                            break
                else: # off board
                    break

    def knight_moves(self, r, c, moves):
        pinned_piece = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                pinned_piece = True
                self.pins.remove(self.pins[i])
                break

        knightMoves = ((-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2))
        sameColor = "w" if self.white_to_move else "b"
        for i in knightMoves:
            end_row = r + i[0]
            end_column = c + i[1]
            if 0 <= end_row < 8 and 0 <= end_column < 8:
                if not pinned_piece:
                    endPiece = self.board[end_row][end_column]
                    if endPiece[0] != sameColor:
                        moves.append(Move((r,c), (end_row, end_column), self.board))


    # Get all bishop moves for bishop located in row, col.  Add these moves to list
    def bishop_moves(self, r, c, moves):
        pinned_piece = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                pinned_piece = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        opposingColor = "b" if self.white_to_move else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_column = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_column < 8: # on board
                    if not pinned_piece or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        endPiece = self.board[end_row][end_column]
                        if endPiece == "--": # valid
                            moves.append(Move((r, c), (end_row, end_column), self.board))
                        elif endPiece[0] == opposingColor: # capture opposing piece
                            moves.append(Move((r,c), (end_row, end_column), self.board))
                            break
                        else: # friendly fire
                            break
                else: # off board
                    break

    # Get all queen moves for queen located in row, col.  Add these moves to list
    def queen_moves(self, r, c, moves):
        self.rook_moves(r, c, moves)
        self.bishop_moves(r, c, moves)

    def king_moves(self, r, c, moves):
        kingMoves = ((-1,-1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        sameColor = "w" if self.white_to_move else "b"
        for i in range(8):
            end_row = r + kingMoves[i][0]
            end_column = c + kingMoves[i][1]
            if 0 <= end_row < 8 and 0 <= end_column < 8:
                endPiece = self.board[end_row][end_column]
                if endPiece[0] != sameColor:
                    # place king on end square and check for checks
                    if sameColor == "w":
                        self.pos_white_king = (end_row, end_column)
                    else:
                        self.pos_black_king = (end_row, end_column)
                    in_check, pins, checks = self.check_pins_and_checks()
                    if not in_check:
                        moves.append(Move((r,c), (end_row, end_column), self.board))
                    # place king in original location
                    if sameColor == "w":
                        self.pos_white_king = (r, c)
                    else:
                        self.pos_black_king = (r, c)
        self.castle_moves(r, c, moves, sameColor)


    def castle_moves(self, r, c, moves, sameColor):
        in_check = self.square_under_attack(r, c, sameColor)
        if self.in_check:
            return
        if (self.white_to_move and self.wks_castle) or (not self.white_to_move and self.bks_castle):
            self.ks_castle_moves(r, c, moves, sameColor)
        if (self.white_to_move and self.wqs_castle) or (not self.white_to_move and self.bqs_castle):
            self.qs_castle_moves(r, c, moves, sameColor)

        
    def ks_castle_moves(self, r, c, moves, sameColor):
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--" and not self.square_under_attack(r, c+1, sameColor) and not self.square_under_attack(r, c+2, sameColor):
            moves.append(Move((r, c), (r, c+2), self.board, castle = True)) 

    def qs_castle_moves(self, r, c, moves, sameColor):
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--" and self.board[r][c-3] == "--" and not self.square_under_attack(r, c-1, sameColor) and not self.square_under_attack(r, c-2, sameColor):
            moves.append(Move((r, c), (r, c-2), self.board, castle = True))

    

    def square_under_attack(self, r, c, sameColor):
        # check outward from square
        oppColor = "w" if sameColor == "b" else "b"
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_column = r + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_column < 8:
                    endPiece = self.board[end_row][end_column]
                    if endPiece[0] == sameColor: # no attack from that direction
                        break
                    elif endPiece[0] == oppColor:
                        type_piece = endPiece[1]
                        # Checks and pins conditions.
                        # 1. diagonally away from king and the piece is a bishop
                        # 2. orthogonally away from king and the piece is a rook
                        # 3. one square diagonally away from the king and the piece is a pawn
                        # 4. any direction and the piece is a queen
                        # 5. any direction one square away and the piece is a king.  - necessary to prevent king moving to a square controlled by another king.
                        if (4 <= j <= 7 and type_piece == "B") or (0 <= j <= 3 and type_piece == "R") or \
                            (i == 1 and type_piece == "p" and ((oppColor == "w" and 6 <= j <= 7) or (oppColor == "b" and 4 <= j <= 5 ))) or \
                            (type_piece == "Q") or (type_piece == "K" and i == 1):
                            return True
                        else:
                            break
                else:
                    break
        
        # check for knight checks
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            end_row = r + m[0]
            end_column = r + m[1]
            if 0 <= end_row < 8 and 0 <= end_column < 8:
                endPiece = self.board[end_row][end_column]
                if endPiece[0] == oppColor and endPiece[1] == "N":
                    return True
        
        return False

    def check_pins_and_checks(self):
        pins = [] # displays square where the ally pinned piece is and the direction it is pinned from
        checks = [] # displays square where opposition is providing a check
        in_check = False
        if self.white_to_move:
            oppColor = "b"
            sameColor = "w"
            start_row = self.pos_white_king[0]
            start_column = self.pos_white_king[1]
        else:
            sameColor = "b"
            oppColor = "w"
            start_row = self.pos_black_king[0]
            start_column = self.pos_black_king[1]
        # Check outward from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()
            for i in range(1, 8):
                end_row = start_row + d[0] * i
                end_column = start_column + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_column < 8:
                    endPiece = self.board[end_row][end_column]
                    if endPiece[0] == sameColor and endPiece[1] != "K": # the first ally piece could be a pin (or not)
                        if possiblePin == ():
                            possiblePin = (end_row, end_column, d[0], d[1])
                        else: # there is a second ally piece, so there is no pin in this situation
                            break
                    elif endPiece[0] == oppColor:
                        type_piece = endPiece[1]
                        # Checks and pins conditions.
                        # 1. diagonally away from king and the piece is a bishop
                        # 2. orthogonally away from king and the piece is a rook
                        # 3. one square diagonally away from the king and the piece is a pawn
                        # 4. any direction and the piece is a queen
                        # 5. any direction one square away and the piece is a king.  - necessary to prevent king moving to a square controlled by another king.
                        if (4 <= j <= 7 and type_piece == "B") or (0 <= j <= 3 and type_piece == "R") or \
                            (i == 1 and type_piece == "p" and ((oppColor == "w" and 6 <= j <= 7) or (oppColor == "b" and 4 <= j <= 5 ))) or \
                            (type_piece == "Q") or (type_piece == "K" and i == 1):
                            if possiblePin == (): # There is no piece blocking, therefore it is in check
                                in_check = True
                                checks.append((end_row, end_column, d[0], d[1]))
                                break
                            else: # piece blocking so pin
                                pins.append(possiblePin)
                                break
                        else: # opposing piece is not applying check
                            break
                else: # off board
                    break

        # A knight cannot pin.  So here we check for knight checks
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            end_row = start_row + m[0]
            end_column = start_column + m[1]
            if 0 <= end_row < 8 and 0 <= end_column < 8:
                endPiece = self.board[end_row][end_column]
                if endPiece[0] == oppColor and endPiece[1] == "N":
                    in_check = True
                    checks.append((end_row, end_column, m[0], m[1]))
        
        return in_check, pins, checks      

class castle_rights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

  
class Move():

    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0 }
    rows_to_ranks = {v:k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v:k for k, v in files_to_cols.items()}


    def __init__(self, startSq, endSq, board, en_passant = False, pawn_promotion = False, castle = False):
        self.start_row = startSq[0]
        self.start_column = startSq[1]
        self.end_row = endSq[0]
        self.end_column = endSq[1]
        self.moved_piece = board[self.start_row][self.start_column]
        self.captured_piece = board[self.end_row][self.end_column]
        # pawn promotion
        self.pawn_promotion = pawn_promotion
        # En Passant Move
        self.en_passant = en_passant
        if en_passant:
            self.captured_piece = 'bp' if self.moved_piece == 'wp' else 'wp'
        # Castle
        self.castle = castle

        self.moveID = self.start_row * 1000 + self.start_column * 100 + self.end_row * 10 + self.end_column
        
    
    # Overriding the equals method
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def GetChessNotation(self):
        return self.GetRankFile(self.start_row, self.start_column) + self.GetRankFile(self.end_row, self.end_column)

    def GetRankFile(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]



