import pygame
import os
from Chess import Piece, Color, PieceType, ChessAI

class ChessGUI:
    def __init__(self, game):
        pygame.init()
        self.game = game
        self.square_size = 80
        self.width = 8 * self.square_size
        self.height = 8 * self.square_size
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Chess Game")
        self.load_images()
        self.selected_piece = None
        self.valid_moves = []
        self.font = pygame.font.SysFont('Arial', 24)
        self.ai_thinking = False
        self.ai = ChessAI(Color.BLACK, depth=3)
        self.last_ai_check_time = 0
        self.ai_check_delay = 100  # milliseconds
        
    def load_images(self):
        self.piece_images = {}
        white_pieces = ['P', 'N', 'B', 'R', 'Q', 'K']
        black_pieces = ['p', 'n', 'b', 'r', 'q', 'k']
        
        # Create images directory if it doesn't exist
        if not os.path.exists('images'):
            print("Creating images directory...")
            os.makedirs('images')
        
        # Load white pieces (uppercase)
        for piece in white_pieces:
            try:
                image_path = f"images/{piece}.png"
                if os.path.exists(image_path):
                    print(f"Loading image for white piece {piece} from {image_path}")
                    self.piece_images[piece] = pygame.transform.scale(
                        pygame.image.load(image_path),
                        (self.square_size, self.square_size))
                else:
                    print(f"No image found for white piece {piece}, using fallback")
                    surf = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
                    pygame.draw.circle(surf, (255, 255, 255), 
                                     (self.square_size//2, self.square_size//2),
                                     self.square_size//3)
                    self.piece_images[piece] = surf
            except Exception as e:
                print(f"Error loading image for white piece {piece}: {e}")
                surf = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
                pygame.draw.circle(surf, (255, 255, 255), 
                                 (self.square_size//2, self.square_size//2),
                                 self.square_size//3)
                self.piece_images[piece] = surf
        
        # Load black pieces (lowercase with (2))
        for piece in black_pieces:
            try:
                image_path = f"images/{piece} (2).png"  # Note the space and (2)
                if os.path.exists(image_path):
                    print(f"Loading image for black piece {piece} from {image_path}")
                    self.piece_images[piece] = pygame.transform.scale(
                        pygame.image.load(image_path),
                        (self.square_size, self.square_size))
                else:
                    print(f"No image found for black piece {piece}, using fallback")
                    surf = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
                    pygame.draw.circle(surf, (0, 0, 0), 
                                     (self.square_size//2, self.square_size//2),
                                     self.square_size//3)
                    self.piece_images[piece] = surf
            except Exception as e:
                print(f"Error loading image for black piece {piece}: {e}")
                surf = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
                pygame.draw.circle(surf, (0, 0, 0), 
                                 (self.square_size//2, self.square_size//2),
                                 self.square_size//3)
                self.piece_images[piece] = surf

    def draw_board(self):
        light = (240, 217, 181)
        dark = (181, 136, 99)
        highlight = (247, 247, 105, 150)
        move_highlight = (106, 168, 79, 150)
        
        # Draw the board squares
        for row in range(8):
            for col in range(8):
                # Draw square
                color = light if (row + col) % 2 == 0 else dark
                pygame.draw.rect(self.screen, color,
                               pygame.Rect(col * self.square_size,
                                         row * self.square_size,
                                         self.square_size,
                                         self.square_size))
                
                # Highlight selected piece
                if self.selected_piece and self.selected_piece == (row, col):
                    s = pygame.Surface((self.square_size, self.square_size))
                    s.set_alpha(150)
                    s.fill(highlight)
                    self.screen.blit(s, (col * self.square_size, row * self.square_size))
                
                # Highlight valid moves
                if (row, col) in self.valid_moves:
                    s = pygame.Surface((self.square_size, self.square_size))
                    s.set_alpha(150)
                    s.fill(move_highlight)
                    self.screen.blit(s, (col * self.square_size, row * self.square_size))
                
                # Draw pieces
                piece = self.game.board[row][col]
                if piece.piece_type != PieceType.EMPTY:
                    piece_str = str(piece)  # This will return the correct character (e.g., 'P' for white pawn, 'p' for black pawn)
                    if piece_str in self.piece_images:
                        self.screen.blit(self.piece_images[piece_str], 
                                       (col * self.square_size, row * self.square_size))
        
        # Draw game status
        status = ""
        if self.game.game_over:
            if self.game.winner:
                status = f"{self.game.winner.name} wins!"
            else:
                status = "Game ended in a draw"
        else:
            status = f"{self.game.current_player.name}'s turn"
        
        text = self.font.render(status, True, (0, 0, 0))
        self.screen.blit(text, (10, 10))

    def square_under_mouse(self, pos):
        x, y = pos
        row = y // self.square_size
        col = x // self.square_size
        if 0 <= row < 8 and 0 <= col < 8:
            return (row, col)
        return None

    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            current_time = pygame.time.get_ticks()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Handle mouse input for White's moves
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                    if self.game.current_player == Color.WHITE:  # Only process clicks during White's turn
                        pos = pygame.mouse.get_pos()
                        square = self.square_under_mouse(pos)
                        print(f"Clicked square: {square}")  # Debug print
                        
                        if square:
                            row, col = square
                            piece = self.game.board[row][col]
                            print(f"Piece at clicked square: {piece}, Color: {piece.color}")  # Debug print
                            
                            # If we've already selected a piece
                            if self.selected_piece:
                                from_row, from_col = self.selected_piece
                                # Try to move if the target square is a valid move
                                if (row, col) in self.valid_moves:
                                    print(f"Moving piece from {self.selected_piece} to {square}")  # Debug print
                                    if self.game.make_move((from_row, from_col), (row, col)):
                                        self.selected_piece = None
                                        self.valid_moves = []
                                # Otherwise, try to select a new piece
                                elif piece.color == Color.WHITE:
                                    print(f"Selecting new white piece at {square}")  # Debug print
                                    self.selected_piece = (row, col)
                                    self.valid_moves = self.game.get_valid_moves((row, col))
                                    print(f"Valid moves: {self.valid_moves}")  # Debug print
                                else:
                                    self.selected_piece = None
                                    self.valid_moves = []
                            # No piece is selected yet
                            elif piece.color == Color.WHITE:
                                print(f"Selecting white piece at {square}")  # Debug print
                                self.selected_piece = (row, col)
                                self.valid_moves = self.game.get_valid_moves((row, col))
                                print(f"Valid moves: {self.valid_moves}")  # Debug print
            
            # Process AI move if it's Black's turn (with delay)
            if (self.game.current_player == Color.BLACK and 
                not self.game.game_over and 
                not self.ai_thinking and 
                current_time - self.last_ai_check_time >= self.ai_check_delay):
                
                self.ai_thinking = True
                print("AI thinking...")  # Debug print
                best_move = self.ai.get_best_move(self.game)
                if best_move:
                    from_pos, to_pos = best_move
                    print(f"AI moving from {from_pos} to {to_pos}")  # Debug print
                    self.game.make_move(from_pos, to_pos)
                else:
                    print("AI couldn't find a move")  # Debug print
                self.ai_thinking = False
                self.last_ai_check_time = current_time
            
            self.screen.fill((0, 0, 0))
            self.draw_board()
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()