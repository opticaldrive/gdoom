from patchright.sync_api import sync_playwright
import time

pw_chromium_profile = "./cookiejar/pw-profile"
with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(headless=False, user_data_dir=pw_chromium_profile)
    page = browser.pages[0]
    page.goto("https://google.com")
    input("press enter when you've put in your creds and navigated to the google doc")
    # page.pause(10)

    browser.close()

def headful_login():
    # headfully launch chrome
    # login
    print("press enter after you've signed in and navigated to your gdocs page")
    input()
    # save cookies/data/profile to file
    # done
    None
def refresh_creds():
    # load profile
    # launch chrome headlessly with profile/ua
    # navigate to docs page
    # click on doc text
    # left key to ensure text isn't selected?
    # press space key
    # undo/cmd/cntrl z
    # for that last cmd z record the save request and update config.py accordinly

    None