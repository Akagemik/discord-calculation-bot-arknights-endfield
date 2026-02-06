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
        title="ℹ️ Помощь",
        description=(
            f"👋 **Доброго времени суток, {interaction.user.mention}!**\n\n"
            "На данный момент вы можете использовать следующие команды:\n\n"

            "🔹 **`/calculation`** — расчёт выгодности товаров.\n"
            "Используется для сравнения прибыли между двумя товарами.\n\n"
            "**Пример использования:**\n"
            "```\n"
            "/calculation\n"
            "Цена товара A: 10\n"
            "Цена продажи товара A: 15\n"
            "Цена товара B: 12\n"
            "Цена продажи товара B: 16\n"
            "Количество для продажи: 320\n"
            "```\n\n"

            "🎮 **`/gachi`** — меню выбора гачи.\n"
            "Позволяет выбрать одну из доступных гач:\n"
            "• Arknights: Endfield\n"
            "• Zenless Zone Zero\n"
            "• Genshin Impact\n\n"
            "⚠️ На данный момент находятся **в разработке**."
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
            "❌ Количество должно быть больше 0",
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
        result = f"✅ Выгоднее вариант **A** (за {quantity} шт.)"
        color = discord.Color.green()
    elif total_profit_b > total_profit_a:
        result = f"✅ Выгоднее вариант **B** (за {quantity} шт.)"
        color = discord.Color.blue()
    else:
        result = f"⚖️ Оба варианта одинаково выгодны (за {quantity} шт.)"
        color = discord.Color.light_grey()

    embed = discord.Embed(
        title="📊 Результаты расчёта",
        description=result,
        color=color
    )

    embed.add_field(
        name="🅰️ Товар A",
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
        name="🅱️ Товар B",
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

# ================== /gachi ==================

# ================== ЦВЕТА ==================

COLOR_MAIN = discord.Color.blurple()
COLOR_DEV = discord.Color.orange()

# ================== VIEW С КНОПКАМИ ==================

class GachiView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    async def in_dev(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🚧 В разработке",
            description="Данный режим ещё находится в разработке.\nСледите за обновлениями!",
            color=COLOR_DEV
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Arknights: Endfield", style=discord.ButtonStyle.primary)
    async def arknights(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.in_dev(interaction)

    @discord.ui.button(label="Zenless Zone Zero", style=discord.ButtonStyle.primary)
    async def zzz(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.in_dev(interaction)

    @discord.ui.button(label="Genshin Impact", style=discord.ButtonStyle.primary)
    async def genshin(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.in_dev(interaction)

# ================== SLASH-КОМАНДА ==================

@bot.tree.command(name="gachi", description="Выбор гачи")
async def gachi(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎮 Выбор гачи",
        description="Выберите одну из гачи, нажав на соответствующую кнопку:",
        color=COLOR_MAIN
    )
    embed.set_footer(text="")

    await interaction.response.send_message(
        embed=embed,
        view=GachiView()
    )

bot.run(TOKEN)
