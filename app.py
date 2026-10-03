import os
import random
import threading

from flask import Flask, jsonify, render_template_string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

app = Flask(__name__)

balance = 12500
earned_today = 1850
tasks = 7

HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>MoneyHelp DEMO</title>
<style>
body {
    margin:0;
    background:#f3f4f6;
    font-family:Arial,sans-serif;
    color:#111827;
}
.header {
    background:#111827;
    color:white;
    padding:20px;
    text-align:center;
    font-size:24px;
    font-weight:bold;
}
.demo {
    background:#f59e0b;
    padding:10px;
    text-align:center;
    font-weight:bold;
}
.container {
    max-width:500px;
    margin:25px auto;
    padding:15px;
}
.card {
    background:white;
    border-radius:18px;
    padding:22px;
    margin-bottom:15px;
    box-shadow:0 4px 15px #0001;
}
.balance {
    font-size:40px;
    font-weight:bold;
    margin:10px 0;
}
.grid {
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:12px;
}
.stat {
    background:#f3f4f6;
    padding:18px;
    border-radius:14px;
}
button {
    width:100%;
    padding:15px;
    border:0;
    border-radius:12px;
    background:#111827;
    color:white;
    font-size:16px;
}
button:disabled {
    opacity:.5;
}
.small {
    color:#6b7280;
    font-size:13px;
}
</style>
</head>

<body>

<div class="header">MoneyHelp</div>

<div class="demo">
ДЕМО • ВИРТУАЛЬНЫЕ ДЕНЬГИ • РЕАЛЬНЫХ ВЫПЛАТ НЕТ
</div>

<div class="container">

<div class="card">
<div class="small">Виртуальный баланс</div>
<div class="balance">
<span id="balance">{{balance}}</span> ₸
</div>
<div class="small">
Баланс используется только для демонстрации.
</div>
</div>

<div class="grid">

<div class="stat">
<b id="today">{{today}}</b> ₸
<br>
<span class="small">заработано сегодня</span>
</div>

<div class="stat">
<b id="tasks">{{tasks}}</b>
<br>
<span class="small">выполнено заданий</span>
</div>

</div>

<div class="card">

<h3>Демо-задание</h3>

<p>
Выполните виртуальное задание и получите случайное
демонстрационное вознаграждение.
</p>

<button onclick="task()">
Выполнить задание
</button>

</div>

<div class="card">

<h3>Вывод средств</h3>

<p class="small">
В демонстрационной версии реальные выплаты отключены.
</p>

<button disabled>
Вывести деньги
</button>

</div>

</div>

<script>

async function task() {

    const response = await fetch(
        "/api/task",
        {method:"POST"}
    );

    const data = await response.json();

    document.getElementById("balance").innerText =
        data.balance;

    document.getElementById("today").innerText =
        data.today;

    document.getElementById("tasks").innerText =
        data.tasks;

    alert(
        "Демо-вознаграждение: +" +
        data.reward +
        " ₸"
    );
}

</script>

</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(
        HTML,
        balance=balance,
        today=earned_today,
        tasks=tasks
    )


@app.post("/api/task")
def task():

    global balance
    global earned_today
    global tasks

    reward = random.randint(100, 500)

    balance += reward
    earned_today += reward
    tasks += 1

    return jsonify({
        "balance": balance,
        "today": earned_today,
        "tasks": tasks,
        "reward": reward
    })


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    web_url = os.getenv("WEBAPP_URL")

    buttons = []

    if web_url:
        buttons.append([
            InlineKeyboardButton(
                "📱 Открыть DEMO",
                url=web_url
            )
        ])

    await update.message.reply_text(
        "🟡 MoneyHelp DEMO\n\n"
        "Учебная имитация заработка.\n\n"
        "Все деньги виртуальные. "
        "Реальных депозитов и выплат нет.",
        reply_markup=(
            InlineKeyboardMarkup(buttons)
            if buttons else None
        )
    )


async def balance_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        f"💰 DEMO-баланс: {balance:,} ₸\n\n"
        "Это виртуальный баланс."
    )


def run_bot():

    token = os.getenv("BOT_TOKEN")

    if not token:
        print("BOT_TOKEN не установлен.")
        return

    telegram_app = (
        Application
        .builder()
        .token(token)
        .build()
    )

    telegram_app.add_handler(
        CommandHandler("start", start)
    )

    telegram_app.add_handler(
        CommandHandler(
            "balance",
            balance_command
        )
    )

    telegram_app.run_polling()


if __name__ == "__main__":

    bot_thread = threading.Thread(
        target=run_bot,
        daemon=True
    )

    bot_thread.start()

    port = int(
        os.getenv("PORT", "10000")
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
