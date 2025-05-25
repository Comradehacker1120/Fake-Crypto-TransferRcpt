#!/usr/bin/env python3
import os
import random
import json
from datetime import datetime
from faker import Faker
import qrcode
from io import BytesIO
import base64
from telegram import Bot, Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# Configuration
CONFIG_FILE = "crypto_fake_config.json"
OUTPUT_FOLDER = "fakecrypto_results"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
fake = Faker()

# Embedded Crypto Icons (Base64 encoded)
CRYPTO_ICONS = {
    "btc": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAzODQgNTEyIj48cGF0aCBmaWxsPSIjZjc5MzFhIiBkPSJNMzQxLjkgMTYwLjFjLTMuMi0yMC43LTcuNC00MS40LTEyLjUtNjEuOEMzMTMuMSA1OC44IDI4Mi44IDMyIDI0Ni4xIDMyaC0xMDguMkMyMDEuNCAzMiAxNzEuMSA1OC44IDE1NC42IDk4LjMtNS4xIDIwLjQtOS4zIDQxLjEtMTIuNSA2MS44QzEzOS40IDE5Ni4yIDEzNiAyMTYgMTM2IDI1NmMwIDQwIDMuNCA1OS44IDYuMSA5NS45IDMuMiAyMC43IDcuNCA0MS40IDEyLjUgNjEuOCAxNi41IDM5LjUgNDYuOCA2Ni4zIDgzLjUgNjYuM2gxMDguMmMzNi43IDAgNjYuOS0yNi44IDgzLjUtNjYuMyA1LjEtMjAuNCA5LjMtNDEuMSAxMi41LTYxLjggMi43LTM2LjEgNi4xLTU1LjkgNi4xLTk1LjkgMC00MC0zLjQtNTkuOC02LjEtOTUuOXptLTE4Ni42IDkxLjhjLTEuNy0xMS41LTIuNy0yMi44LTIuNy0zNS45czAuOS0yNC40IDIuNy0zNS45YzEuNy0xMS41IDQuMS0yMS42IDcuNS0zMC44IDMuNC05LjIgNy44LTE3LjMgMTMuMS0yNC40czExLjgtMTMuMSAxOS41LTE4LjFjNy43LTUgMTYuOS04LjQgMjcuNS04LjQgMTAuNiAwIDE5LjggMy40IDI3LjUgOC40IDcuNyA1IDE0LjEgMTEuMyAxOS41IDE4LjFzOS43IDE1LjIgMTMuMSAyNC40YzMuNCA5LjIgNS44IDE5LjMgNy41IDMwLjggMS43IDExLjUgMi43IDIyLjggMi43IDM1LjlzLTAuOSAyNC40LTIuNyAzNS45Yy0xLjcgMTEuNS00LjEgMjEuNi03LjUgMzAuOC0zLjQgOS4yLTcuOCAxNy4zLTEzLjEgMjQuNHMtMTEuOCAxMy4xLTE5LjUgMTguMWMtNy43IDUtMTYuOSA4LjQtMjcuNSA4LjQtMTAuNiAwLTE5LjgtMy40LTI3LjUtOC40LTcuNy01LTE0LjEtMTEuMy0xOS41LTE4LjFzLTkuNy0xNS4yLTEzLjEtMjQuNGMtMy40LTkuMi01LjgtMTkuMy03LjUtMzAuOHptNDUuNiAxMzkuNWMtNS40IDE1LjEtMTAuMSAyOS45LTEzLjUgNDUuN2gtNDIuMmMtNy4xIDAtMTMuMS01LjEtMTQuNC0xMi4xQzEyNCAzMDkuOCAxMjQgMjgyLjUgMTI0IDI1NnMwLTUzLjggMi42LTgwLjFjMS4zLTcgNy4zLTEyLjEgMTQuNC0xMi4xaDQyLjJjMy40IDE1LjggOC4xIDMwLjYgMTMuNSA0NS43czEyLjEgMjkuMSAyMC4xIDQyLjFjLTggMTMtMTQuNiAyNy4xLTIwLjEgNDIuMXptOTYuNi0xMzkuNWMtMS43LTExLjUtNC4xLTIxLjYtNy41LTMwLjgtMy40LTkuMi03LjgtMTcuMy0xMy4xLTI0LjRzLTExLjgtMTMuMS0xOS41LTE4LjFjLTcuNy01LTE2LjktOC40LTI3LjUtOC40LTEwLjYgMC0xOS44IDMuNC0yNy41IDguNC03LjcgNS0xNC4xIDExLjMtMTkuNSAxOC4xcy05LjcgMTUuMi0xMy4xIDI0LjRjLTMuNCA5LjItNS44IDE5LjMtNy41IDMwLjgtMS43IDExLjUtMi43IDIyLjgtMi43IDM1LjlzMC45IDI0LjQgMi43IDM1LjljMS43IDExLjUgNC4xIDIxLjYgNy41IDMwLjggMy40IDkuMiA3LjggMTcuMyAxMy4xIDI0LjRzMTEuOCAxMy4xIDE5LjUgMTguMWM3LjcgNSAxNi45IDguNCAyNy41IDguNCAxMC42IDAgMTkuOC0zLjQgMjcuNS04LjQgNy43LTUgMTQuMS0xMS4zIDE5LjUtMTguMXM5LjctMTUuMiAxMy4xLTI0LjRjMy40LTkuMiA1LjgtMTkuMyA3LjUtMzAuOCAxLjctMTEuNSAyLjctMjIuOCAyLjctMzUuOXMtMC45LTI0LjQtMi43LTM1Ljl6Ii8+PC9zdmc+",
    "eth": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAzMjAgNTEyIj48cGF0aCBmaWxsPSIjNjI3ZWVhIiBkPSJNMzIwIDI1NmMwIDE0MS40LTExNC42IDI1Ni0yNTYgMjU2UzAgMzk3LjQgMCAyNTYgMTE0LjYgMCAyNTYgMHMyNTYgMTE0LjYgMjU2IDI1NnptLTEyOCA4MGMwIDQ0LjItMzUuOCA4MC04MCA4MHM4MC0zNS44IDgwLTgwLTM1LjgtODAtODAtODAtODAgMzUuOC04MCA4MHptMC0xNjBjMCA0NC4yLTM1LjggODAtODAgODBzODAtMzUuOCA4MC04MC0zNS44LTgwLTgwLTgwLTgwIDM1LjgtODAgODB6Ii8+PC9zdmc+",
    "bnb": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA0NDggNTEyIj48cGF0aCBmaWxsPSIjZjNiYTJmIiBkPSJNMjI0IDUxMmMxMjMuNSAwIDIyNC0xMDAuNSAyMjQtMjI0UzM0Ny41IDY0IDIyNCA2NCAwIDE2NC41IDAgMjg4czEwMC41IDIyNCAyMjQgMjI0em0wLTM4NGM4OC4yIDAgMTYwIDcxLjggMTYwIDE2MHMtNzEuOCAxNjAtMTYwIDE2MC0xNjAtNzEuOC0xNjAtMTYwIDcxLjgtMTYwIDE2MC0xNjB6Ii8+PC9zdmc+",
    "doge": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA0NDggNTEyIj48cGF0aCBmaWxsPSIjYzJhNjMzIiBkPSJNMjI0IDUxMmMxMjMuNSAwIDIyNC0xMDAuNSAyMjQtMjI0UzM0Ny41IDY0IDIyNCA2NCAwIDE2NC41IDAgMjg4czEwMC41IDIyNCAyMjQgMjI0em0wLTM4NGM4OC4yIDAgMTYwIDcxLjggMTYwIDE2MHMtNzEuOCAxNjAtMTYwIDE2MC0xNjAtNzEuOC0xNjAtMTYwIDcxLjgtMTYwIDE2MC0xNjB6Ii8+PC9zdmc+"
}

