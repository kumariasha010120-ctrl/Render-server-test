import logging
import psutil
import platform
import time
import threading
import speedtest
import os
import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

# --- CONFIG ---
TOKEN = "8715339019:AAGplme4-3WhfQzZAIzcpMzJ8gBY6dwXE84"
START_TIME = time.time()

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- UTILS ---
def get_uptime():
    delta = time.time() - START_TIME
    h, r = divmod(int(delta), 3600)
    m, s = divmod(r, 60)
    return f"{h}h {m}m {s}s"

def get_size(bytes):
    for unit in ['', 'K', 'M', 'G', 'T']:
        if bytes < 1024: return f"{bytes:.2f}{unit}B"
        bytes /= 1024

# --- 🌐 WEB JSON INTERFACE (Render Success Logic) ---
class JsonHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        data = {
            "status": "Online",
            "server": "Render Paid Tier",
            "uptime": get_uptime(),
            "cpu": f"{psutil.cpu_percent()}%",
            "ram": f"{psutil.virtual_memory().percent}%",
            "dev": "Adarsh"
        }
        self.wfile.write(json.dumps(data, indent=4).encode())

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), JsonHandler)
    server.serve_forever()

# --- ⌨️ KEYBOARDS (UI DESIGN) ---
def main_menu():
    keyboard = [
        [InlineKeyboardButton("📊 System Stats", callback_data='stats'),
         InlineKeyboardButton("🚀 Speed Test", callback_data='speed')],
        [InlineKeyboardButton("💻 HW Specs", callback_data='hw'),
         InlineKeyboardButton("🛠️ Commands", callback_data='cmds')],
        [InlineKeyboardButton("🌐 My API Site", url="https://info-test-1.onrender.com")]
    ]
    return InlineKeyboardMarkup(keyboard)

def back_btn():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back to Menu", callback_data='home')]])

# --- 🎮 HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👑 **ELITE RENDER BOT V3**\n\n"
        f"Hello {update.effective_user.first_name}!\n"
        "Main aapka professional AI assistant hoon.\n\n"
        "🟢 **Status:** Active\n"
        "🔵 **Server:** Render Singapore\n"
        "🟡 **Mode:** Subscription Paid"
    )
    await update.message.reply_text(text, reply_markup=main_menu(), parse_mode='Markdown')

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ram = psutil.virtual_memory()
    text = (
        "📊 **LIVE SERVER METRICS**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"⏱️ **Uptime:** {get_uptime()}\n"
        f"🧠 **RAM:** {ram.percent}% ({get_size(ram.used)}/{get_size(ram.total)})\n"
        f"🔥 **CPU Usage:** {psutil.cpu_percent()}%\n"
        f"📁 **Disk:** {psutil.disk_usage('/').percent}% Used\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )
    if update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=back_btn(), parse_mode='Markdown')
    else:
        await update.message.reply_text(text, parse_mode='Markdown')

async def speed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    msg = await query.message.edit_text("⚡ *Measuring Speed...*", parse_mode='Markdown')
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        d, u = st.download()/1e6, st.upload()/1e6
        res = (
            "🚀 **NETWORK SPEED**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"📥 **Download:** {d:.2f} Mbps\n"
            f"📤 **Upload:** {u:.2f} Mbps\n"
            f"📶 **Ping:** {st.results.ping} ms\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        await msg.edit_text(res, reply_markup=back_btn(), parse_mode='Markdown')
    except:
        await msg.edit_text("❌ Speedtest busy. Try again.", reply_markup=back_btn())

async def hw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "💻 **HARDWARE DETAILS**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🖥️ **CPU:** {platform.processor()}\n"
        f"⚙️ **Cores:** {psutil.cpu_count()} Cores\n"
        f"🌍 **OS:** {platform.system()} {platform.machine()}\n"
        f"🐍 **Python:** v{platform.python_version()}\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )
    await update.callback_query.message.edit_text(text, reply_markup=back_btn(), parse_mode='Markdown')

async def cmd_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📜 **COMMAND LIST**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🔹 `/start` - Home\n"
        "🔹 `/info` - Stats\n"
        "🔹 `/speed` - Speedtest\n"
        "🔹 `/hw` - Specs\n"
        "🔹 `/cmd` - All List\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )
    if update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=back_btn(), parse_mode='Markdown')
    else:
        await update.message.reply_text(text, parse_mode='Markdown')

# --- BUTTON ROUTING ---
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'stats': await stats(update, context)
    elif query.data == 'speed': await speed(update, context)
    elif query.data == 'hw': await hw(update, context)
    elif query.data == 'cmds': await cmd_list(update, context)
    elif query.data == 'home':
        await query.message.edit_text("👑 **ELITE DASHBOARD V3**", reply_markup=main_menu(), parse_mode='Markdown')

if __name__ == '__main__':
    # Start Web Server (Success Signal for Render)
    threading.Thread(target=run_web_server, daemon=True).start()
    
    # Start Bot
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("info", stats))
    app.add_handler(CommandHandler("speed", speed))
    app.add_handler(CommandHandler("cmd", cmd_list))
    app.add_handler(CommandHandler("hw", hw))
    app.add_handler(CallbackQueryHandler(button_click))
    
    print("Bot & Web Site are LIVE!")
    app.run_polling()
    
