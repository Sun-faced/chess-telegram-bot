
# Chess Telegram Bot

A Telegram bot integrated with the Lichess API for automating game-related tasks. The bot utilizes a local SQLite database to track and manage game results.

## Features
- Create Blitz(3 + 0) and Bullet (2 + 1) chess games
- Track wins, losses, and draws
- Leaderboards

## Installation

### **Method 1: Using pip**
```bash
git clone https://github.com/Sun-faced/chess-telegram-bot
cd chess-telegram-bot
pip install -r requirements.txt
```

### **Method 2: Using Poetry**
```bash
git clone https://github.com/Sun-faced/chess-telegram-bot
cd chess-telegram-bot
poetry install
poetry shell
```
## After Installation

You will have to edit `constants.py` to assign your own name for bot and Telegram bot token.