import json 
import requests
import time
import urllib 
import ConfigParser
import logging

TOKEN = ""
POLLING_TIMEOUT = None

# Lambda functions to parse updates
def getText(update):            return update["message"]["text"]
def getChatId(update):          return update["message"]["chat"]["id"]
def getUpId(update):            return int(update["update_id"])
def getResult(updates):         return updates["result"]

logger = logging.getLogger("LanaBot")
logger.setLevel(logging.DEBUG)

# Configure file and console logging
def configLogging():
    # Create file logger and set level to DEBUG
    # Mode = write -> clear existing log file
    handler = logging.FileHandler('run.log', mode='w')
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Create console handler and set level to INFO
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(levelname)s] - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

# Read settings from configuration file
def parseConfig():
    global URL, POLLING_TIMEOUT
    
    c = ConfigParser.ConfigParser()
    c.read('config.ini')
    TOKEN = c.get('Settings', 'TOKEN')
    logger.debug("Token: %s" % TOKEN)
    URL = "https://api.telegram.org/bot{}/".format(TOKEN)
    POLLING_TIMEOUT = c.get('Settings', 'POLLING_TIMEOUT')
    logger.debug("Polling interval: %s" % POLLING_TIMEOUT)

# Make a request to Telegram bot and get JSON response
def makeRequest(url):
    logger.debug("URL: %s" % url)
    r = requests.get(url)
    resp = json.loads(r.content.decode("utf8"))
    return resp

# Return all the updates with ID > offset
# Updates list kept by Telegram for 24h
def getUpdates(offset=None):
    url = URL + "getUpdates?timeout=%s" % POLLING_TIMEOUT
    logger.info("Getting updates") 
    if offset:
        url += "&offset={}".format(offset)
    js = makeRequest(url)
    return js

# Send URL-encoded message to chat id
def sendMessage(text, chatId):
    text = urllib.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chatId)
    requests.get(url)

# Get the ID of the last available update
def getLastUpdateId(updates):
    ids = []
    for update in getResult(updates):
        ids.append(getUpId(update))
    return max(ids)

# Echo all messages back
def echoAll(updates):
    for update in getResult(updates):
        text = getText(update)
        chatId = getChatId(update)
        sendMessage(text, chatId)

def main():
    configLogging()

    parseConfig()
   
    with open("banner") as f:
        data = f.read()
        print data
 
    last_update_id = None
    while True:
        updates = getUpdates(last_update_id)
        if len(getResult(updates)) > 0:
            last_update_id = getLastUpdateId(updates) + 1
            echoAll(updates)
        time.sleep(0.5)

if __name__ == "__main__":
    main()

