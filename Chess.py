import numpy as np
from enum import Enum, auto
import copy

class PieceType(Enum):
    EMPTY = auto()
    PAWN = auto()
    KNIGHT = auto()
    BISHOP = auto()
    ROOK = auto()
    QUEEN = auto()
    KING = auto()

class Color(Enum):
    NONE = auto()
    WHITE = auto()
    BLACK = auto()

class Piece:
    def __init__(self, piece_type=PieceType.EMPTY, color=Color.NONE):
        self.piece_type = piece_type
        self.color = color
        self.has_moved = False
    
    def __str__(self):
        if self.piece_type == PieceType.EMPTY:
            return "."
        
        symbol = {
            PieceType.PAWN: "P",
            PieceType.KNIGHT: "N",
            PieceType.BISHOP: "B",
            PieceType.ROOK: "R",
            PieceType.QUEEN: "Q",
            PieceType.KING: "K"
        }[self.piece_type]
        
        return symbol if self.color == Color.WHITE else symbol.lower()
    
    def copy(self):
        new_piece = Piece(self.piece_type, self.color)
        new_piece.has_moved = self.has_moved
        return new_piece

class ChessGame:
    def __init__(self):
        self.board = np.array([[Piece() for _ in range(8)] for _ in range(8)])
        self.current_player = Color.WHITE
        self.move_history = []
        self.initialize_board()
        self.en_passant_target = None
        self.white_king_pos = (7, 4)
        self.black_king_pos = (0, 4)
        self.game_over = False
        self.winner = None
    
    def initialize_board(self):
        # Set up the pawns
        for col in range(8):
            self.board[1][col] = Piece(PieceType.PAWN, Color.BLACK)
            self.board[6][col] = Piece(PieceType.PAWN, Color.WHITE)
        
        # Set up the other pieces
        back_row = [PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP, PieceType.QUEEN, 
                    PieceType.KING, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK]
        
        for col in range(8):
            self.board[0][col] = Piece(back_row[col], Color.BLACK)
            self.board[7][col] = Piece(back_row[col], Color.WHITE)
    
 #   def print_board(self):
 #       print("  a b c d e f g h")
 #       print(" +-----------------+")
 #       for row in range(8):
 #           print(f"{8-row}|", end=" ")
 #           for col in range(8):
 #               print(str(self.board[row][col]), end=" ")
 #           print(f"|{8-row}")
 #       print(" +-----------------+")
  #      print("  a b c d e f g h")
    
    def algebraic_to_coords(self, algebraic):
        if len(algebraic) != 2:
            return None
        col = ord(algebraic[0].lower()) - ord('a')
        row = 8 - int(algebraic[1])
        if 0 <= row < 8 and 0 <= col < 8:
            return (row, col)
        return None
    
    def coords_to_algebraic(self, coords):
        row, col = coords
        return chr(col + ord('a')) + str(8 - row)
    
    def make_move(self, from_pos, to_pos, skip_validation=False):
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Get the piece being moved
        piece = self.board[from_row][from_col]
        
        # Check that the piece exists and belongs to the current player
        if piece.piece_type == PieceType.EMPTY:
            print(f"No piece at {from_pos}")
            return False
        if piece.color != self.current_player:
            print(f"Not your turn. Current player: {self.current_player}, Piece color: {piece.color}")
            return False
        
        # Always validate unless explicitly told to skip
        if not skip_validation and not self.is_valid_move(from_pos, to_pos):
            print(f"Invalid move: {from_pos} to {to_pos}")
            return False
        
        # Store the move
        self.move_history.append((from_pos, to_pos, self.board[to_row][to_col].copy(), self.en_passant_target))
        
        # Handle en passant capture
        en_passant_capture = False
        if piece.piece_type == PieceType.PAWN and (to_col != from_col) and self.board[to_row][to_col].piece_type == PieceType.EMPTY:
            if self.en_passant_target == to_pos:
                # Capture the pawn that just moved two squares
                if piece.color == Color.WHITE:
                    self.board[to_row + 1][to_col] = Piece()
                else:
                    self.board[to_row - 1][to_col] = Piece()
                en_passant_capture = True
        
        # Update en passant target
        self.en_passant_target = None
        if piece.piece_type == PieceType.PAWN and abs(to_row - from_row) == 2:
            # Set the en passant target to the square the pawn skipped
            middle_row = (from_row + to_row) // 2
            self.en_passant_target = (middle_row, from_col)
        
        # Handle castling
        if piece.piece_type == PieceType.KING and abs(to_col - from_col) == 2:
            # Determine rook positions based on castling side
            if to_col > from_col:  # Kingside
                rook_from = (from_row, 7)
                rook_to = (from_row, to_col - 1)
            else:  # Queenside
                rook_from = (from_row, 0)
                rook_to = (from_row, to_col + 1)
            
            # Move the rook
            self.board[rook_to[0]][rook_to[1]] = self.board[rook_from[0]][rook_from[1]]
            self.board[rook_from[0]][rook_from[1]] = Piece()
            self.board[rook_to[0]][rook_to[1]].has_moved = True
        
        # Update king position
        if piece.piece_type == PieceType.KING:
            if piece.color == Color.WHITE:
                self.white_king_pos = to_pos
            else:
                self.black_king_pos = to_pos
        
        # Move the piece
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = Piece()
        piece.has_moved = True
        
        # Handle pawn promotion
        if piece.piece_type == PieceType.PAWN and (to_row == 0 or to_row == 7):
            # Auto-promote to queen for now
            self.board[to_row][to_col] = Piece(PieceType.QUEEN, piece.color)
        
        # Switch player
        self.current_player = Color.BLACK if self.current_player == Color.WHITE else Color.WHITE
        
        # Check for checkmate or stalemate
        self.check_game_end()
        
        return True
    
    def undo_move(self):
        if not self.move_history:
            return False
        
        from_pos, to_pos, captured_piece, prev_en_passant = self.move_history.pop()
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Get the piece being moved back
        piece = self.board[to_row][to_col]
        
        # Handle castling
        if piece.piece_type == PieceType.KING and abs(to_col - from_col) == 2:
            # Determine rook positions based on castling side
            if to_col > from_col:  # Kingside
                rook_from = (from_row, to_col - 1)
                rook_to = (from_row, 7)
            else:  # Queenside
                rook_from = (from_row, to_col + 1)
                rook_to = (from_row, 0)
            
            # Move the rook back
            self.board[rook_to[0]][rook_to[1]] = self.board[rook_from[0]][rook_from[1]]
            self.board[rook_from[0]][rook_from[1]] = Piece()
            self.board[rook_to[0]][rook_to[1]].has_moved = False
        
        # Handle en passant
        if piece.piece_type == PieceType.PAWN and (to_col != from_col) and captured_piece.piece_type == PieceType.EMPTY:
            # This was an en passant capture, restore the captured pawn
            if piece.color == Color.WHITE:
                self.board[to_row + 1][to_col] = Piece(PieceType.PAWN, Color.BLACK)
                self.board[to_row + 1][to_col].has_moved = True
            else:
                self.board[to_row - 1][to_col] = Piece(PieceType.PAWN, Color.WHITE)
                self.board[to_row - 1][to_col].has_moved = True
        
        # Move the piece back
        self.board[from_row][from_col] = piece
        self.board[to_row][to_col] = captured_piece
        
        # Update king position
        if piece.piece_type == PieceType.KING:
            if piece.color == Color.WHITE:
                self.white_king_pos = from_pos
            else:
                self.black_king_pos = from_pos
        
        # Reset has_moved flag if this was the piece's first move
        if len(self.move_history) == 0 or self.move_history[-1][0] != from_pos:
            piece.has_moved = False
        
        # Restore en passant target
        self.en_passant_target = prev_en_passant
        
        # Switch player back
        self.current_player = Color.BLACK if self.current_player == Color.WHITE else Color.WHITE
        
        # Reset game_over status if we're undoing a terminal state
        self.game_over = False
        self.winner = None
        
        return True
    
    def get_valid_moves(self, position):
        row, col = position
        piece = self.board[row][col]
        
        if piece.piece_type == PieceType.EMPTY or piece.color != self.current_player:
            return []
        
        valid_moves = []
        
        # Get all possible moves based on piece type
        possible_moves = self.get_possible_moves(position)
        
        # Filter out moves that would leave the king in check
        for move in possible_moves:
            # Make a copy of the current state
            original_board = self.board.copy()
            original_current_player = self.current_player
            original_en_passant = self.en_passant_target
            original_white_king_pos = self.white_king_pos
            original_black_king_pos = self.black_king_pos
            
            # Make the move directly without validation
            from_row, from_col = position
            to_row, to_col = move
            
            # Move the piece
            self.board[to_row][to_col] = self.board[from_row][from_col]
            self.board[from_row][from_col] = Piece()
            
            # Update king position if needed
            if piece.piece_type == PieceType.KING:
                if piece.color == Color.WHITE:
                    self.white_king_pos = move
                else:
                    self.black_king_pos = move
            
            # Check if the king is in check
            if not self.is_check(piece.color):
                valid_moves.append(move)
            
            # Restore the original state
            self.board = original_board
            self.current_player = original_current_player
            self.en_passant_target = original_en_passant
            self.white_king_pos = original_white_king_pos
            self.black_king_pos = original_black_king_pos
        
        return valid_moves
    
    def get_possible_moves(self, position):
        row, col = position
        piece = self.board[row][col]
        moves = []
        
        if piece.piece_type == PieceType.PAWN:
            moves = self.get_pawn_moves(position)
        elif piece.piece_type == PieceType.KNIGHT:
            moves = self.get_knight_moves(position)
        elif piece.piece_type == PieceType.BISHOP:
            moves = self.get_bishop_moves(position)
        elif piece.piece_type == PieceType.ROOK:
            moves = self.get_rook_moves(position)
        elif piece.piece_type == PieceType.QUEEN:
            moves = self.get_queen_moves(position)
        elif piece.piece_type == PieceType.KING:
            moves = self.get_king_moves(position)
        
        return moves
    
    def get_pawn_moves(self, position):
        row, col = position
        piece = self.board[row][col]
        moves = []
        
        # Direction of movement depends on color
        direction = -1 if piece.color == Color.WHITE else 1
        
        # Move forward one square
        if 0 <= row + direction < 8 and self.board[row + direction][col].piece_type == PieceType.EMPTY:
            moves.append((row + direction, col))
            
            # Move forward two squares if it's the pawn's first move
            if not piece.has_moved and 0 <= row + 2 * direction < 8 and self.board[row + 2 * direction][col].piece_type == PieceType.EMPTY:
                moves.append((row + 2 * direction, col))
        
        # Capture diagonally
        for col_offset in [-1, 1]:
            capture_col = col + col_offset
            if 0 <= capture_col < 8 and 0 <= row + direction < 8:
                # Regular capture
                target = self.board[row + direction][capture_col]
                if target.piece_type != PieceType.EMPTY and target.color != piece.color:
                    moves.append((row + direction, capture_col))
                
                # En passant capture
                if self.en_passant_target == (row + direction, capture_col):
                    moves.append((row + direction, capture_col))
        
        return moves
    
    def get_knight_moves(self, position):
        row, col = position
        piece = self.board[row][col]
        moves = []
        
        # All possible knight moves
        offsets = [
            (-2, -1), (-2, 1),
            (-1, -2), (-1, 2),
            (1, -2), (1, 2),
            (2, -1), (2, 1)
        ]
        
        for offset_row, offset_col in offsets:
            new_row, new_col = row + offset_row, col + offset_col
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = self.board[new_row][new_col]
                if target.piece_type == PieceType.EMPTY or target.color != piece.color:
                    moves.append((new_row, new_col))
        
        return moves
    
    def get_bishop_moves(self, position):
        row, col = position
        piece = self.board[row][col]
        moves = []
        
        # Diagonal directions
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for direction_row, direction_col in directions:
            for distance in range(1, 8):
                new_row, new_col = row + direction_row * distance, col + direction_col * distance
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                
                target = self.board[new_row][new_col]
                if target.piece_type == PieceType.EMPTY:
                    moves.append((new_row, new_col))
                elif target.color != piece.color:
                    moves.append((new_row, new_col))
                    break
                else:
                    break
        
        return moves
    
    def get_rook_moves(self, position):
        row, col = position
        piece = self.board[row][col]
        moves = []
        
        # Horizontal and vertical directions
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for direction_row, direction_col in directions:
            for distance in range(1, 8):
                new_row, new_col = row + direction_row * distance, col + direction_col * distance
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                
                target = self.board[new_row][new_col]
                if target.piece_type == PieceType.EMPTY:
                    moves.append((new_row, new_col))
                elif target.color != piece.color:
                    moves.append((new_row, new_col))
                    break
                else:
                    break
        
        return moves
    
    def get_queen_moves(self, position):
        # Queen moves like a bishop and a rook combined
        return self.get_bishop_moves(position) + self.get_rook_moves(position)
    
    def get_king_moves(self, position):
        row, col = position
        piece = self.board[row][col]
        moves = []
        
        # Regular king moves (one square in any direction)
        for row_offset in range(-1, 2):
            for col_offset in range(-1, 2):
                if row_offset == 0 and col_offset == 0:
                    continue
                
                new_row, new_col = row + row_offset, col + col_offset
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    target = self.board[new_row][new_col]
                    if target.piece_type == PieceType.EMPTY or target.color != piece.color:
                        moves.append((new_row, new_col))
        
        # Castling
        if not piece.has_moved and not self.is_check(piece.color):
            # Kingside castling
            if (col + 3 < 8 and 
                self.board[row][col + 3].piece_type == PieceType.ROOK and 
                self.board[row][col + 3].color == piece.color and 
                not self.board[row][col + 3].has_moved and
                self.board[row][col + 1].piece_type == PieceType.EMPTY and 
                self.board[row][col + 2].piece_type == PieceType.EMPTY and
                not self.is_square_attacked((row, col + 1), piece.color) and
                not self.is_square_attacked((row, col + 2), piece.color)):
                moves.append((row, col + 2))
            
            # Queenside castling
            if (col - 4 >= 0 and 
                self.board[row][col - 4].piece_type == PieceType.ROOK and 
                self.board[row][col - 4].color == piece.color and 
                not self.board[row][col - 4].has_moved and
                self.board[row][col - 1].piece_type == PieceType.EMPTY and 
                self.board[row][col - 2].piece_type == PieceType.EMPTY and
                self.board[row][col - 3].piece_type == PieceType.EMPTY and
                not self.is_square_attacked((row, col - 1), piece.color) and
                not self.is_square_attacked((row, col - 2), piece.color)):
                moves.append((row, col - 2))
        
        return moves
    
    def is_valid_move(self, from_pos, to_pos):
        valid_moves = self.get_valid_moves(from_pos)
        return to_pos in valid_moves
    
    def is_square_attacked(self, position, color):
        row, col = position
        opponent_color = Color.BLACK if color == Color.WHITE else Color.WHITE
        
        # Check for pawn attacks
        pawn_direction = 1 if color == Color.WHITE else -1
        for col_offset in [-1, 1]:
            attack_row, attack_col = row + pawn_direction, col + col_offset
            if 0 <= attack_row < 8 and 0 <= attack_col < 8:
                attacker = self.board[attack_row][attack_col]
                if attacker.piece_type == PieceType.PAWN and attacker.color == opponent_color:
                    return True
        
        # Check for knight attacks
        knight_offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for offset_row, offset_col in knight_offsets:
            attack_row, attack_col = row + offset_row, col + offset_col
            if 0 <= attack_row < 8 and 0 <= attack_col < 8:
                attacker = self.board[attack_row][attack_col]
                if attacker.piece_type == PieceType.KNIGHT and attacker.color == opponent_color:
                    return True
        
        # Check for bishop/queen attacks (diagonals)
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for direction_row, direction_col in directions:
            for distance in range(1, 8):
                attack_row, attack_col = row + direction_row * distance, col + direction_col * distance
                if not (0 <= attack_row < 8 and 0 <= attack_col < 8):
                    break
                
                attacker = self.board[attack_row][attack_col]
                if attacker.piece_type != PieceType.EMPTY:
                    if (attacker.piece_type in [PieceType.BISHOP, PieceType.QUEEN] and 
                        attacker.color == opponent_color):
                        return True
                    break
        
        # Check for rook/queen attacks (horizontals and verticals)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for direction_row, direction_col in directions:
            for distance in range(1, 8):
                attack_row, attack_col = row + direction_row * distance, col + direction_col * distance
                if not (0 <= attack_row < 8 and 0 <= attack_col < 8):
                    break
                
                attacker = self.board[attack_row][attack_col]
                if attacker.piece_type != PieceType.EMPTY:
                    if (attacker.piece_type in [PieceType.ROOK, PieceType.QUEEN] and 
                        attacker.color == opponent_color):
                        return True
                    break
        
        # Check for king attacks (one square in any direction)
        for row_offset in range(-1, 2):
            for col_offset in range(-1, 2):
                if row_offset == 0 and col_offset == 0:
                    continue
                
                attack_row, attack_col = row + row_offset, col + col_offset
                if 0 <= attack_row < 8 and 0 <= attack_col < 8:
                    attacker = self.board[attack_row][attack_col]
                    if attacker.piece_type == PieceType.KING and attacker.color == opponent_color:
                        return True
        
        return False
    
    def is_check(self, color):
        king_pos = self.white_king_pos if color == Color.WHITE else self.black_king_pos
        return self.is_square_attacked(king_pos, color)
    
    def is_checkmate(self, color):
        if not self.is_check(color):
            return False
        
        # Check if there are any legal moves
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece.piece_type != PieceType.EMPTY and piece.color == color:
                    valid_moves = self.get_valid_moves((row, col))
                    if valid_moves:
                        return False
        
        return True
    
    def is_stalemate(self, color):
        if self.is_check(color):
            return False
        
        # Check if there are any legal moves
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece.piece_type != PieceType.EMPTY and piece.color == color:
                    valid_moves = self.get_valid_moves((row, col))
                    if valid_moves:
                        return False
        
        return True
    
    def check_game_end(self):
        if self.is_checkmate(self.current_player):
            self.game_over = True
            self.winner = Color.BLACK if self.current_player == Color.WHITE else Color.WHITE
            return True
        
        if self.is_stalemate(self.current_player):
            self.game_over = True
            self.winner = None  # Draw
            return True
        
        return False
    
    def get_all_valid_moves(self, color):
        moves = []
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece.piece_type != PieceType.EMPTY and piece.color == color:
                    valid_moves = self.get_valid_moves((row, col))
                    for move in valid_moves:
                        moves.append(((row, col), move))
        return moves
    
    def copy(self):
        new_game = ChessGame()
        new_game.board = np.array([[piece.copy() for piece in row] for row in self.board])
        new_game.current_player = self.current_player
        new_game.move_history = copy.deepcopy(self.move_history)
        new_game.en_passant_target = self.en_passant_target
        new_game.white_king_pos = self.white_king_pos
        new_game.black_king_pos = self.black_king_pos
        new_game.game_over = self.game_over
        new_game.winner = self.winner
        return new_game

