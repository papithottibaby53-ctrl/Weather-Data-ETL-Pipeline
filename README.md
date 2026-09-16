# 🌦️ Weather Data ETL Pipeline

An end-to-end Python ETL pipeline that extracts real-time weather data from the Open-Meteo API, validates and transforms the data, and loads the cleaned records into Microsoft SQL Server.

---

## 📌 Project Overview

This project demonstrates a simple but production-oriented ETL workflow:

**Extract → Validate → Transform → Load**

The pipeline retrieves weather information from an external REST API, performs basic data quality checks, converts the timestamp into a database-compatible format, and stores the final data in SQL Server.

### Pipeline Flow

```text
Open-Meteo API
      ↓
   Python
      ↓
 API Extraction
      ↓
 Data Validation
      ↓
 Data Transformation
      ↓
 SQL Server
      ↓
 WeatherData Table
```

---

## 🎯 Project Objectives

The main objectives of this project are:

* Extract weather data from a REST API
* Handle API failures and connection errors
* Validate incoming weather data
* Detect invalid temperature and wind-speed values
* Convert API timestamps into Python datetime objects
* Load validated data into SQL Server
* Implement basic error handling and logging through pipeline messages
* Demonstrate an end-to-end ETL workflow using Python and SQL

---

## 🛠️ Technologies Used

| Technology | Purpose                                |
| ---------- | -------------------------------------- |
| Python     | ETL development                        |
| Requests   | API data extraction                    |
| PyODBC     | SQL Server connectivity                |
| SQL Server | Data storage                           |
| SQL        | Data insertion and database operations |
| Git/GitHub | Version control                        |

---

## 🏗️ Architecture

```text
                 ┌───────────────────┐
                 │  Open-Meteo API   │
                 └─────────┬─────────┘
                           │
                           │ REST API
                           ▼
                 ┌───────────────────┐
                 │ Python ETL Script │
                 └─────────┬─────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
      Data Extraction             Data Validation
                                      │
                                      ▼
                              Data Transformation
                                      │
                                      ▼
                              ┌───────────────┐
                              │  SQL Server   │
                              │   Weather DB  │
                              └───────┬───────┘
                                      │
                                      ▼
                              WeatherData Table
```

---

# 📥 1. Data Extraction

The pipeline uses the Open-Meteo REST API to retrieve current weather information.

Example API endpoint:

```text
https://api.open-meteo.com/v1/forecast
```

The API provides information including:

* Temperature
* Wind speed
* Observation time

Python's `requests` library is used to make the HTTP GET request.

```python
response = requests.get(API_URL, timeout=10)
response.raise_for_status()
```

A timeout is used to prevent the pipeline from waiting indefinitely for an API response.

---

# 🔍 2. Data Validation

After receiving the API response, the pipeline extracts the required fields:

```python
temperature
windspeed
recorded_time
```

Basic data quality rules are applied.

### Temperature validation

```python
if not (-90 <= temperature <= 60):
    return None
```

Records with unrealistic temperature values are rejected.

### Wind-speed validation

```python
if windspeed < 0:
    return None
```

Negative wind-speed values are rejected.

### Timestamp validation

The API returns the timestamp as text:

```text
2026-09-16T15:00
```

The pipeline converts it into a Python datetime object:

```python
datetime.strptime(
    recorded_time,
    "%Y-%m-%dT%H:%M"
)
```

---

# 🔄 3. Data Transformation

The raw API response is transformed into a clean Python dictionary:

```python
{
    "temperature": temperature,
    "windspeed": windspeed,
    "recorded_time": recorded_time
}
```

This creates a consistent structure before loading the data into SQL Server.

---

# 🗄️ 4. Data Loading

The cleaned record is inserted into SQL Server using PyODBC.

```python
cursor.execute(
    """
    INSERT INTO WeatherData
    (temperature, windspeed, recorded_time)
    VALUES (?, ?, ?)
    """,
    record["temperature"],
    record["windspeed"],
    record["recorded_time"]
)
```

The transaction is committed using:

```python
conn.commit()
```

---

# 🗃️ Database Schema

The project uses a `WeatherData` table.

Example:

```sql
CREATE TABLE WeatherData (
    id INT IDENTITY(1,1) PRIMARY KEY,
    temperature FLOAT,
    windspeed FLOAT,
    recorded_time DATETIME
);
```

