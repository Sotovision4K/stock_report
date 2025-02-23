import logging
import azure.functions as func
import datetime
import requests
from dotenv import load_dotenv
import os
from json import dumps

app = func.FunctionApp()

TICKERS = os.getenv("Tickers").split(",")


def group_response(data):
    result_list = []
    counter = 0
    for stock in data["results"]:
        if stock["T"] in TICKERS:
            result_list.append(stock)
            counter += 1
        if counter == len(TICKERS):
            break
        
    return result_list

@app.cosmos_db_output(arg_name="outputDocument", 
                      database_name="stocks", 
                    container_name="Stocks", 
                    connection="CosmosDbConnectionSetting")
@app.timer_trigger(schedule="*/2 * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def timer_trigger(myTimer: func.TimerRequest,
    outputDocument: func.Out[func.Document]) -> None:
    logging.info('Starting the timer...')
    yesterday = datetime.datetime.now() - datetime.timedelta(days=2)
    yesterday = yesterday.strftime('%Y-%m-%d')
    url = f"https://api.polygon.io/v2/aggs/grouped/locale/us/market/stocks/2025-02-07?adjusted=true&apiKey={os.getenv('API_KEY')}"
    response = requests.get(url)
    data = response.json()
    message = group_response(data)
    logging.info(dumps(message) + "stocks to add to the database")
    outputDocument.set(func.Document.from_dict({"id": yesterday, "message": message}))
    logging.info("Document added to the database")

    if myTimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function executed.')