class ChessAI:
    def __init__(self, color, depth=3):
        self.color = color
        self.depth = depth
        self.piece_values = {
            PieceType.PAWN: 100,
            PieceType.KNIGHT: 320,
            PieceType.BISHOP: 330,
            PieceType.ROOK: 500,
            PieceType.QUEEN: 900,
            PieceType.KING: 20000
        }
        
        # Position evaluation tables (same as before)
        self.pawn_table = [
            [0,  0,  0,  0,  0,  0,  0,  0],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [5,  5, 10, 25, 25, 10,  5,  5],
            [0,  0,  0, 20, 20,  0,  0,  0],
            [5, -5,-10,  0,  0,-10, -5,  5],
            [5, 10, 10,-20,-20, 10, 10,  5],
            [0,  0,  0,  0,  0,  0,  0,  0]
        ]
        
        self.knight_table = [
            [-50,-40,-30,-30,-30,-30,-40,-50],
            [-40,-20,  0,  0,  0,  0,-20,-40],
            [-30,  0, 10, 15, 15, 10,  0,-30],
            [-30,  5, 15, 20, 20, 15,  5,-30],
            [-30,  0, 15, 20, 20, 15,  0,-30],
            [-30,  5, 10, 15, 15, 10,  5,-30],
            [-40,-20,  0,  5,  5,  0,-20,-40],
            [-50,-40,-30,-30,-30,-30,-40,-50]
        ]
        
        self.bishop_table = [
            [-20,-10,-10,-10,-10,-10,-10,-20],
            [-10,  0,  0,  0,  0,  0,  0,-10],
            [-10,  0, 10, 10, 10, 10,  0,-10],
            [-10,  5,  5, 10, 10,  5,  5,-10],
            [-10,  0,  5, 10, 10,  5,  0,-10],
            [-10,  5,  5,  5,  5,  5,  5,-10],
            [-10,  0,  5,  0,  0,  5,  0,-10],
            [-20,-10,-10,-10,-10,-10,-10,-20]
        ]
        
        self.rook_table = [
            [0,  0,  0,  0,  0,  0,  0,  0],
            [5, 10, 10, 10, 10, 10, 10,  5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [0,  0,  0,  5,  5,  0,  0,  0]
        ]
        
        self.queen_table = [
            [-20,-10,-10, -5, -5,-10,-10,-20],
            [-10,  0,  0,  0,  0,  0,  0,-10],
            [-10,  0,  5,  5,  5,  5,  0,-10],
            [-5,  0,  5,  5,  5,  5,  0, -5],
            [0,  0,  5,  5,  5,  5,  0, -5],
            [-10,  5,  5,  5,  5,  5,  0,-10],
            [-10,  0,  5,  0,  0,  0,  0,-10],
            [-20,-10,-10, -5, -5,-10,-10,-20]
        ]
        
        self.king_table_middlegame = [
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-20,-30,-30,-40,-40,-30,-30,-20],
            [-10,-20,-20,-20,-20,-20,-20,-10],
            [20, 20,  0,  0,  0,  0, 20, 20],
            [20, 30, 10,  0,  0, 10, 30, 20]
        ]

    def evaluate_board(self, game):
        """
        Evaluate the current board position from the AI's perspective.
        Returns a score where positive values favor the AI.
        """
        score = 0
        
        # Material evaluation
        for row in range(8):
            for col in range(8):
                piece = game.board[row][col]
                if piece.piece_type != PieceType.EMPTY:
                    # Base piece value
                    piece_value = self.piece_values[piece.piece_type]
                    
                    # Positional value
                    if piece.color == Color.WHITE:
                        if piece.piece_type == PieceType.PAWN:
                            piece_value += self.pawn_table[row][col]
                        elif piece.piece_type == PieceType.KNIGHT:
                            piece_value += self.knight_table[row][col]
                        elif piece.piece_type == PieceType.BISHOP:
                            piece_value += self.bishop_table[row][col]
                        elif piece.piece_type == PieceType.ROOK:
                            piece_value += self.rook_table[row][col]
                        elif piece.piece_type == PieceType.QUEEN:
                            piece_value += self.queen_table[row][col]
                        elif piece.piece_type == PieceType.KING:
                            piece_value += self.king_table_middlegame[row][col]
                    else:  # Black pieces (tables are symmetric for black)
                        if piece.piece_type == PieceType.PAWN:
                            piece_value += self.pawn_table[7-row][col]
                        elif piece.piece_type == PieceType.KNIGHT:
                            piece_value += self.knight_table[7-row][col]
                        elif piece.piece_type == PieceType.BISHOP:
                            piece_value += self.bishop_table[7-row][col]
                        elif piece.piece_type == PieceType.ROOK:
                            piece_value += self.rook_table[7-row][col]
                        elif piece.piece_type == PieceType.QUEEN:
                            piece_value += self.queen_table[7-row][col]
                        elif piece.piece_type == PieceType.KING:
                            piece_value += self.king_table_middlegame[7-row][col]
                    
                    # Add or subtract based on color
                    if piece.color == self.color:
                        score += piece_value
                    else:
                        score -= piece_value
        
        # Mobility evaluation (number of legal moves)
        ai_moves = len(game.get_all_valid_moves(self.color))
        opponent_color = Color.BLACK if self.color == Color.WHITE else Color.WHITE
        opponent_moves = len(game.get_all_valid_moves(opponent_color))
        score += (ai_moves - opponent_moves) * 0.1  # Small weight for mobility
        
        # King safety (simple version - penalize being in check)
        if game.is_check(self.color):
            score -= 50
        if game.is_check(opponent_color):
            score += 50
            
        return score

    def get_best_move(self, game):
        """
        Returns the best move for the AI using min-max with alpha-beta pruning.
        Returns a tuple of (from_pos, to_pos).
        """
        best_move = None
        best_value = -float('inf')
        alpha = -float('inf')
        beta = float('inf')
        
        # Get all possible moves
        possible_moves = game.get_all_valid_moves(self.color)
        
        # Try each move and evaluate it
        for move in possible_moves:
            from_pos, to_pos = move
            game_copy = game.copy()
            game_copy.make_move(from_pos, to_pos)
            
            # Perform min-max search
            move_value = self.minimax(game_copy, self.depth - 1, alpha, beta, False)
            
            # Update best move if this one is better
            if move_value > best_value:
                best_value = move_value
                best_move = move
            
            # Update alpha
            alpha = max(alpha, best_value)
            
            # Alpha-beta pruning
            if beta <= alpha:
                break
        
        return best_move

    def minimax(self, game, depth, alpha, beta, maximizing_player):
        """
        Min-max algorithm with alpha-beta pruning.
        Returns the evaluation of the position.
        """
        # Base case: return evaluation if we've reached max depth or game is over
        if depth == 0 or game.game_over:
            return self.evaluate_board(game)
        
        if maximizing_player:
            max_eval = -float('inf')
            for move in game.get_all_valid_moves(self.color):
                from_pos, to_pos = move
                game_copy = game.copy()
                game_copy.make_move(from_pos, to_pos)
                
                eval = self.minimax(game_copy, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                
                # Alpha-beta pruning
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            
            return max_eval
        else:
            min_eval = float('inf')
            opponent_color = Color.BLACK if self.color == Color.WHITE else Color.WHITE
            for move in game.get_all_valid_moves(opponent_color):
                from_pos, to_pos = move
                game_copy = game.copy()
                game_copy.make_move(from_pos, to_pos)
                
                eval = self.minimax(game_copy, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                
                # Alpha-beta pruning
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            
            return min_eval