# Transaction HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{crypto_name} Transaction</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f7fa;
            margin: 0;
            padding: 20px;
            color: #333;
        }}
        .receipt-container {{
            max-width: 500px;
            margin: 20px auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: {header_color};
            color: white;
            padding: 20px;
            text-align: center;
            position: relative;
        }}
        .crypto-icon {{
            width: 60px;
            height: 60px;
            margin: 0 auto 15px;
            display: block;
        }}
        .status-badge {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(255,255,255,0.2);
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
        }}
        .tx-id {{
            background: #f8f9fa;
            padding: 15px;
            margin: 0;
            font-family: monospace;
            word-break: break-all;
            border-bottom: 1px solid #eee;
        }}
        .details {{
            padding: 20px;
        }}
        .detail-row {{
            display: flex;
            margin-bottom: 15px;
            align-items: center;
        }}
        .label {{
            font-weight: 600;
            width: 120px;
            color: #666;
        }}
        .value {{
            flex: 1;
        }}
        .amount {{
            font-size: 24px;
            font-weight: bold;
            color: {header_color};
            text-align: center;
            margin: 20px 0;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 15px;
            text-align: center;
            font-size: 12px;
            color: #999;
            border-top: 1px solid #eee;
        }}
        .qr-code {{
            width: 150px;
            height: 150px;
            margin: 20px auto;
            background: #eee;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .qr-code img {{
            width: 100%;
            height: 100%;
        }}
        .ref-id {{
            background: #f0f0f0;
            padding: 10px;
            border-radius: 6px;
            font-family: monospace;
            text-align: center;
            margin: 15px 0;
        }}
        .memo {{
            background: #f8f9fa;
            padding: 10px;
            border-radius: 6px;
            border-left: 3px solid {header_color};
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <div class="receipt-container">
        <div class="header">
            <img src="{crypto_icon}" class="crypto-icon" alt="{crypto_name}">
            <h2>{crypto_name} Transaction</h2>
            <div class="status-badge">CONFIRMED</div>
        </div>
        
        <p class="tx-id">Transaction ID: {tx_id}</p>
        
        <div class="details">
            <div class="amount">{amount} {crypto_symbol}</div>
            
            <div class="ref-id">Reference ID: {ref_id}</div>
            
            <div class="detail-row">
                <div class="label">Date:</div>
                <div class="value">{timestamp}</div>
            </div>
            <div class="detail-row">
                <div class="label">From:</div>
                <div class="value">{sender}</div>
            </div>
            <div class="detail-row">
                <div class="label">To:</div>
                <div class="value">{receiver}</div>
            </div>
            <div class="detail-row">
                <div class="label">Network Fee:</div>
                <div class="value">{fee} {crypto_symbol}</div>
            </div>
            
            {memo_html}
            
            <div class="qr-code">
                <img src="data:image/png;base64,{qr_code}" alt="QR Code">
            </div>
        </div>
        
        <div class="footer">
            Transaction complete, Remember no Refund
        </div>
    </div>
</body>
</html>
"""

def init_config():
    if not os.path.exists(CONFIG_FILE):
        config = {
            "telegram_token": "",
            "chat_id": "",
            "last_ref_id": 100000,
            "network_fees": {
                "btc": 0.0005,
                "eth": 0.01,
                "bnb": 0.001,
                "doge": 2.0
            }
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
        return config
    with open(CONFIG_FILE) as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def generate_qr(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def generate_receipt(crypto, sender, receiver, amount, fee, ref_id, memo=""):
    crypto_data = {
        "btc": {"name": "Bitcoin", "symbol": "BTC", "color": "#f7931a", "icon": CRYPTO_ICONS["btc"]},
        "eth": {"name": "Ethereum", "symbol": "ETH", "color": "#627eea", "icon": CRYPTO_ICONS["eth"]},
        "bnb": {"name": "Binance Coin", "symbol": "BNB", "color": "#f3ba2f", "icon": CRYPTO_ICONS["bnb"]},
        "doge": {"name": "Dogecoin", "symbol": "DOGE", "color": "#c2a633", "icon": CRYPTO_ICONS["doge"]}
    }[crypto]
    
    tx_id = f"{random.randint(100000, 999999)}...{random.randint(1000,9999)}"
    qr_code = generate_qr(f"{crypto_data['symbol']}:{receiver}?amount={amount}&memo={memo}")
    
    memo_html = f'<div class="memo"><strong>Memo:</strong> {memo}</div>' if memo else ""
    
    html = HTML_TEMPLATE.format(
        crypto_name=crypto_data["name"],
        crypto_symbol=crypto_data["symbol"],
        header_color=crypto_data["color"],
        crypto_icon=crypto_data["icon"],
        tx_id=tx_id,
        sender=sender,
        receiver=receiver,
        amount=amount,
        fee=fee,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ref_id=ref_id,
        qr_code=qr_code,
        memo_html=memo_html
    )
    
    filename = f"{OUTPUT_FOLDER}/{crypto}_tx_{ref_id}.html"
    with open(filename, "w") as f:
        f.write(html)
    
    return filename

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
🚀 Welcome to Fake Crypto Transfer Bot!

Available commands:
/generate - Create a fake transaction
/settings - Configure bot options
/help - Show this help message
""")

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["awaiting_crypto"] = True
    await update.message.reply_text("""
📊 Select cryptocurrency:
1. Bitcoin (BTC) 🪙
2. Ethereum (ETH) 💴
3. Binance Coin (BNB) 💵
4. Dogecoin (DOGE) 💶

Reply with the number (1-4)
""")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config = init_config()
    text = update.message.text
    
    if context.user_data.get("awaiting_crypto"):
        cryptos = ["btc", "eth", "bnb", "doge"]
        if text in ["1", "2", "3", "4"]:
            crypto = cryptos[int(text)-1]
            context.user_data["crypto"] = crypto
            context.user_data["awaiting_crypto"] = False
            context.user_data["awaiting_receiver"] = True
            await update.message.reply_text(f"""
💳 Enter recipient {crypto.upper()} address:
(Example: {'1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa' if crypto == 'btc' else 
           '0x71C7656EC7ab88b098defB751B7401B5f6d8976F' if crypto == 'eth' else
           'bnb1qxy2kgdygjrsqtzq2n0yrf2493py83pe5x4q2j' if crypto == 'bnb' else
           'D8hy7Wn2pXJY7D9A3q7JhZ6T2X1QrJ5yW9'})
""")
        else:
            await update.message.reply_text("❌ Invalid choice. Please select 1-4")
    
    elif context.user_data.get("awaiting_receiver"):
        receiver = text.strip()
        if len(receiver) > 5:  # Basic validation
            context.user_data["receiver"] = receiver
            context.user_data["awaiting_receiver"] = False
            context.user_data["awaiting_amount"] = True
            await update.message.reply_text("💰 Enter amount to send example 0.00065 or 0.0236:")
        else:
            await update.message.reply_text("❌ Invalid address format. Please try again")
    
    elif context.user_data.get("awaiting_amount"):
        try:
            amount = float(text)
            if amount <= 0:
                await update.message.reply_text("❌ Amount must be greater than 0")
                return
                
            context.user_data["amount"] = amount
            context.user_data["awaiting_amount"] = False
            context.user_data["awaiting_memo"] = True
            await update.message.reply_text("📝 Enter transaction memo example  #Transaction1467 #Payment235(or /skip):")
        except ValueError:
            await update.message.reply_text("❌ Invalid amount. Please enter a number")
    
    elif context.user_data.get("awaiting_memo"):
        memo = text if text != "/skip" else ""
        crypto = context.user_data["crypto"]
        receiver = context.user_data["receiver"]
        amount = context.user_data["amount"]
        
        # Generate transaction
        config["last_ref_id"] += 1
        ref_id = f"TRX{config['last_ref_id']}"
        fee = config["network_fees"][crypto]
        sender = f"{crypto.upper()}_Wallet_{random.randint(1000,9999)}"
        
        filename = generate_receipt(crypto, sender, receiver, amount, fee, ref_id, memo)
        save_config(config)
        
        # Send receipt
        with open(filename, "rb") as f:
            await update.message.reply_document(
                document=f,
                caption=f"""
✅ Fake {crypto.upper()} Transaction Generated!

🔹 Amount: {amount} {crypto.upper()}
🔹 To: {receiver}
🔹 Fee: {fee} {crypto.upper()}
🔹 Ref ID: {ref_id}
🔹 Memo: {memo if memo else 'None'}

📁 Receipt saved as: {filename}
"""
            )
        
        # Clear conversation state
        context.user_data.clear()

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config = init_config()
    await update.message.reply_text(f"""
⚙️ Current Settings:

🔸 Bot Token: {'✅ Configured' if config['telegram_token'] else '❌ Not set'}
🔸 Chat ID: {config['chat_id'] or '❌ Not set'}
🔸 Last Ref ID: {config['last_ref_id']}
🔸 Network Fees:
   - BTC: {config['network_fees']['btc']}
   - ETH: {config['network_fees']['eth']}
   - BNB: {config['network_fees']['bnb']}
   - DOGE: {config['network_fees']['doge']}

Send /setup to configure bot
""")

async def setup_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config = init_config()
    context.user_data["setting_up"] = True
    await update.message.reply_text("""
⚙️ Bot Setup Instructions:

1. Create a bot with @BotFather
2. Get your Chat ID from @userinfobot
3. Enter your Bot Token:
""")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
🆘 Help Guide:

/generate - Create a fake crypto transaction
/settings - View current bot configuration
/setup - Configure bot settings
/help - Show this help message

Transactions include:
- Beautiful HTML receipt
- QR code
- Reference ID
- Network fees
- Memo support
""")

def main():
    config = init_config()
    
    if not config["telegram_token"]:
        print("""
██████╗ ██████╗  █████╗ ███╗   ██╗██╗  ██╗
██╔══██╗██╔══██╗██╔══██╗████╗  ██║██║ ██╔╝
██████╔╝██████╔╝███████║██╔██╗ ██║█████╔╝ 
██╔═══╝ ██╔══██╗██╔══██║██║╚██╗██║██╔═██╗ 
██║     ██║  ██║██║  ██║██║ ╚████║██║  ██╗
╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝
ComradeHacker Fake Crypto Transfer Generator (Telegram Bot)
        
1. First, create a bot with @BotFather
2. Get your chat ID from @userinfobot
3. Enter your bot token below:
""")
        config["telegram_token"] = input("Bot Token: ").strip()
        config["chat_id"] = input("Chat ID: ").strip()
        save_config(config)
    
    # Create Application
    application = Application.builder().token(config["telegram_token"]).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("generate", generate))
    application.add_handler(CommandHandler("settings", settings))
    application.add_handler(CommandHandler("setup", setup_bot))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Your Telegram Bot is running enterbot page and press /help Or /generate... Press Ctrl+C to stop")
    application.run_polling()

if __name__ == "__main__":
    main()