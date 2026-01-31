import discord
from discord import app_commands
from discord.ext import commands
import os

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Бот запущен как {bot.user}")
    await bot.tree.sync()


@bot.tree.command(
    name="calculation",
    description="Сравнение выгодности двух товаров"
)
@app_commands.describe(
    price_a="Цена товара A",
    sale_a="Цена продажи товара A",
    price_b="Цена товара B",
    sale_b="Цена продажи товара B"
)
async def calculation(
    interaction: discord.Interaction,
    price_a: float,
    sale_a: float,
    price_b: float,
    sale_b: float
):
    profit_a = sale_a - price_a
    profit_b = sale_b - price_b

    if profit_a > profit_b:
        result = "✅ **Выгоднее вариант A**"
    elif profit_b > profit_a:
        result = "✅ **Выгоднее вариант B**"
    else:
        result = "⚖️ **Оба варианта одинаково выгодны**"

    response = (
        f"📊 **Результаты расчёта:**\n\n"
        f"**Товар A**\n"
        f"Цена товара: {price_a}\n"
        f"Цена продажи: {sale_a}\n"
        f"Прибыль: **{profit_a}**\n\n"
        f"**Товар B**\n"
        f"Цена товара: {price_b}\n"
        f"Цена продажи: {sale_b}\n"
        f"Прибыль: **{profit_b}**\n\n"
        f"{result}"
    )

    await interaction.response.send_message(response)

bot.run(TOKEN)
