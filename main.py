from Chess import ChessGame
from chess_gui import ChessGUI

if __name__ == "__main__":
    game = ChessGame()
    gui = ChessGUI(game)
    gui.run()