Example records:

| id | temperature | windspeed | recorded_time       |
| -: | ----------: | --------: | ------------------- |
|  1 |        24.5 |      10.2 | 2026-09-16 15:00:00 |
|  2 |        25.1 |       8.7 | 2026-09-16 16:00:00 |

---

# ⚠️ Error Handling

The pipeline handles errors at multiple stages.

### API errors

```python
try:
    response = requests.get(API_URL, timeout=10)
except requests.exceptions.RequestException:
    ...
```

Handles issues such as:

* API unavailable
* Network failure
* Timeout
* HTTP errors

### Missing API fields

```python
except KeyError:
    ...
```

Prevents the pipeline from processing incomplete API responses.

### Invalid data

Invalid temperature, wind speed, or timestamps are rejected before database insertion.

### Database errors

```python
except pyodbc.Error as e:
    ...
```

Handles SQL Server connection and query errors.

---

# 🚀 Installation

## 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/weather-etl-pipeline.git
```

```bash
cd weather-etl-pipeline
```

## 2. Create a virtual environment

Windows:

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

`requirements.txt`:

```text
requests
pyodbc
```

---

# 🔧 Configuration

Update the following values in the Python script:

```python
API_URL = "YOUR_API_URL"

SQL_SERVER = r"YOUR_SQL_SERVER"

SQL_DATABASE = "Weather"
```

The project currently uses Windows/Trusted Authentication for SQL Server:

```text
Trusted_Connection=yes;
```

Make sure SQL Server is running and the `Weather` database exists.

---

# ▶️ Running the Pipeline

Run:

```bash
python src/weather_pipeline.py
```

Expected output:

```text
==================================================
Pipeline started at 2026-09-16 21:59:10
==================================================

Requesting data from API...
Data received successfully.

Validated data -> Temp: 24.5°C, Wind: 10.2 km/h,
Time: 2026-09-16 15:00:00

Record saved to SQL Server successfully.

==================================================
Pipeline finished.
==================================================
```

---

# 📊 Data Flow

The complete data flow is:

```text
REST API
   ↓
JSON Response
   ↓
Python requests
   ↓
Raw Data
   ↓
Validation
   ↓
Transformation
   ↓
Clean Record
   ↓
PyODBC
   ↓
SQL Server
   ↓
WeatherData
```

---

# 📁 Project Structure

```text
weather-etl-pipeline/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── src/
│   └── weather_pipeline.py
│
├── sql/
│   └── create_tables.sql
│
├── screenshots/
│   ├── api_response.png
│   ├── pipeline_output.png
│   └── sql_table.png
│
└── docs/
    └── architecture.png
```

---

# 💡 Key Data Engineering Concepts Demonstrated

This project demonstrates practical understanding of:

* REST API ingestion
* ETL pipeline design
* JSON processing
* Data validation
* Data transformation
* Error handling
* SQL Server
* Database connectivity
* Parameterized SQL queries
* Python functions
* Transaction management
* Basic data quality checks

---

# 🔮 Future Improvements

The current project is intentionally simple. Future versions could include:

### Version 2

* Add multiple cities
* Store latitude and longitude
* Add weather conditions
* Add API response logging
* Add duplicate detection

### Version 3

* Schedule the pipeline using Apache Airflow
* Store raw JSON files in Amazon S3
* Create a staging layer
* Implement incremental loading
* Add retry mechanisms
* Add structured logging

### Version 4

```text
Open-Meteo API
       ↓
Python
       ↓
Amazon S3
       ↓
Apache Airflow
       ↓
Transformation
       ↓
Amazon Redshift
       ↓
Power BI
```

This would turn the project into a more complete cloud-based data engineering pipeline.

---

# 👨‍💻 Skills Demonstrated

**Languages:** Python, SQL

**Data Engineering:** ETL, Data Validation, Data Transformation, API Integration

**Database:** Microsoft SQL Server

**Libraries:** Requests, PyODBC

**Tools:** Git, GitHub

---

## 📌 Resume Project Description

**Weather Data ETL Pipeline | Python, REST API, SQL Server**

Developed an end-to-end ETL pipeline using Python to extract real-time weather data from a REST API, perform data quality validation and timestamp transformations, and load structured records into SQL Server using PyODBC. Implemented API/database error handling and parameterized SQL inserts to create a reliable data ingestion workflow.
