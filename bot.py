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
    if prev_status is None or result != prev_status:
        text = "[ " + domain + " ] is " \
               + (result and "alive" or "dead:[" + str(status_code) + "], Fix it immediately!")
        send_message(client, text)

    return result


if __name__ == "__main__":
    print("main start")

    BOT_ID = os.environ.get("BOT_ID")
    SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
    CHANNEL = os.environ.get("CHANNEL")

    DEV_DOMAIN = os.environ.get("DEV_DOMAIN")
    LIVE_DOMAIN = os.environ.get("LIVE_DOMAIN")
    CHECK_PATH = os.environ.get("CHECK_PATH")

    if BOT_ID is None and SLACK_BOT_TOKEN is None and CHANNEL is None and DEV_DOMAIN is None and LIVE_DOMAIN is None and CHECK_PATH is None:
        print("error")
        exit(1)

    slack_client = SlackClient(SLACK_BOT_TOKEN)

    try:
        dev_status: bool = None
        live_status: bool = None

        send_message(slack_client, "Start watching server")

        while True:
            dev_status = bot_proc(slack_client, dev_status, DEV_DOMAIN, CHECK_PATH)
            live_status = bot_proc(slack_client, live_status, LIVE_DOMAIN, CHECK_PATH)
            sleep(10)
    except Exception as err:
        print(str(err))
    finally:
        send_message(slack_client, "I'm dying")
