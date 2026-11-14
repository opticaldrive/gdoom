from patchright.sync_api import sync_playwright
import time
import sys

pw_chromium_profile = "./cookiejar/pw-profile"

from config import GDOC_URL
from urllib.parse import urlparse
import sys
from urllib.parse import parse_qs, urlparse

parsed = urlparse(GDOC_URL)

base_path = "/".join(parsed.path.split("/")[:4])
clean_gdoc_url = f"{parsed.scheme}://{parsed.netloc}{base_path}/"

print(clean_gdoc_url)


def headful_login():
    # headfully launch chrome
    # login
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            headless=False, user_data_dir=pw_chromium_profile
        )
        page = browser.pages[0]
        page.goto("https://google.com")
        input(
            "press enter when you've put in your creds and navigated to the google doc"
        )
        # page.pause(10)

        browser.close()
    print("done")
    # save cookies/data/profile to file
    # done


# def refresh_creds():
#     # load profile
#     # launch chrome headlessly with profile/ua
#     # navigate to docs page
#     # click on doc text
#     # left key to ensure text isn't selected?
#     # press space key
#     # undo/cmd/cntrl z
#     # for that last cmd z record the save request and update config.py accordinly
#     undo_shortcut = "Meta+z" if sys.platform == "darwin" else "Control+z"

#     with sync_playwright() as p:
#         browser = p.chromium.launch_persistent_context(
#             headless=False, user_data_dir=pw_chromium_profile
#         )
#         page = browser.pages[0]
#         page.goto(clean_gdoc_url)
#         # page.wait_for_load_state("domcontentloaded")
#         # page.click()
#         # Wait for the actual document page canvas to render
#         page_sheet = page.locator(".kix-page-paginated").first
#         page_sheet.wait_for(state="visible")
#         page_sheet.click(position={"x": 200, "y": 200})
#         page.wait_for_timeout(500)
#         print("clicked")
#         # Press Left arrow to deselect any highlighted text
#         page.keyboard.press("ArrowLeft")

#         # Type a space to trigger an edit
#         page.keyboard.press("Space")
#         page.wait_for_timeout(500)

#         # Intercept the /save POST request triggered by the Undo action
#         with page.expect_request(
#             lambda req: "/save" in req.url and req.method == "POST"
#         ) as req_info:
#             page.keyboard.press(undo_shortcut)

#         save_request = req_info.value

#         print("Save URL:", save_request.url)
#         print("Headers:", save_request.headers)
#         print("Post Data:", save_request.post_data)

#     None


def refresh_creds():
    undo_shortcut = "Meta+z" if sys.platform == "darwin" else "Control+z"
    save_events = []

    def handle_request(req):
        if "/save" in req.url:
            parsed = urlparse(req.url)
            params = parse_qs(parsed.query)
            sid = params.get("sid", [None])[0]
            save_events.append(
                {
                    "sid": sid,
                    "method": req.method,
                    "url": req.url,
                    "headers": req.all_headers(),
                    "post_data": req.post_data,
                }
            )

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            headless=True, user_data_dir=pw_chromium_profile
        )
        browser.on("request", handle_request)

        page = browser.pages[0] if browser.pages else browser.new_page()
        page.goto(clean_gdoc_url)

        page.locator(".kix-appview-editor").wait_for(state="visible", timeout=20000)
        page.wait_for_timeout(600)  # more waiting
        # some dumb clicking google thought would worked, and it did. after a dozen searches.
        page.locator(".kix-page-paginated").first.click()
        typing_body = page.frame_locator("iframe.docs-texteventtarget-iframe").locator(
            "[contenteditable='true']"
        )
        typing_body.focus()
        page.wait_for_timeout(300)

        page.keyboard.press("ArrowLeft")  # nselect stuff cuz
        page.keyboard.insert_text(" ")
        page.wait_for_timeout(500)

        # undo the space
        page.keyboard.press(undo_shortcut)
        page.wait_for_timeout(1000)  # abnother save

        browser.close()

    all_sids = list(dict.fromkeys(e["sid"] for e in save_events if e["sid"]))
    print(f"Captured {len(save_events)} /save requests.")
    print("All Save IDs (sid):", all_sids)

    if save_events:
        print("\nLast /save URL:", save_events[-1]["url"])
        print("Last /save Post Data:", save_events[-1]["post_data"])
        print("last headers", save_events[-1]["headers"])
        print("last urls", save_events[-1]["url"])

    return save_events


# headful_login()
refresh_creds()
