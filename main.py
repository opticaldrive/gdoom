import aiohttp
import asyncio
import json
from urllib.parse import urlparse, parse_qs, urlencode
import random
import hashlib, time

from config import (
    HEADERS,
    GDOC_URL,
)  # i spent a good 10 minutes hand formatting the curl headers into a python dict. So, you don't get it. jkjk, its cuz there are secrets.

import re


from playwright_cookiejar import refresh_creds

parsed_url = urlparse(GDOC_URL)
params = parse_qs(parsed_url.query)
SID = params["sid"][0]

CONFIG_PATH = "config.json"  # im tired of hardocing revisions :p
# ton of copy pastintg snippets sorry

JSON_PATH = "bad_apple.json"

ORIGIN = f"{urlparse(GDOC_URL).scheme}://{urlparse(GDOC_URL).netloc}"  # idk why not just hardcpde

TARGET_FPS = 20
period = 1 / TARGET_FPS


def parse_rev_from_post_data(post_data: str) -> int | None:
    m = re.search(r"(?:^|&)rev=(\d+)", post_data)  # i (hope) deepseek did it right
    return int(m.group(1)) if m else None


def save_config(save_request, index=None, rev=None):
    config = load_config() or {}
    config["save_request"] = save_request
    if index is not None:
        config["index"] = index
    if rev is not None:
        config["revision"] = rev
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)


def load_config():
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def _cookie(name):
    raw = HEADERS.get("cookie") or HEADERS.get("Cookie") or ""
    for part in raw.split(";"):
        k, _, v = part.strip().partition("=")
        if k == name:
            return v
    return None


# this didn't help so i might as well delete it later

SAPISID = _cookie("SAPISID")
assert SAPISID, "SAPISID cookie not found in HEADERS"


def sapisidhash(ts=None):
    ts = ts or int(time.time())
    digest = hashlib.sha1(f"{ts} {SAPISID} {ORIGIN}".encode()).hexdigest()
    return f"SAPISIDHASH {ts}_{digest}"


