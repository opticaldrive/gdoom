from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://playwright.dev")
    print(page.title())
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