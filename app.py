from quart import Quart, request
import requests
import asyncio
from telegram import Bot, Update

app = Quart(__name__)
bot_token = 'your-bot-token-from-telegram'

# Initialize bot
bot = Bot(token=bot_token)

# InfluxDB settings
INFLUXDB_URL = "http://ip_addr:8086"

async def send_message(chat_id, text):
    await bot.send_message(chat_id=chat_id, text=text)

async def start(update):
    await send_message(update.message.chat_id, 'Hi! Use /airquality or /temperature to get the latest readings.')

async def get_air_quality(update):
    try:
        response = requests.get(f"{INFLUXDB_URL}/query", params={
            "q": "SELECT last(air_quality) FROM sensor_data",
            "db": "sensor_data"
        })
        data = response.json()
        print("Air quality response:", data)
        if 'results' in data and data['results'][0].get('series'):
            air_quality = data['results'][0]['series'][0]['values'][0][1]
            print(f"Air quality value: {air_quality}")
            await send_message(update.message.chat_id, f"Current air quality: {air_quality}")
        else:
            print("No air quality data found.")
            await send_message(update.message.chat_id, "No air quality data found.")
    except Exception as e:
        print("Error fetching air quality:", e)
        await send_message(update.message.chat_id, "Error fetching air quality data.")

async def get_temperature(update):
    try:
        response = requests.get(f"{INFLUXDB_URL}/query", params={
            "q": "SELECT last(temperature) FROM sensor_data",
            "db": "sensor_data"
        })
        data = response.json()
        print("Temperature response:", data)
        if 'results' in data and data['results'][0].get('series'):
            temperature = data['results'][0]['series'][0]['values'][0][1]
            print(f"Temperature value: {temperature}")
            await send_message(update.message.chat_id, f"Current temperature: {temperature}°C")
        else:
            print("No temperature data found.")
            await send_message(update.message.chat_id, "No temperature data found.")
    except Exception as e:
        print("Error fetching temperature:", e)
        await send_message(update.message.chat_id, "Error fetching temperature data.")

@app.route('/webhook', methods=['POST'])
async def webhook():
    update = Update.de_json(await request.get_json(), bot)
    await handle_update(update)
    return 'ok'

async def handle_update(update):
    if update.message:
        print(f"Handling message: {update.message.text}")
        if update.message.text == '/start':
            await start(update)
        elif update.message.text == '/airquality':
            await get_air_quality(update)
        elif update.message.text == '/temperature':
            await get_temperature(update)
        else:
            await send_message(update.message.chat_id, "Unknown command")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8443)
