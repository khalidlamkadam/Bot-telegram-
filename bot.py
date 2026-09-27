import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def start_health_check_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=start_health_check_server, daemon=True).start()

# حط التوكن الجديد هنا
API_TOKEN = os.environ.get("BOT_TOKEN")


# محافظ استقبال الأموال
BINANCE_ID = "838990812"
USDT_BEP20 = "0x71e70715d63e2d20b82a1cfe770eb3a50a696f05"
USDT_TRC20 = "TEkXcay6yRsqRzceUMYbDixh4g9oSa6cke"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# تخزين لغة كل زبون
user_lang = {}

# نصوص اللغات
TEXTS = {
    "en": {
        "welcome": "👋 Welcome to our Store!",
        "menu_hint": "Please select an option from the menu below:",
        "catalog_title": "🛒 **Available Digital Accounts & Subscriptions:**",
        "wallet_text": "💳 **My Wallet**\n\nBalance: `0.00 USDT`",
        "support_text": "🗣 **Customer Support:**\nFor help, contact: @YourSupportAccount",
        "channel_text": "📢 **Join our updates channel:**\nhttps://t.me/YourChannel",
        "choose_lang": "🌐 Choose your preferred language:",
        "lang_updated": "✅ Language changed to English.",
        "pay_title": "💳 **Select Payment Network:**",
        "pay_info": "Send **{price} USDT** to:\n\nNetwork: `{net}`\nAddress: `{addr}`\n\nAfter transfer, send your TxID to confirm."
    },
    "ar": {
        "welcome": "👋 مرحباً بك في المتجر!",
        "menu_hint": "يرجى اختيار أحد الأقسام من القائمة بالأسفل:",
        "catalog_title": "🛒 **الحسابات والاشتراكات الرقمية المتوفرة:**",
        "wallet_text": "💳 **محفظتي**\n\nالرصيد: `0.00 USDT`",
        "support_text": "🗣 **الدعم الفني:**\nلأي استفسار تواصل مع: @YourSupportAccount",
        "channel_text": "📢 **اشترك في قناة العروض:**\nhttps://t.me/YourChannel",
        "choose_lang": "🌐 اختر لغتك المفضلة:",
        "lang_updated": "✅ تم تغيير اللغة إلى العربية.",
        "pay_title": "💳 **اختر شبكة الدفع:**",
        "pay_info": "أرسل **{price} USDT** إلى:\n\nالشبكة: `{net}`\nالعنوان: `{addr}`\n\nبعد التحويل، أرسل رمز المعاملة TxID للتأكيد."
    },
    "fr": {
        "welcome": "👋 Bienvenue sur notre boutique!",
        "menu_hint": "Veuillez choisir une option dans le menu ci-dessous:",
        "catalog_title": "🛒 **Comptes et abonnements digitaux disponibles:**",
        "wallet_text": "💳 **Mon Portefeuille**\n\nSolde: `0.00 USDT`",
        "support_text": "🗣 **Support Client:**\nPour toute aide, contactez: @YourSupportAccount",
        "channel_text": "📢 **Rejoignez notre canal:**\nhttps://t.me/YourChannel",
        "choose_lang": "🌐 Choisissez votre langue préférée:",
        "lang_updated": "✅ Langue modifiée en français.",
        "pay_title": "💳 **Sélectionnez le réseau de paiement:**",
        "pay_info": "Envoyez **{price} USDT** à:\n\nRéseau: `{net}`\nAdresse: `{addr}`\n\nAprès transfert, envoyez le TxID pour confirmer."
    }
}

# الكيبورد السفلي الدائم
def get_main_keyboard():
    kb = [
        [KeyboardButton(text="🛒 Products"), KeyboardButton(text="💳 My Wallet")],
        [KeyboardButton(text="📢 Channel"), KeyboardButton(text="🗣 Support")],
        [KeyboardButton(text="🌐 Language")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# أزرار اختيار اللغة
def get_lang_inline():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="set_en")],
        [InlineKeyboardButton(text="🇸🇦 العربية", callback_data="set_ar")],
        [InlineKeyboardButton(text="🇫🇷 Français", callback_data="set_fr")]
    ])

# أزرار المنتجات
def get_products_inline():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ChatGPT Plus - 1 Month ($10)", callback_data="prod_chatgpt")],
        [InlineKeyboardButton(text="CapCut Pro - 1 Year ($15)", callback_data="prod_capcut")],
        [InlineKeyboardButton(text="Canva Pro - Lifetime ($5)", callback_data="prod_canva")]
    ])

# أزرار شبكات الدفع
def get_payment_networks(prod_id: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="USDT (TRC20)", callback_data=f"pay_trc20_{prod_id}")],
        [InlineKeyboardButton(text="USDT (BSC / BEP20)", callback_data=f"pay_bsc_{prod_id}")],
        [InlineKeyboardButton(text="Binance Pay ID", callback_data=f"pay_bpay_{prod_id}")]
    ])

