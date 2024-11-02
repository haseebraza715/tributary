# import dependencies
import json
import redis as redis
from flask import Flask, request
from loguru import logger

# define constants
HISTORY_LENGTH = 10
DATA_KEY = "engine_temperature"

# create a Flask server, and allow us to interact with it using the app variable
app = Flask(__name__)


# define an endpoint which accepts POST requests, and is reachable from the /record endpoint
@app.route('/record', methods=['POST'])
def record_engine_temperature():
    payload = request.get_json(force=True)
    logger.info(f"(*) record request --- {json.dumps(payload)} (*)")

    engine_temperature = payload.get("engine_temperature")
    logger.info(f"engine temperature to record is: {engine_temperature}")

    database = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)
    database.lpush(DATA_KEY, engine_temperature)
    logger.info(f"stashed engine temperature in redis: {engine_temperature}")

    while database.llen(DATA_KEY) > HISTORY_LENGTH:
        database.rpop(DATA_KEY)
    engine_temperature_values = database.lrange(DATA_KEY, 0, -1)
    logger.info(f"engine temperature list now contains these values: {engine_temperature_values}")

    logger.info(f"record request successful")
    return {"success": True}, 200


# we'll implement this in the next step!
@app.route('/collect', methods=['POST'])
def collect_engine_temperature():
    # Parse the incoming JSON data
    load = request.get_json(force=True)
    logger.info(f"(*) record request --- {json.dumps(load)} (*)")

    # Retrieve the temperature reading
    engine_temperature = load.get("engine_temperature")

    # Connect to Redis
    database = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)

    # Store the current temperature in Redis
    database.lpush(DATA_KEY, engine_temperature)
    logger.info(f"Stashed engine temperature in Redis: {engine_temperature}")

    # Maintain the list to the defined HISTORY_LENGTH
    while database.llen(DATA_KEY) > HISTORY_LENGTH:
        database.rpop(DATA_KEY)

    # Retrieve all stored temperature values and convert them to floats
    engine_temperature_values = list(map(float, database.lrange(DATA_KEY, 0, -1)))

    # Get the most recent temperature
    engine_temperature_current = engine_temperature_values[0]
    logger.info(f"Current value of temperature is: {engine_temperature_current}")

    # Calculate the average temperature
    average_engine_temperature = sum(engine_temperature_values) / len(engine_temperature_values)
    logger.info(f"Average engine temperature is: {average_engine_temperature}")

    # Return the current and average temperatures
    return {
        "current_engine_temperature": engine_temperature_current,
        "average_engine_temperature": average_engine_temperature,
        "success": True
    }, 200


