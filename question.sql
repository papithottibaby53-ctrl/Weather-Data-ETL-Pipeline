CREATE DATABASE Weather;

drop table WeatherData ;
USE Weather;


CREATE TABLE WeatherData (
    id INT IDENTITY(1,1) PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    temperature DECIMAL(5,2) NOT NULL,
    windspeed DECIMAL(6,2) NOT NULL,
    recorded_time DATETIME NOT NULL,

    CONSTRAINT UQ_Weather_City_Time
        UNIQUE (city, recorded_time)
);


select * from WeatherData ;

select * from WeatherData ;