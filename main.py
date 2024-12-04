import os
from dotenv import load_dotenv
import requests
from twilio.rest import Client

# Load environment variables
load_dotenv()

# Get environment variables
STOCK = os.getenv('STOCK')
COMPANY_NAME = os.getenv('COMPANY_NAME')
API_KEY_ONE = os.getenv('API_KEY_ONE')
API_KEY_TWO = os.getenv('API_KEY_TWO')
URL_ONE = os.getenv('URL_ONE')
URL_TWO = os.getenv('URL_TWO')

# Twilio credentials
TWILIO_SID = os.getenv('TWILIO_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
YOUR_PHONE_NUMBER = os.getenv('YOUR_PHONE_NUMBER')

# Parameters for API requests
PARAM_ONE = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": API_KEY_ONE
}

PARAM_TWO = {
    "apikey": API_KEY_TWO,
    "qInTitle": COMPANY_NAME
}


def req(url, params):
    """Makes a request to the given URL with the specified parameters.

    Args:
        url (str): The API endpoint URL.
        params (dict): The parameters for the API request.

    Returns:
        dict: The JSON response from the API, or None if an error occurs.
    """
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses
        data = response.json()
        return data
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")


# Fetch stock data
data_one = req(URL_ONE, PARAM_ONE)
if data_one:
    data = data_one.get("Time Series (Daily)", {})
    TIMESERIES_LIST = [value for (key, value) in data.items()]
    print(TIMESERIES_LIST)

    if len(TIMESERIES_LIST) >= 2:
        # Compare closing prices
        yesterday_date = TIMESERIES_LIST[0]
        yesterday_closing_price = float(yesterday_date["4. close"])

        day_before_yesterday_date = TIMESERIES_LIST[1]
        day_before_yesterday_closing_price = float(day_before_yesterday_date["4. close"])

        differ = abs(yesterday_closing_price - day_before_yesterday_closing_price)
        differ_percent = (differ / day_before_yesterday_closing_price) * 100

        if differ_percent > 5:
            # Fetch news articles
            data_two = req(URL_TWO, PARAM_TWO)
            if data_two:
                three_articles = data_two.get("articles", [])[:3]

                # Prepare the message
                direction = "🔺" if yesterday_closing_price > day_before_yesterday_closing_price else "🔻"
                message = f"{STOCK}: {direction}{differ_percent:.2f}%\n"
                for article in three_articles:
                    title = article.get("title", "No title")
                    description = article.get("description", "No description")
                    message += f"Headline: {title}\nBrief: {description}\n\n"

                print(message)  # Optional: Print the message to verify it

                # Send SMS via Twilio
                try:
                    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
                    client.messages.create(
                        body=message,
                        from_=TWILIO_PHONE_NUMBER,
                        to=YOUR_PHONE_NUMBER
                    )
                except Exception as e:
                    print(f"Failed to send SMS: {e}")
