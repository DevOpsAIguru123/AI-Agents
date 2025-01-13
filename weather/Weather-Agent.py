import os
import resend
import http.client
import json
from urllib.parse import quote  # Import for URL encoding
from resend.exceptions import ResendError
from dotenv import load_dotenv
import logging
from groq import Groq

# -------------------------------------------------------------
# 1. Configure Logging
# -------------------------------------------------------------
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("email_sender.log"),
        logging.StreamHandler()
    ]
)

# -------------------------------------------------------------
# 2. Load Environment Variables from .env
# -------------------------------------------------------------
load_dotenv()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")
TO_EMAIL = os.getenv("TO_EMAIL")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
LOCATION = os.getenv("LOCATION", "London")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Validate essential environment variables
missing_vars = []
for var_name, var_value in [("RESEND_API_KEY", RESEND_API_KEY), ("FROM_EMAIL", FROM_EMAIL), ("TO_EMAIL", TO_EMAIL), ("RAPIDAPI_KEY", RAPIDAPI_KEY), ("GROQ_API_KEY", GROQ_API_KEY)]:
    if not var_value:
        missing_vars.append(var_name)

if missing_vars:
    logging.critical(f"Missing environment variables: {', '.join(missing_vars)}. Please check your .env file.")
    exit(1)

resend.api_key = RESEND_API_KEY

# -------------------------------------------------------------
# 3. Groq Client Initialization
# -------------------------------------------------------------
groq_client = Groq(api_key=GROQ_API_KEY)

# -------------------------------------------------------------
# 4. Get Weather Information
# -------------------------------------------------------------
def get_tomorrow_weather():
    """
    Fetches the weather forecast for tomorrow using RapidAPI's WeatherAPI.
    """
    try:
        conn = http.client.HTTPSConnection("weatherapi-com.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': RAPIDAPI_KEY,
            'x-rapidapi-host': "weatherapi-com.p.rapidapi.com"
        }
        
        encoded_location = quote(LOCATION)
        endpoint = f"/forecast.json?q={encoded_location}&days=2"
        conn.request("GET", endpoint, headers=headers)
        
        res = conn.getresponse()
        data = res.read()
        weather_data = json.loads(data.decode("utf-8"))

        tomorrow_forecast = weather_data["forecast"]["forecastday"][1]
        date = tomorrow_forecast["date"]
        condition = tomorrow_forecast["day"]["condition"]["text"]
        avg_temp_c = tomorrow_forecast["day"]["avgtemp_c"]
        avg_temp_f = tomorrow_forecast["day"]["avgtemp_f"]
        max_wind_kph = tomorrow_forecast["day"]["maxwind_kph"]
        humidity = tomorrow_forecast["day"]["avghumidity"]

        return {
            "date": date,
            "condition": condition,
            "avg_temp_c": avg_temp_c,
            "avg_temp_f": avg_temp_f,
            "max_wind_kph": max_wind_kph,
            "humidity": humidity
        }

    except Exception as e:
        logging.error(f"Failed to fetch weather data: {e}")
        return None

# -------------------------------------------------------------
# 5. Get Outdoor Activity Suggestions using Groq
# -------------------------------------------------------------
def get_activity_suggestions(weather_info):
    """
    Generates outdoor activity suggestions based on weather conditions using Groq Cloud's LLM.
    """
    try:
        chat_completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant that suggests outdoor activities based on the weather conditions."
                },
                {
                    "role": "user",
                    "content": (
                        f"Based on the following weather forecast, suggest 3 suitable outdoor activities:\n\n"
                        f"- Location: {LOCATION}\n"
                        f"- Date: {weather_info['date']}\n"
                        f"- Weather Condition: {weather_info['condition']}\n"
                        f"- Average Temperature: {weather_info['avg_temp_c']}°C / {weather_info['avg_temp_f']}°F\n"
                        f"- Humidity: {weather_info['humidity']}%\n"
                        f"- Max Wind Speed: {weather_info['max_wind_kph']} kph\n\n"
                        "Provide the suggestions as a list."
                    )
                }
            ],
            temperature=0.5,
            max_tokens=1024,
            top_p=1,
            stop=None,
            stream=False
        )

        activities = chat_completion.choices[0].message.content.strip()
        return activities

    except Exception as e:
        logging.error(f"Groq Cloud API Error: {e}")
        return "Unable to provide activity suggestions at this time."

# -------------------------------------------------------------
# 6. Send Email
# -------------------------------------------------------------
def send_email():
    """
    Sends an email using the Resend service with an HTML body containing weather info and activity suggestions.
    """
    weather_info = get_tomorrow_weather()
    if not weather_info:
        weather_info_html = "<p>Unable to fetch weather data at this time.</p>"
        activity_suggestions_html = ""
    else:
        weather_info_html = f"""
        <h2>Tomorrow's Weather in {LOCATION} ({weather_info['date']})</h2>
        <p><strong>Condition:</strong> {weather_info['condition']}</p>
        <p><strong>Average Temperature:</strong> {weather_info['avg_temp_c']}°C / {weather_info['avg_temp_f']}°F</p>
        <p><strong>Max Wind Speed:</strong> {weather_info['max_wind_kph']} kph</p>
        <p><strong>Humidity:</strong> {weather_info['humidity']}%</p>
        """
        activity_suggestions = get_activity_suggestions(weather_info)
        activity_suggestions_html = f"""
        <h3>Suggested Outdoor Activities</h3>
        <p>{activity_suggestions}</p>
        """

    email_body = f"""
    <html>
        <body>
            {weather_info_html}
            {activity_suggestions_html}
        </body>
    </html>
    """

    try:
        response = resend.Emails.send({
            "from": FROM_EMAIL,
            "to": TO_EMAIL,
            "subject": f"Tomorrow's Weather & Outdoor Activities 🌤️ - {LOCATION}",
            "html": email_body
        })
        logging.info("Email sent successfully via Resend!")
        logging.debug(f"Resend Response: {response}")
        return response
    except ResendError as e:
        logging.error(f"Resend API Error: {e}")
        return {}
    except Exception as e:
        logging.error(f"Unexpected error sending email with Resend: {e}")
        return {}

if __name__ == "__main__":
    send_email()
