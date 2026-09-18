import requests
import pyodbc
from datetime import datetime


# ---------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------

SQL_SERVER = r"BLR26-Y0A529JPT\SQLEXPRESS"
SQL_DATABASE = "Weather"

CITIES = [
    {
        "city": "New York",
        "latitude": 40.71,
        "longitude": -74.01
    },
    {
        "city": "Bengaluru",
        "latitude": 12.97,
        "longitude": 77.59
    },
    {
        "city": "London",
        "latitude": 51.51,
        "longitude": -0.13
    },
    {
        "city": "Tokyo",
        "latitude": 35.68,
        "longitude": 139.65
    },
    {
        "city": "Dubai",
        "latitude": 25.20,
        "longitude": 55.27
    }
]


# ---------------------------------------------------------------
# STEP 1: FETCH WEATHER DATA
# ---------------------------------------------------------------

def fetch_weather_data(city_config):

    city = city_config["city"]
    latitude = city_config["latitude"]
    longitude = city_config["longitude"]

    api_url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}"
        f"&longitude={longitude}"
        "&current_weather=true"
    )

    print(f"Requesting weather for {city}...")

    try:

        response = requests.get(
            api_url,
            timeout=10
        )

        response.raise_for_status()

        print(f"Data received for {city}")

        return response.json()

    except requests.exceptions.RequestException as e:

        print(
            f"ERROR: Could not fetch weather for {city}. "
            f"Details: {e}"
        )

        return None


# ---------------------------------------------------------------
# STEP 2: VALIDATE AND TRANSFORM DATA
# ---------------------------------------------------------------

def validate_and_extract(data, city):

    if data is None:

        print(
            f"No data available for {city}. "
            f"Skipping."
        )

        return None

    try:

        weather = data["current_weather"]

        temperature = weather["temperature"]

        windspeed = weather["windspeed"]

        recorded_time = weather["time"]

    except KeyError as e:

        print(
            f"ERROR: Missing field {e} "
            f"for {city}"
        )

        return None


    # -----------------------------------------------------------
    # TEMPERATURE VALIDATION
    # -----------------------------------------------------------

    if not (-90 <= temperature <= 60):

        print(
            f"WARNING: Invalid temperature "
            f"{temperature} for {city}"
        )

        return None


    # -----------------------------------------------------------
    # WINDSPEED VALIDATION
    # -----------------------------------------------------------

    if windspeed < 0:

        print(
            f"WARNING: Invalid windspeed "
            f"{windspeed} for {city}"
        )

        return None


    # -----------------------------------------------------------
    # TIMESTAMP TRANSFORMATION
    # -----------------------------------------------------------

    try:

        recorded_time = datetime.strptime(
            recorded_time,
            "%Y-%m-%dT%H:%M"
        )

    except ValueError as e:

        print(
            f"WARNING: Invalid timestamp "
            f"for {city}. Details: {e}"
        )

        return None


    # -----------------------------------------------------------
    # CLEAN RECORD
    # -----------------------------------------------------------

    record = {

        "city": city,

        "temperature": temperature,

        "windspeed": windspeed,

        "recorded_time": recorded_time

    }


    print(
        f"Validated -> "
        f"{city} | "
        f"{temperature}°C | "
        f"{windspeed} km/h | "
        f"{recorded_time}"
    )

    return record


# ---------------------------------------------------------------
# STEP 3: CONNECT TO SQL SERVER
# ---------------------------------------------------------------

def get_database_connection():

    connection_string = (

        "DRIVER={ODBC Driver 17 for SQL Server};"

        f"SERVER={SQL_SERVER};"

        f"DATABASE={SQL_DATABASE};"

        "Trusted_Connection=yes;"

    )

    return pyodbc.connect(connection_string)


# ---------------------------------------------------------------
# STEP 4: LOAD DATA INTO SQL SERVER
# ---------------------------------------------------------------

def save_to_database(record):

    if record is None:

        return


    try:

        conn = get_database_connection()

        cursor = conn.cursor()


        # -------------------------------------------------------
        # CHECK FOR DUPLICATE
        # -------------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM WeatherData
            WHERE city = ?
              AND recorded_time = ?
            """,
            record["city"],
            record["recorded_time"]
        )

        count = cursor.fetchone()[0]


        if count > 0:

            print(
                f"Duplicate found for "
                f"{record['city']} at "
                f"{record['recorded_time']}. "
                f"Skipping."
            )

            conn.close()

            return


        # -------------------------------------------------------
        # INSERT RECORD
        # -------------------------------------------------------

        cursor.execute(
            """
            INSERT INTO WeatherData
            (
                city,
                temperature,
                windspeed,
                recorded_time
            )
            VALUES (?, ?, ?, ?)
            """,

            record["city"],

            record["temperature"],

            record["windspeed"],

            record["recorded_time"]
        )


        conn.commit()

        conn.close()


        print(
            f"Saved to SQL Server -> "
            f"{record['city']}"
        )


    except pyodbc.Error as e:

        print(
            f"ERROR: Database operation failed. "
            f"Details: {e}"
        )


# ---------------------------------------------------------------
# STEP 5: MAIN PIPELINE
# ---------------------------------------------------------------

def run_pipeline():

    print("=" * 60)

    print(
        f"Pipeline started at "
        f"{datetime.now()}"
    )

    print("=" * 60)


    for city_config in CITIES:

        city = city_config["city"]


        # EXTRACT

        raw_data = fetch_weather_data(
            city_config
        )


        # TRANSFORM + VALIDATE

        clean_record = validate_and_extract(
            raw_data,
            city
        )


        # LOAD

        save_to_database(
            clean_record
        )


    print("=" * 60)

    print("Pipeline finished.")

    print("=" * 60)


# ---------------------------------------------------------------
# PROGRAM ENTRY POINT
# ---------------------------------------------------------------

if __name__ == "__main__":

    run_pipeline()