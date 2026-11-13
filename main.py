import aiohttp
import asyncio
import json
from urllib.parse import urlparse, parse_qs, urlencode


from config import (
    HEADERS,
    GDOC_URL,
)  # i spent a good 10 minutes hand formatting the curl headers into a python dict. So, you don't get it. jkjk, its cuz there are secrets.

# todo - put it in .env

parsed_url = urlparse(GDOC_URL)
params = parse_qs(parsed_url.query)
SID = params["sid"][0]
# print(SID)
# print(GDOC_URL)  # gdoc url is stable across allrequests i've tried, seems obvious
# cookie  isn't stable between requets, but we just hope it works.


def make_raw_data(rev, commands, gdoc_url=GDOC_URL, sid=SID):
    # rev=24&bundles=[{"commands":[{"ty":"ds","si":4,"ei":5}],"sid":"","reqId":3}]
    # rev=23&bundles=[{"commands":[{"ty":"is","ibi":3,"s":"y"}],"sid":"","reqId":5}]
    bundles_list = [
        {
            "commands": commands,
            "sid": sid,
            "reqId": 5,
        }
    ]

    data = {
        "rev": rev,
        "bundles": json.dumps(bundles_list, separators=(",", ":")),
    }
    return urlencode(data)


async def main():

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        # you gotta update this every time you run it unfortunately - I haven't found the api route yet, haven't tried. Probs in an init request on doc page load?
        current_revision = 667
        while True:
            text = "a" * 5000
            insert_command = make_raw_data(
                current_revision, [{"ty": "is", "ibi": 3, "s": text}]
            )
            async with session.post(GDOC_URL, data=insert_command) as response:

                print("Status:", response.status)
                print("Content-type:", response.headers["content-type"])
                body = await response.text()
                print(
                    body
                )  # todo: parse this to get the current revision, store in json
            await asyncio.sleep(1)
            current_revision += 1


asyncio.run(main())
