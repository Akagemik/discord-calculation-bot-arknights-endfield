import discord
from discord import app_commands
from discord.ext import commands
import os

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Бот запущен как {bot.user}")
    await bot.tree.sync()

@bot.tree.command(name="calculation", description="Сравнение выгодности товаров")
@app_commands.describe(
    price_a="Цена товара A",
    sale_a="Цена продажи товара A",
    price_b="Цена товара B",
    sale_b="Цена продажи товара B"
)
async def calculation(interaction: discord.Interaction,
    price_a: float,
    sale_a: float,
    price_b: float,
    sale_b: float):

    profit_a = sale_a - price_a
    profit_b = sale_b - price_b

    result = (
        "✅ Выгоднее вариант A" if profit_a > profit_b else
        "✅ Выгоднее вариант B" if profit_b > profit_a else
        "⚖️ Оба варианта одинаковы"
    )

    await interaction.response.send_message(
        f"Товар A: прибыль {profit_a}\n"
        f"Товар B: прибыль {profit_b}\n\n"
        f"{result}"
    )

bot.run(TOKEN)
