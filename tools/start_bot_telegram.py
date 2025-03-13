import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.bot_telegram import BotFather

bot = BotFather()
bot.start_bot()
