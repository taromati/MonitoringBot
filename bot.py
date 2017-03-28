import http.client
import os
from slackclient import SlackClient
from time import sleep

BOT_ID = os.environ.get("BOT_ID")
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
CHANNEL = os.environ.get("CHANNEL")

DEV_DOMAIN = os.environ.get("DEV_DOMAIN")
LIVE_DOMAIN = os.environ.get("LIVE_DOMAIN")
CHECK_PATH = os.environ.get("CHECK_PATH")

dev_status = False
live_status = False


def check(domain: str,
          method: str = "GET",
          path: str = "/",
          port: int = http.client.HTTP_PORT,
          timeout: int = 10) -> (bool, int):
    conn = http.client.HTTPSConnection(domain, port, timeout=timeout)
    conn.request(method, path)
    response = conn.getresponse()
    print(response.status)
    return response.status == http.HTTPStatus.OK, response.status


def send_message(message: str):
    slack_client.api_call("chat.postMessage",
                          channel=CHANNEL,
                          text=message,
                          as_user=True)


def bot_proc(prev_status: bool, domain: str, path: str):
    (result, status_code) = check(domain, path=path, port=http.client.HTTPS_PORT)
    if result != prev_status:
        text = "[ " + domain + " ] is " + (result and "alive" or "dead, [" + status_code + "]")
        send_message(text)

    return result


if __name__ == "__main__":
    try:
        send_message("Start watching server")

        slack_client = SlackClient(SLACK_BOT_TOKEN)

        while True:
            dev_status = bot_proc(dev_status, DEV_DOMAIN, CHECK_PATH)
            live_status = bot_proc(live_status, LIVE_DOMAIN, CHECK_PATH)
            sleep(10)
    finally:
        send_message("I'm dying")