def make_raw_data(rev, commands, gdoc_url=GDOC_URL, sid=SID, reqId=1):
    # rev=24&bundles=[{"commands":[{"ty":"ds","si":4,"ei":5}],"sid":"","reqId":3}]
    # rev=23&bundles=[{"commands":[{"ty":"is","ibi":3,"s":"y"}],"sid":"","reqId":5}]
    # rev=682&bundles=%5B%7B%22commands%22%3A%5B%7B%22ty%22%3A%22mlti%22%2C%22mts%22%3A%5B%7B%22ty%22%3A%22is%22%2C%22ibi%22%3A18%2C%22s%22%3A%22This%20text%20is%20red%22%7D%2C%7B%22ty%22%3A%22as%22%2C%22st%22%3A%22text%22%2C%22si%22%3A18%2C%22ei%22%3A33%2C%22sm%22%3A%7B%22ts_bd_i%22%3Atrue%2C%22ts_fs_i%22%3Atrue%2C%22ts_ff_i%22%3Afalse%2C%22ts_ff%22%3A%22Noto%20Sans%20Mono%22%2C%22ts_it_i%22%3Atrue%2C%22ts_sc_i%22%3Atrue%2C%22ts_st_i%22%3Atrue%2C%22ts_tw%22%3A400%2C%22ts_un_i%22%3Atrue%2C%22ts_va_i%22%3Atrue%2C%22ts_bgc2_i%22%3Atrue%2C%22ts_fgc2_i%22%3Afalse%2C%22ts_fgc2%22%3A%7B%22clr_type%22%3A0%2C%22hclr_color%22%3A%22%23ff0000%22%7D%7D%7D%2C%7B%22ty%22%3A%22as%22%2C%22st%22%3A%22paragraph%22%2C%22si%22%3A34%2C%22ei%22%3A34%2C%22sm%22%3A%7B%22ps_al_i%22%3Atrue%2C%22ps_awao_i%22%3Atrue%2C%22ps_sd_i%22%3Atrue%2C%22ps_bbtw_i%22%3Atrue%2C%22ps_bb_i%22%3Atrue%2C%22ps_bl_i%22%3Atrue%2C%22ps_br_i%22%3Atrue%2C%22ps_bt_i%22%3Atrue%2C%22ps_hd%22%3A0%2C%22ps_hdid%22%3A%22%22%2C%22ps_ifl_i%22%3Atrue%2C%22ps_il_i%22%3Atrue%2C%22ps_ir_i%22%3Atrue%2C%22ps_klt_i%22%3Atrue%2C%22ps_kwn_i%22%3Atrue%2C%22ps_ltr%22%3Atrue%2C%22ps_ls_i%22%3Afalse%2C%22ps_ls%22%3A1%2C%22ps_lslm_i%22%3Atrue%2C%22ps_pbb_i%22%3Atrue%2C%22ps_sm_i%22%3Atrue%2C%22ps_sa_i%22%3Atrue%2C%22ps_sb_i%22%3Atrue%2C%22ps_rd%22%3A%22%22%2C%22ps_shd%22%3Afalse%2C%22ps_ts%22%3A%7B%22cv%22%3A%7B%22op%22%3A%22set%22%2C%22opValue%22%3A%5B%5D%7D%7D%7D%7D%2C%7B%22ty%22%3A%22as%22%2C%22st%22%3A%22bookmark_range%22%2C%22si%22%3A18%2C%22ei%22%3A33%2C%22sm%22%3A%7B%22brs_id%22%3A%7B%22cv%22%3A%7B%22op%22%3A%22set%22%2C%22opValue%22%3A%5B%5D%7D%7D%7D%7D%2C%7B%22ty%22%3A%22as%22%2C%22st%22%3A%22comment%22%2C%22si%22%3A18%2C%22ei%22%3A33%2C%22sm%22%3A%7B%22cs_cids%22%3A%7B%22cv%22%3A%7B%22op%22%3A%22set%22%2C%22opValue%22%3A%5B%5D%7D%7D%7D%7D%2C%7B%22ty%22%3A%22as%22%2C%22st%22%3A%22doco_anchor%22%2C%22si%22%3A18%2C%22ei%22%3A33%2C%22sm%22%3A%7B%22das_a%22%3A%7B%22cv%22%3A%7B%22op%22%3A%22set%22%2C%22opValue%22%3A%5B%5D%7D%7D%7D%7D%2C%7B%22ty%22%3A%22as%22%2C%22st%22%3A%22ignore_spellcheck%22%2C%22si%22%3A18%2C%22ei%22%3A33%2C%22sm%22%3A%7B%22isc_osh%22%3Anull%2C%22isc_smer%22%3Atrue%7D%7D%2C%7B%22ty%22%3A%22as%22%2C%22st%22%3A%22import_warnings%22%2C%22si%22%3A18%2C%22ei%22%3A33%2C%22sm%22%3A%7B%22iws_iwids%22%3A%7B%22cv%22%3A%7B%22op%22%3A%22set%22%2C%22opValue%22%3A%5B%5D%7D%7D%7D%7D%2C%7B%22ty%22%3A%22as%22%2C%22st%22%3A%22link%22%2C%22si%22%3A18%2C%22ei%22%3A33%2C%22sm%22%3A%7B%22lnks_link%22%3Anull%7D%7D%2C%7B%22ty%22%3A%22as%22%2C%22st%22%3A%22text%22%2C%22si%22%3A18%2C%22ei%22%3A33%2C%22sm%22%3A%7B%22ts_bd_i%22%3Atrue%2C%22ts_fs_i%22%3Atrue%2C%22ts_ff_i%22%3Afalse%2C%22ts_ff%22%3A%22Noto%20Sans%20Mono%22%2C%22ts_it_i%22%3Atrue%2C%22ts_sc_i%22%3Atrue%2C%22ts_st_i%22%3Atrue%2C%22ts_tw%22%3A400%2C%22ts_un_i%22%3Atrue%2C%22ts_va_i%22%3Atrue%2C%22ts_bgc2_i%22%3Atrue%2C%22ts_fgc2_i%22%3Afalse%2C%22ts_fgc2%22%3A%7B%22clr_type%22%3A0%2C%22hclr_color%22%3A%22%23ff0000%22%7D%7D%7D%5D%7D%5D%2C%22sid%22%3A%22oops%22%2C%22reqId%22%3A0%7D%5D
    # rev=706&bundles=%5B%7B%22commands%22%3A%5B%7B%22ty%22%3A%22mlti%22%2C%22mts%22%3A%5B%7B%22ty%22%3A%22is%22%2C%22ibi%22%3A79%2C%22s%22%3A%22The%20background%20of%20this%20text%20is%20red%2C%20too%5Cn%22%7D%2C%7B%22ty%22%3A%22as%22%2C%22st%22%3A%22paragraph%22%2C%22si%22%3A118%2C%22ei%22%3A118%2C%22sm%22%3A%7B%22ps_al%22%3A0%2C%22ps_awao%22%3Afalse%2C%22ps_sd%22%3Anull%2C%22ps_bbtw%22%3Anull%2C%22ps_bb%22%3Anull%2C%22ps_bl%22%3Anull%2C%22ps_br%22%3Anull%2C%22ps_bt%22%3Anull%2C%22ps_hd%22%3A0%2C%22ps_hdid%22%3A%22%22%2C%22ps_ifl%22%3A0%2C%22ps_il%22%3A0%2C%22ps_ir%22%3A0%2C%22ps_klt%22%3Afalse%2C%22ps_kwn%22%3Afalse%2C%22ps_ltr%22%3Atrue%2C%22ps_ls%22%3A1%2C%22ps_lslm%22%3A1%2C%22ps_pbb%22%3Afalse%2C%22ps_sm%22%3A0%2C%22ps_sa%22%3A0%2C%22ps_sb%22%3A0%2C%22ps_al_i%22%3Atrue%2C%22ps_awao_i%22%3Atrue%2C%22ps_sd_i%22%3Atrue%2C%22ps_bbtw_i%22%3Atrue%2C%22ps_bb_i%22%3Atrue%2C%22ps_bl_i%22%3Atrue%2C%22ps_br_i%22%3Atrue%2C%22ps_bt_i%22%3Atrue%2C%22ps_ifl_i%22%3Atrue%2C%22ps_il_i%22%3Atrue%2C%22ps_ir_i%22%3Atrue%2C%22ps_klt_i%22%3Atrue%2C%22ps_kwn_i%22%3Atrue%2C%22ps_ls_i%22%3Afalse%2C%22ps_lslm_i%22%3Atrue%2C%22ps_pbb_i%22%3Atrue%2C%22ps_rd%22%3A%22%22%2C%22ps_sm_i%22%3Atrue%2C%22ps_sa_i%22%3Atrue%2C%22ps_sb_i%22%3Atrue%2C%22ps_shd%22%3Afalse%2C%22ps_ts%22%3A%7B%22cv%22%3A%7B%22op%22%3A%22set%22%2C%22opValue%22%3A%5B%5D%7D%7D%7D%7D%2C%7B%22ty%22%3A%22as%22%2C%22st%22%3A%22text%22%2C%22si%22%3A79%2C%22ei%22%3A118%2C%22sm%22%3A%7B%22ts_bd_i%22%3Atrue%2C%22ts_fs_i%22%3Atrue%2C%22ts_ff_i%22%3Afalse%2C%22ts_ff%22%3A%22Noto%20Sans%20Mono%22%2C%22ts_it_i%22%3Atrue%2C%22ts_sc_i%22%3Atrue%2C%22ts_st_i%22%3Atrue%2C%22ts_tw%22%3A400%2C%22ts_un_i%22%3Atrue%2C%22ts_va_i%22%3Atrue%2C%22ts_bgc2_i%22%3Afalse%2C%22ts_bgc2%22%3A%7B%22clr_type%22%3A0%2C%22hclr_color%22%3A%22%23ff0000%22%7D%2C%22ts_fgc2_i%22%3Afalse%2C%22ts_fgc2%22%3A%7B%22clr_type%22%3A0%2C%22hclr_color%22%3A%22%23ff0000%22%7D%7D%7D%2C%7B%22ty%22%3A%22as%22%2C%22st%22%3A%22bookmark_range%22%2C%22si%22%3A79%2C%22ei%22%3A118%2C%22sm%22%3A%7B%22brs_id%22%3A%7B%22cv%22%3A%7B%22op%22%3A%22set%22%2C%22opValue%22%3A%5B%5D%7D%7D%7D%7D%2C%7B%22ty%22%3A%22as%22%2C%22st%22%3A%22comment%22%2C%22si%22%3A79%2C%22ei%22%3A118%2C%22sm%22%3A%7B%22cs_cids%22%3A%7B%22cv%22%3A%7B%22op%22%3A%22set%22%2C%22opValue%22%3A%5B%5D%7D%7D%7D%7D%2C%7B%22ty%22%3A%22as%22%2C%22st%22%3A%22doco_anchor%22%2C%22si%22%3A79%2C%22ei%22%3A118%2C%22sm%22%3A%7B%22das_a%22%3A%7B%22cv%22%3A%7B%22op%22%3A%22set%22%2C%22opValue%22%3A%5B%5D%7D%7D%7D%7D%2C%7B%22ty%22%3A%22as%22%2C%22st%22%3A%22ignore_spellcheck%22%2C%22si%22%3A79%2C%22ei%22%3A118%2C%22sm%22%3A%7B%22isc_osh%22%3Anull%2C%22isc_smer%22%3Atrue%7D%7D%2C%7B%22ty%22%3A%22as%22%2C%22st%22%3A%22import_warnings%22%2C%22si%22%3A79%2C%22ei%22%3A118%2C%22sm%22%3A%7B%22iws_iwids%22%3A%7B%22cv%22%3A%7B%22op%22%3A%22set%22%2C%22opValue%22%3A%5B%5D%7D%7D%7D%7D%2C%7B%22ty%22%3A%22as%22%2C%22st%22%3A%22link%22%2C%22si%22%3A79%2C%22ei%22%3A118%2C%22sm%22%3A%7B%22lnks_link%22%3Anull%7D%7D%2C%7B%22ty%22%3A%22as%22%2C%22st%22%3A%22text%22%2C%22si%22%3A79%2C%22ei%22%3A118%2C%22sm%22%3A%7B%22ts_bd_i%22%3Atrue%2C%22ts_fs_i%22%3Atrue%2C%22ts_ff_i%22%3Afalse%2C%22ts_ff%22%3A%22Noto%20Sans%20Mono%22%2C%22ts_it_i%22%3Atrue%2C%22ts_sc_i%22%3Atrue%2C%22ts_st_i%22%3Atrue%2C%22ts_tw%22%3A400%2C%22ts_un_i%22%3Atrue%2C%22ts_va_i%22%3Atrue%2C%22ts_bgc2_i%22%3Afalse%2C%22ts_bgc2%22%3A%7B%22clr_type%22%3A0%2C%22hclr_color%22%3A%22%23ff0000%22%7D%2C%22ts_fgc2_i%22%3Afalse%2C%22ts_fgc2%22%3A%7B%22clr_type%22%3A0%2C%22hclr_color%22%3A%22%23ff0000%22%7D%7D%7D%5D%7D%5D%2C%22sid%22%3A%22oops%22%2C%22reqId%22%3A24%7D%5D
    # 	rev	"706"
    # bundles	'[{"commands":[{"ty":"mlti","mts":[{"ty":"is","ibi":79,"s":"The background of this text is red, too\\n"},{"ty":"as","st":"paragraph","si":118,"ei":118,"sm":{"ps_al":0,"ps_awao":false,"ps_sd":null,"ps_bbtw":null,"ps_bb":null,"ps_bl":null,"ps_br":null,"ps_bt":null,"ps_hd":0,"ps_hdid":"","ps_ifl":0,"ps_il":0,"ps_ir":0,"ps_klt":false,"ps_kwn":false,"ps_ltr":true,"ps_ls":1,"ps_lslm":1,"ps_pbb":false,"ps_sm":0,"ps_sa":0,"ps_sb":0,"ps_al_i":true,"ps_awao_i":true,"ps_sd_i":true,"ps_bbtw_i":true,"ps_bb_i":true,"ps_b…":79,"ei":118,"sm":{"iws_iwids":{"cv":{"op":"set","opValue":[]}}}},{"ty":"as","st":"link","si":79,"ei":118,"sm":{"lnks_link":null}},{"ty":"as","st":"text","si":79,"ei":118,"sm":{"ts_bd_i":true,"ts_fs_i":true,"ts_ff_i":false,"ts_ff":"Noto Sans Mono","ts_it_i":true,"ts_sc_i":true,"ts_st_i":true,"ts_tw":400,"ts_un_i":true,"ts_va_i":true,"ts_bgc2_i":false,"ts_bgc2":{"clr_type":0,"hclr_color":"#ff0000"},"ts_fgc2_i":false,"ts_fgc2":{"clr_type":0,"hclr_color":"#ff0000"}}}]}],"sid":"oops","reqId":24}]'
    # rev	"771"
    # bundles	'[{"commands":[{"ty":"mlti","mts":[{"ty":"as","st":"document","si":0,"ei":0,"sm":{"ds_b":{"bg_c2":{"clr_type":0,"hclr_color":"#000000"}}}},{"ty":"as","st":"column_sector","si":0,"ei":0,"sm":{}}]}],"sid":"oops","reqId":89}]'
    """
        [
      {
        "commands": [
          {
            "ty": "mlti",
            "mts": [
              {
                "ty": "as",
                "st": "document",
                "si": 0,
                "ei": 0,
                "sm": {
                  "ds_b": {
                    "bg_c2": {
                      "clr_type": 0,
                      "hclr_color": "#000000"
                    }
                  }
                }
              },
              {
                "ty": "ds",
                "si": 4,
                "ei": 5
              },
              {
                "ty": "is",
                "ibi": 3,
                "s": "Your new text here"
              },
              {
                "ty": "as",
                "st": "text",
                "si": 3,
                "ei": 20,
                "sm": {
                "ts_fgc2_i": false,
                "ts_fgc2": {
                    "clr_type": 0,
                    "hclr_color": "#ffffff"
                }
                }
            }
            ]
          }
        ],
        "sid": "",
        "reqId": 90
      }
    ]

    """

    bundles_list = [
        {
            "commands": commands,
            "sid": sid,
            "reqId": reqId,
        }
    ]

    data = {
        "rev": rev,
        "bundles": json.dumps(bundles_list, separators=(",", ":")),
    }
    return urlencode(data)