@dp.message(Command("start"))
async def start_command(message: types.Message):
    lang = user_lang.get(message.from_user.id, "en")
    t = TEXTS[lang]
    await message.answer(f"{t['welcome']}\n\n{t['menu_hint']}", reply_markup=get_main_keyboard())

@dp.message(F.text == "🛒 Products")
async def show_products(message: types.Message):
    lang = user_lang.get(message.from_user.id, "en")
    await message.answer(TEXTS[lang]["catalog_title"], reply_markup=get_products_inline(), parse_mode="Markdown")

@dp.message(F.text == "💳 My Wallet")
async def show_wallet(message: types.Message):
    lang = user_lang.get(message.from_user.id, "en")
    await message.answer(TEXTS[lang]["wallet_text"], parse_mode="Markdown")

@dp.message(F.text == "📢 Channel")
async def show_channel(message: types.Message):
    lang = user_lang.get(message.from_user.id, "en")
    await message.answer(TEXTS[lang]["channel_text"])

@dp.message(F.text == "🗣 Support")
async def show_support(message: types.Message):
    lang = user_lang.get(message.from_user.id, "en")
    await message.answer(TEXTS[lang]["support_text"])

@dp.message(F.text == "🌐 Language")
async def show_languages(message: types.Message):
    lang = user_lang.get(message.from_user.id, "en")
    await message.answer(TEXTS[lang]["choose_lang"], reply_markup=get_lang_inline())

@dp.callback_query(F.data.startswith("set_"))
async def update_language(cb: types.CallbackQuery):
    selected = cb.data.split("_")[1]
    user_lang[cb.from_user.id] = selected
    await cb.message.edit_text(TEXTS[selected]["lang_updated"])
    await cb.answer()

@dp.callback_query(F.data.startswith("prod_"))
async def choose_prod_payment(cb: types.CallbackQuery):
    lang = user_lang.get(cb.from_user.id, "en")
    prod_id = cb.data.split("_")[1]
    await cb.message.edit_text(TEXTS[lang]["pay_title"], reply_markup=get_payment_networks(prod_id), parse_mode="Markdown")
    await cb.answer()

@dp.callback_query(F.data.startswith("pay_"))
async def payment_details(cb: types.CallbackQuery):
    lang = user_lang.get(cb.from_user.id, "en")
    _, net, prod = cb.data.split("_")
    
    addr_map = {
        "trc20": ("TRC20", USDT_TRC20, "10.00"),
        "bsc": ("BEP20", USDT_BEP20, "10.00"),
        "bpay": ("Binance Pay ID", BINANCE_ID, "10.00")
    }
    net_name, addr, price = addr_map[net]
    
    text = TEXTS[lang]["pay_info"].format(price=price, net=net_name, addr=addr)
    await cb.message.edit_text(text, parse_mode="Markdown")
    await cb.answer()
from aiogram import F
from aiogram.types import CallbackQuery

# 1. معالج شبكة TRC20
@dp.callback_query(F.data.startswith("pay_trc20_"))
async def process_pay_trc20(callback: CallbackQuery):
    await callback.answer()
    prod_id = callback.data.replace("pay_trc20_", "")
    
    msg = (
        f"💳 **شبكة الدفع: USDT (TRC20)**\n\n"
        f"📍 **عنوان الإيداع:**\n`{USDT_TRC20}`\n\n"
        f"⚠️ يرجى التأكد من التحويل عبر شبكة Tron (TRC20) فقط."
    )
    await callback.message.answer(msg, parse_mode="Markdown")

# 2. معالج شبكة BEP20 (BSC)
@dp.callback_query(F.data.startswith("pay_bsc_"))
async def process_pay_bsc(callback: CallbackQuery):
    await callback.answer()
    prod_id = callback.data.replace("pay_bsc_", "")
    
    msg = (
        f"💳 **شبكة الدفع: USDT (BSC / BEP20)**\n\n"
        f"📍 **عنوان الإيداع:**\n`{USDT_BEP20}`\n\n"
        f"⚠️ يرجى التأكد من التحويل عبر شبكة BNB Smart Chain (BEP20)."
    )
    await callback.message.answer(msg, parse_mode="Markdown")

# 3. معالج Binance Pay ID
@dp.callback_query(F.data.startswith("pay_bpay_"))
async def process_pay_bpay(callback: CallbackQuery):
    await callback.answer()
    prod_id = callback.data.replace("pay_bpay_", "")
    
    msg = (
        f"💳 **الدفع عبر Binance Pay**\n\n"
        f"🆔 **معرف الحساب (Binance ID):**\n`{BINANCE_ID}`\n\n"
        f"يرجى إرسال لقطة شاشة للإشعار بعد التحويل للتأكيد."
    )
    await callback.message.answer(msg, parse_mode="Markdown")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
