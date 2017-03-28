import http.client
import os
from slackclient import SlackClient
from time import sleep


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


def send_message(client: SlackClient, message: str):
    client.api_call("chat.postMessage",
                    channel=CHANNEL,
                    text=message,
                    as_user=True)


def bot_proc(client: SlackClient, prev_status: bool, domain: str, path: str):
    (result, status_code) = check(domain, path=path, port=http.client.HTTPS_PORT)
    if result != prev_status:
        text = "[ " + domain + " ] is " + (result and "alive" or "dead, [" + status_code + "]")
        send_message(client, text)

    return result


if __name__ == "__main__":
    BOT_ID = os.environ.get("BOT_ID")
    print("BOT_ID: " + BOT_ID)
    SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
    print("SLACK_BOT_TOKEN: " + SLACK_BOT_TOKEN)
    CHANNEL = os.environ.get("CHANNEL")
    print("CHANNEL: " + CHANNEL)

    DEV_DOMAIN = os.environ.get("DEV_DOMAIN")
    print("DEV_DOMAIN: " + DEV_DOMAIN)
    LIVE_DOMAIN = os.environ.get("LIVE_DOMAIN")
    print("LIVE_DOMAIN: " + LIVE_DOMAIN)
    CHECK_PATH = os.environ.get("CHECK_PATH")
    print("CHECK_PATH: " + CHECK_PATH)

    if BOT_ID is None and SLACK_BOT_TOKEN is None and CHANNEL is None and DEV_DOMAIN is None and LIVE_DOMAIN is None and CHECK_PATH is None:
        print("error")
        exit(1)

    slack_client = SlackClient(SLACK_BOT_TOKEN)

    try:
        dev_status = False
        live_status = False

        send_message(slack_client, "Start watching server")

        while True:
            dev_status = bot_proc(slack_client, dev_status, DEV_DOMAIN, CHECK_PATH)
            live_status = bot_proc(slack_client, live_status, LIVE_DOMAIN, CHECK_PATH)
            sleep(10)
    finally:
        send_message(slack_client, "I'm dying")