async def main():

    async with aiohttp.ClientSession() as session:  # headers=HEADERS
        refreshed_creds = await refresh_creds()
        await asyncio.sleep(5)
        if refreshed_creds:
            save_config(save_request=refreshed_creds[-1])
        else:
            print("big problem, no refreshed creds")
            exit()
        # you gotta update this every time you run it unfortunately - I haven't found the api route yet, haven't tried. Probs in an init request on doc page load?
        current_revision = 10446
        current_state = load_config()
        current_revision = current_state["revision"]

        # current_headers=current_state["save_request"]["headers"] - minus everything that starts key with ":" and also get rid of content-length
        current_headers = {
            k: v
            for k, v in current_state["save_request"]["headers"].items()
            if not k.startswith(":") and k.lower() != "content-length"
        }

        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        frames = data["frames"]
        total_frames = len(frames)

        index = 0

        timestamp = index / data["fps"]

        STEP = 2  # todo- make itmake more sense
        delay = (STEP / data["fps"]) / 2  # 2/30 = 0.0667 = 1/15
        while True:
            # text = "a" * 5000
            frame = frames[index]
            background_color = "#ffffff" if frame["white_bg"] else "#000000"
            text_color = "#000000" if frame["white_bg"] else "#ffffff"
            length = len(frame["braille"])
            command = [
                {
                    "ty": "mlti",
                    "mts": [
                        {
                            "ty": "as",
                            "st": "document",
                            "si": 0,
                            "ei": 0,
                            "sm": {
                                "ds_b": {
                                    "bg_c2": {
                                        "clr_type": 0,
                                        "hclr_color": background_color,
                                    }
                                }
                            },
                        },
                        {"ty": "ds", "si": 1, "ei": length},  # del everything
                        {"ty": "is", "ibi": 1, "s": frame["braille"]},
                        {
                            "ty": "as",
                            "st": "text",
                            "si": 1,
                            "ei": length,
                            "sm": {
                                "ts_fgc2_i": False,
                                "ts_fgc2": {"clr_type": 0, "hclr_color": text_color},
                            },
                        },
                    ],
                }
            ]
            # print(f"Frame: {index} / {total_frames - 1} ({timestamp:.2f}s)")
            # print(
            #     f"Background: {'WHITE (black dots)' if frame['white_bg'] else 'BLACK (white dots)'}"
            # )
            # print("-" * data["width"])
            # print(frame["braille"])
            # print("-" * data["width"])

            raw_command = make_raw_data(current_revision, command, reqId=index)
            t0 = time.monotonic()
            async with session.post(
                GDOC_URL,
                data=raw_command,
                #     headers={
                #         "authorization": sapisidhash()
                #     },  # probs remove content length too, and anything that starts with ":" in the key
                headers=current_headers,
            ) as response:
                body = await response.text()
                if response.status != 200:
                    print("Status:", response.status)
                    print("Content-type:", response.headers["content-type"])

                    print(response.headers)

                if response.status == 401:
                    print("\n=== AUTH DEBUG ===")
                    print(f"sent auth header : {sapisidhash()}")
                    print(
                        f"SAPISID cookie   : ...{SAPISID[-8:] if SAPISID else 'MISSING'}"
                    )
                    print(
                        f"cookie total len : {len(HEADERS.get('cookie', HEADERS.get('Cookie', '')))}"
                    )
                    print(f"current unix ts  : {int(time.time())}")
                    print(f"stuck at frame   : {index}")
                    save_config(
                        save_request=refreshed_creds[-1],
                        index=index,
                        rev=current_revision,
                    )
                    refreshed_creds = await refresh_creds()
                    await asyncio.sleep(5)
                    if refreshed_creds:
                        save_config(save_request=refreshed_creds[-1])
                    else:
                        print("big problem, no refreshed creds")
                        exit()
                    # you gotta update this every time you run it unfortunately - I haven't found the api route yet, haven't tried. Probs in an init request on doc page load?
                    current_revision = 10446
                    current_state = load_config()
                    current_revision = current_state["revision"]

                    # current_headers=current_state["save_request"]["headers"] - minus everything that starts key with ":" and also get rid of content-length
                    current_headers = {
                        k: v
                        for k, v in current_state["save_request"]["headers"].items()
                        if not k.startswith(":") and k.lower() != "content-length"
                    }

                    # return
                    # exit()
                if body.startswith(")]}'"):
                    clean_json = body.lstrip(")]}'\n ")
                else:
                    clean_json = body

                cleaner_response = json.loads(clean_json)
                if response.status == 200:
                    # next_rev = cleaner_response["revisionRanges"][0][1]
                    save_config(
                        save_request=refreshed_creds[-1],
                        index=index,
                        rev=current_revision + 1,
                    )

                # print("RAW RESPONSE:", body[:500])
                # print("PARSED:", cleaner_response)
                # print(
                #     body
                # )  # todo: parse this to get the current revision, store in json. Could literally just fuzz a couple digits o smt if im bored
            elapsed = time.monotonic() - t0
            # print(f"req took {elapsed*1000:.0f}ms  (target period {period*1000:.0f}ms)")
            await asyncio.sleep(delay)
            current_revision += 1

            index += STEP

            if index >= total_frames:
                index = 0
                save_config(
                    save_request=refreshed_creds[-1],
                    index=index,
                    rev=current_revision,
                )


asyncio.run(main())
