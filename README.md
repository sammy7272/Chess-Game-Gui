# Chess Game with AI Opponent

A Python-based chess game featuring a graphical user interface (GUI) and an AI opponent. Built using Pygame, this application allows users to play chess against a computer opponent with a clean and intuitive interface.

## Features

- 🎮 Interactive GUI built with Pygame
- 🤖 AI opponent with move prediction
- 🎨 Clean and intuitive user interface
- ♟️ Standard chess rules implementation
- 🖱️ Mouse-based piece movement
- 🎯 Valid move highlighting
- 🏆 Win/loss detection

## Requirements

- Python 3.x
- Pygame 2.6.1 or later

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Chess-Game-Gui.git
cd Chess-Game-Gui
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install the required packages:
```bash
pip install pygame
```

## How to Play

1. Run the game:
```bash
python main.py
```

2. Game Controls:
- Click on a piece to select it
- Valid moves will be highlighted
- Click on a highlighted square to move the piece
- The AI will automatically make its move after you complete yours

## Project Structure

- `main.py` - Entry point of the application
- `chess_gui.py` - GUI implementation using Pygame
- `Chess.py` - Core chess game logic and AI implementation
- `images/` - Directory containing chess piece sprites

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details.
