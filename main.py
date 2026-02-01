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


# ---------- HELP ----------
@bot.tree.command(
    name="help",
    description="Информация о доступных командах"
)
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title=":information_source: Помощь",
        description=(
            f":wave: **Доброго времени суток, {interaction.user.mention}!**\n\n"
            "На данный момент вы можете использовать **одну команду**:\n"
            "**`/calculation`** — расчёт выгодности товаров.\n\n"
            "**Как правильно использовать команду:**\n"
            "```⁩\n"
            "/calculation\n"
            "Цена товара A: 10\n"
            "Цена продажи товара A: 15\n"
            "Цена товара B: 12\n"
            "Цена продажи товара B: 16\n"
            "Количество для продажи: 320\n"
            "⁨```\n"
            "Я автоматически посчитаю прибыль и покажу, "
            "какой вариант будет выгоднее - если сами не можете решить."
        ),
        color=discord.Color.blurple()
    )

    embed.set_footer(text="Arknights Endfield • Help")

    await interaction.response.send_message(embed=embed)


# ---------- CALCULATION ----------
@bot.tree.command(
    name="calculation",
    description="Сравнение выгодности двух товаров"
)
@app_commands.describe(
    price_a="Цена товара A",
    sale_a="Цена продажи товара A",
    price_b="Цена товара B",
    sale_b="Цена продажи товара B",
    quantity="Количество для продажи"
)
async def calculation(
    interaction: discord.Interaction,
    price_a: float,
    sale_a: float,
    price_b: float,
    sale_b: float,
    quantity: int
):
    if quantity <= 0:
        await interaction.response.send_message(
            ":x: Количество должно быть больше 0",
            ephemeral=True
        )
        return

    profit_a = sale_a - price_a
    profit_b = sale_b - price_b

    total_sale_a = sale_a * quantity
    total_sale_b = sale_b * quantity

    total_profit_a = profit_a * quantity
    total_profit_b = profit_b * quantity

    if total_profit_a > total_profit_b:
        result = f":white_check_mark: Выгоднее вариант **A** (за {quantity} шт.)"
        color = discord.Color.green()
    elif total_profit_b > total_profit_a:
        result = f":white_check_mark: Выгоднее вариант **B** (за {quantity} шт.)"
        color = discord.Color.blue()
    else:
        result = f":scales: Оба варианта одинаково выгодны (за {quantity} шт.)"
        color = discord.Color.light_grey()

    embed = discord.Embed(
        title=":bar_chart: Результаты расчёта",
        description=result,
        color=color
    )

    embed.add_field(
        name=":a: Товар A",
        value=(
            f"Цена товара: `{price_a}`\n"
            f"Цена продажи: `{sale_a}`\n"
            f"Прибыль за 1: `{profit_a}`\n"
            f"Продажа за {quantity}: `{total_sale_a}`\n"
            f"Прибыль за {quantity}: `{total_profit_a}`"
        ),
        inline=False
    )

    embed.add_field(
        name=":b: Товар B",
        value=(
            f"Цена товара: `{price_b}`\n"
            f"Цена продажи: `{sale_b}`\n"
            f"Прибыль за 1: `{profit_b}`\n"
            f"Продажа за {quantity}: `{total_sale_b}`\n"
            f"Прибыль за {quantity}: `{total_profit_b}`"
        ),
        inline=False
    )

    embed.set_footer(text="Arknights Endfield • Экономический расчёт")

    await interaction.response.send_message(embed=embed)


bot.run(TOKEN)
