import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import json
import os
from datetime import datetime, timedelta

TOKEN = os.getenv("DISCORD_TOKEN")
DATA_FILE = "reminders.json"

# ================= НАСТРОЙКА ВРЕМЕНИ =================
# 🔧 ТЕСТ
REMINDER_DELAY = timedelta(seconds=10)

# 🔁 ПРОД (ВЕРНУТЬ ПОСЛЕ ТЕСТОВ)
# REMINDER_DELAY = timedelta(hours=24)
# ====================================================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ================= DATA =================

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

reminders = load_data()

# ================= REMINDER TASK =================

async def reminder_task(user_id: int):
    data = reminders.get(str(user_id))
    if not data or not data.get("active"):
        return

    next_time = datetime.fromisoformat(data["next_time"])
    wait_seconds = (next_time - datetime.utcnow()).total_seconds()

    if wait_seconds > 0:
        await asyncio.sleep(wait_seconds)

    user = bot.get_user(user_id)
    if not user:
        return

    embed = discord.Embed(
        title="⏰ Напоминание",
        description=(
            "Вы не забыли сделать **ежедневную отметку**?\n\n"
            "Хотите продолжить напоминания?"
        ),
        color=discord.Color.orange()
    )

    await user.send(embed=embed, view=ContinueMarkView(user_id))

# ================= VIEWS =================

class MarkSetupView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=60)
        self.user_id = user_id

    @discord.ui.button(label="Да", style=discord.ButtonStyle.green)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="❓ **Вы сегодня отмечались?**",
            view=MarkTodayView(self.user_id)
        )

    @discord.ui.button(label="Нет", style=discord.ButtonStyle.red)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="Хорошо, напоминание не установлено.",
            view=None
        )

class MarkTodayView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=60)
        self.user_id = user_id

    @discord.ui.button(label="Да", style=discord.ButtonStyle.green)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        next_time = datetime.utcnow() + REMINDER_DELAY

        reminders[str(self.user_id)] = {
            "active": True,
            "next_time": next_time.isoformat()
        }
        save_data(reminders)

        bot.loop.create_task(reminder_task(self.user_id))

        embed = discord.Embed(
            title="✅ Метка установлена",
            description=f"Следующее напоминание через **{int(REMINDER_DELAY.total_seconds())} сек.**",
            color=discord.Color.green()
        )

        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="Нет", style=discord.ButtonStyle.red)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="Хорошо 🙂 Не забудьте отметиться позже.",
            view=None
        )

class ContinueMarkView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.button(label="Да", style=discord.ButtonStyle.green)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        next_time = datetime.utcnow() + REMINDER_DELAY
        reminders[str(self.user_id)]["next_time"] = next_time.isoformat()
        save_data(reminders)

        bot.loop.create_task(reminder_task(self.user_id))

        embed = discord.Embed(
            title="⏱ Продлено",
            description="Напоминание продлено.",
            color=discord.Color.green()
        )

        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="Нет", style=discord.ButtonStyle.red)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        reminders[str(self.user_id)]["active"] = False
        save_data(reminders)

        embed = discord.Embed(
            title="❌ Отключено",
            description="Напоминание отключено.",
            color=discord.Color.red()
        )

        await interaction.response.edit_message(embed=embed, view=None)

class DisableMarkView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=60)
        self.user_id = user_id

    @discord.ui.button(label="Да", style=discord.ButtonStyle.red)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        reminders[str(self.user_id)]["active"] = False
        save_data(reminders)

        embed = discord.Embed(
            title="❌ Метка отключена",
            description="Ежедневные напоминания отключены.",
            color=discord.Color.red()
        )

        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="Нет", style=discord.ButtonStyle.green)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="ℹ Без изменений",
            description="Напоминание остаётся активным.",
            color=discord.Color.green()
        )

        await interaction.response.edit_message(embed=embed, view=None)

# ================= READY =================

@bot.event
async def on_ready():
    print(f"Бот запущен как {bot.user}")
    await bot.tree.sync()

    for user_id, data in reminders.items():
        if data.get("active"):
            bot.loop.create_task(reminder_task(int(user_id)))

# ================= HELP =================

@bot.tree.command(name="help", description="Информация о доступных командах")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="ℹ️ Помощь",
        description=(
            f"👋 **Привет, {interaction.user.mention}!**\n\n"
            "**Доступные команды:**\n"
            "• `/calculation` — экономический расчёт\n"
            "• `/mark` — ежедневные отметки"
        ),
        color=discord.Color.blurple()
    )

    embed.set_footer(text="Arknights Endfield • Help")
    await interaction.response.send_message(embed=embed)

# ================= CALCULATION =================

@bot.tree.command(name="calculation", description="Сравнение выгодности двух товаров")
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
        await interaction.response.send_message(":x: Количество должно быть больше 0", ephemeral=True)
        return

    profit_a = (sale_a - price_a) * quantity
    profit_b = (sale_b - price_b) * quantity

    better = "A" if profit_a > profit_b else "B" if profit_b > profit_a else "Одинаково"

    embed = discord.Embed(
        title="📊 Результаты расчёта",
        description=f"**Выгоднее:** {better}",
        color=discord.Color.green()
    )

    embed.add_field(name="🅰️ Товар A", value=f"Прибыль: `{profit_a}`", inline=False)
    embed.add_field(name="🅱️ Товар B", value=f"Прибыль: `{profit_b}`", inline=False)

    await interaction.response.send_message(embed=embed)

# ================= MARK =================

@bot.tree.command(name="mark", description="Ежедневные отметки")
async def mark(interaction: discord.Interaction):
    user_id = str(interaction.user.id)

    if user_id in reminders and reminders[user_id].get("active"):
        embed = discord.Embed(
            title="📌 Метка уже установлена",
            description="Вы уже поставили метку.\nХотите отключить?",
            color=discord.Color.orange()
        )

        await interaction.response.send_message(
            embed=embed,
            view=DisableMarkView(interaction.user.id),
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title="📌 Установка метки",
        description="Вы хотите установить напоминание о ежедневных отметках?",
        color=discord.Color.blurple()
    )

    await interaction.response.send_message(
        embed=embed,
        view=MarkSetupView(interaction.user.id),
        ephemeral=True
    )

bot.run(TOKEN)
