@app.route('/')
def health_check():
    return "Bot is running", 200

# Команды бота
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Welcome! Use /set_pairs to change pairs, /check to analyze now.")

@bot.message_handler(commands=['set_pairs'])
def set_pairs(message):
    user_id = message.from_user.id
    markup = types.InlineKeyboardMarkup()
    btn_regular = types.InlineKeyboardButton("Regular (Crypto/Forex)", callback_data="regular")
    btn_otc = types.InlineKeyboardButton("OTC (Deriv Synthetics)", callback_data="otc")
    markup.add(btn_regular, btn_otc)
    bot.send_message(user_id, "Choose pair type:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id
    if call.data == "regular":
        user_pairs[user_id] = DEFAULT_PAIRS.copy()
        bot.answer_callback_query(call.id, "Set to regular pairs!")
    elif call.data == "otc":
        user_pairs[user_id] = ['R_10', 'R_25', 'R_50', 'R_75', 'R_100']
        bot.answer_callback_query(call.id, "Set to OTC pairs! (Note: Use Deriv API)")
    bot.edit_message_text("Pairs updated. Use /check to analyze.", call.message.chat.id, call.message.message_id)

@bot.message_handler(commands=['check'])
def check_signals(message):
    for pair in PAIRS:
        for interval in INTERVALS:
            signal_data = analyze_candles(pair, interval)
            if signal_data:
                send_signal_message(signal_data)
    bot.reply_to(message, f"Checked {len(PAIRS)*len(INTERVALS)} setups. Signals sent if any.")

# Фоновое задание
def start_background_task():
    loop = asyncio.get_event_loop()
    task = loop.create_task(run_periodically())
    return task

async def run_periodically():
    while True:
        for pair in PAIRS:
            for interval in INTERVALS:
                signal_data = analyze_candles(pair, interval)
                if signal_data:
                    send_signal_message(signal_data)
        await asyncio.sleep(60)  # Проверка каждую минуту

if name == 'main':
    task = start_background_task()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
