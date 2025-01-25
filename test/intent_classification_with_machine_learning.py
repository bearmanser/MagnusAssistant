from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score


# Define dummy functions for various tasks
def getWeather(location):
    return "It's sunny in " + location


def setTimer(duration):
    return f"Timer set for {duration} minutes."


def getNews(topic):
    return f"Here are the latest news about {topic}."


def playMusic(genre):
    return f"Playing {genre} music."


def getStockPrice(stock):
    return f"The current price of {stock} is $100."


def sendEmail(recipient, subject):
    return f"Email sent to {recipient} with subject '{subject}'."


def bookFlight(destination, date):
    return f"Flight to {destination} on {date} booked."


def getJoke():
    return "Why don't scientists trust atoms? Because they make up everything!"


def checkWeatherForecast(location):
    return f"The forecast for {location} is rain tomorrow."


def startWorkout(workout_type):
    return f"Starting your {workout_type} workout."


# Expanded training data with more examples
training_data = [
    ("What's the weather like in New York?", "get_weather"),
    ("Tell me the weather in London", "get_weather"),
    ("What's the temperature in Tokyo?", "get_weather"),
    ("Will it rain tomorrow in Paris?", "check_weather_forecast"),
    ("Show me the forecast for Rome", "check_weather_forecast"),
    ("Set a timer for 10 minutes", "set_timer"),
    ("I need a timer for 15 minutes", "set_timer"),
    ("Start a timer for 5 minutes", "set_timer"),
    ("Play some jazz music", "play_music"),
    ("Play pop songs", "play_music"),
    ("Can you play some classical music?", "play_music"),
    ("Get me the latest news on technology", "get_news"),
    ("What's new in sports?", "get_news"),
    ("Show me the headlines for today", "get_news"),
    ("Send an email to John with the subject 'Meeting'", "send_email"),
    ("Compose an email to Lisa about the report", "send_email"),
    ("Email Sarah about the dinner plans", "send_email"),
    ("Book a flight to Paris on September 20th", "book_flight"),
    ("I need a flight to New York for next Monday", "book_flight"),
    ("Find me a flight to Tokyo on December 25th", "book_flight"),
    ("What's the stock price of Apple?", "get_stock_price"),
    ("How much is Tesla's stock?", "get_stock_price"),
    ("Get me the current price of Amazon shares", "get_stock_price"),
    ("Tell me a joke", "get_joke"),
    ("Can you tell me a funny joke?", "get_joke"),
    ("I need a good laugh, tell me a joke", "get_joke"),
    ("Will it rain in Seattle tomorrow?", "check_weather_forecast"),
    ("What's the weather forecast for Chicago?", "check_weather_forecast"),
    ("Start a cardio workout", "start_workout"),
    ("Begin a yoga session", "start_workout"),
    ("I want to do a strength workout", "start_workout"),
]

texts, intents = zip(*training_data)

# Vectorization and model training
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)
model = LogisticRegression().fit(X, intents)

# Test with various user inputs to evaluate accuracy
test_data = [
    ("What's the weather in Oslo?", "get_weather"),
    # ("Will it rain in Seattle tomorrow?", "check_weather_forecast"),
    # ("Start a 5-minute timer", "set_timer"),
    # ("Play some rock music", "play_music"),
    # ("Give me news about sports", "get_news"),
    # ("Send an email to Sarah about the project", "send_email"),
    # ("Book a flight to Tokyo on December 25th", "book_flight"),
    # ("What is the stock price of Tesla?", "get_stock_price"),
    # ("Tell me a joke", "get_joke"),
    # ("What's the forecast for New York tomorrow?", "check_weather_forecast"),
    # ("Start a strength workout", "start_workout"),
]

test_texts, expected_intents = zip(*test_data)
X_test = vectorizer.transform(test_texts)
predicted_intents = model.predict(X_test)

# Calculate accuracy
accuracy = accuracy_score(expected_intents, predicted_intents)
print(f"Model Accuracy: {accuracy * 100:.2f}%")

# Output for individual test cases
for i, user_input in enumerate(test_texts):
    predicted_intent = predicted_intents[i]

    if predicted_intent == "get_weather":
        location = "San Francisco"  # Dummy location extraction
        result = getWeather(location)
    elif predicted_intent == "set_timer":
        duration = 5  # Dummy duration extraction
        result = setTimer(duration)
    elif predicted_intent == "play_music":
        genre = "rock"  # Dummy genre extraction
        result = playMusic(genre)
    elif predicted_intent == "get_news":
        topic = "sports"  # Dummy topic extraction
        result = getNews(topic)
    elif predicted_intent == "send_email":
        recipient = "Sarah"  # Dummy recipient extraction
        subject = "the project"  # Dummy subject extraction
        result = sendEmail(recipient, subject)
    elif predicted_intent == "book_flight":
        destination = "Tokyo"  # Dummy destination extraction
        date = "December 25th"  # Dummy date extraction
        result = bookFlight(destination, date)
    elif predicted_intent == "get_stock_price":
        stock = "Tesla"  # Dummy stock extraction
        result = getStockPrice(stock)
    elif predicted_intent == "get_joke":
        result = getJoke()
    elif predicted_intent == "check_weather_forecast":
        location = "New York"  # Dummy location extraction
        result = checkWeatherForecast(location)
    elif predicted_intent == "start_workout":
        workout_type = "strength"  # Dummy workout type extraction
        result = startWorkout(workout_type)
    else:
        result = "Unknown intent"

    print(f"User Input: {user_input}")
    print(f"Predicted Intent: {predicted_intent}")
    print(f"Result: {result}")
    print("-" * 40)
