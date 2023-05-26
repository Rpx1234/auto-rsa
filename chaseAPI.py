# Nelson Dane
# API to Interface with Fidelity
# Uses headless Selenium

import os
import traceback
from time import sleep
from dotenv import load_dotenv
from seleniumAPI import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Code modified from fidelityAPI version

def chase_init(DOCKER=False):
    try:
        # Initialize .env file
        load_dotenv()
        # Import Fidelity account
        if not os.getenv("CHASE_USERNAME") or not os.getenv("CHASE_PASSWORD"):
            print("Chase not found, skipping...")
            return None
        CHASE_USERNAME = os.environ["CHASE_USERNAME"]
        CHASE_PASSWORD = os.environ["CHASE_PASSWORD"]
        # Init webdriver
        print("Logging in to CHASE...")
        driver = getDriver(DOCKER)
        # Log in to Fidelity account
        driver.get(
            "https://secure03ea.chase.com/web/auth/dashboard#/dashboard/trade/equity/entry;ai=select-account;sym=")
        # Wait for page load
        sleep(5)
        #Switches to Iframe login box is in.
        driver.switch_to.frame('logonbox')
        WebDriverWait(driver, 20).until(check_if_page_loaded)

        # Type in username and password and click login

        username_field = driver.find_element(by=By.CSS_SELECTOR, value="#userId-text-input-field")
        username_field.send_keys(CHASE_USERNAME)
        WebDriverWait(driver, 10).until(
            expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, "#password-text-input-field"))
        )
        password_field = driver.find_element(by=By.CSS_SELECTOR, value="#password-text-input-field")
        password_field.send_keys(CHASE_PASSWORD)
        driver.find_element(by=By.CSS_SELECTOR, value="#signin-button").click()
        WebDriverWait(driver, 10).until(check_if_page_loaded)
        sleep(3)

        if(driver.find_element(by=By.CSS_SELECTOR, value="#simpler-auth > div > div > div > div > div > h2")):
            sendtophone = driver.find_element(by=By.CSS_SELECTOR, value="#input-sec-auth-options-0")
            sendtophone.click()
            sleep(2)
            nextbtn = driver.find_element(by=By.CSS_SELECTOR, value="#requestIdentificationCode-sm")
            nextbtn.click()
            WebDriverWait(driver,20).until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR,"#greeting-area > span")))

            sleep(3)
            print("Logged in to Chase!")
        else:
            sleep(3)
            print("Logged in to Chase!")
        # Reloads page to get to trading page of chase.
        driver.get("https://secure03ea.chase.com/web/auth/dashboard#/dashboard/trade/equity/entry;ai=select-account;sym=")

    except Exception as e:
        print(f'Error logging in: "{e}"')
        traceback.print_exc()
        return None
    return driver


async def chase_holdings(driver, ctx):
    print("WIP")


async def chase_transaction(driver, action, stock, amount, price, time, DRY=True, ctx=None):
    # Issue with this portion getting AttributeError: 'NoneType' object has no attribute 'get'.
    print()
    print("==============================")
    print("Chase")
    print("==============================")
    print()
    action = action.lower()
    stock = stock.upper()
    amount = int(amount)
    # Go to trade page
    driver.get("https://secure03ea.chase.com/web/auth/dashboard#/dashboard/trade/equity/entry;ai=select-account;sym=")
    # Wait for page to load
    WebDriverWait(driver, 20).until(check_if_page_loaded)
    sleep(3)
    # Get number of accounts
    try:
        accounts_dropdown = driver.find_element(by=By.CSS_SELECTOR, value="#header-accountDropDown")
        driver.execute_script("arguments[0].click();", accounts_dropdown)
        WebDriverWait(driver, 10).until(
            expected_conditions.presence_of_element_located((By.CSS_SELECTOR, "#header-accountDropDown"))
            )
        test = driver.find_element(by=By.CSS_SELECTOR, value="#ul-list-container-accountDropDown")
        accounts_list = test.find_elements(by=By.CSS_SELECTOR, value="li")
        print(f'Number of accounts: {len(accounts_list)}')
        number_of_accounts = len(accounts_list)
        # Click a second time to clear the account list
        driver.execute_script("arguments[0].click();", accounts_dropdown)
    except:
        print("Error: No accounts foundin dropdown")
        traceback.print_exc()
        return None
    # Complete on each account
    # Because of stale elements, we need to re-find the elements each time
    for x in range(number_of_accounts):
        try:
            # Select account
            accounts_dropdown_in = driver.find_element(by=By.CSS_SELECTOR, value="#header-accountDropDown")
            driver.execute_script("arguments[0].click();", accounts_dropdown_in)
            WebDriverWait(driver, 10).until(
                expected_conditions.presence_of_element_located((By.ID, "ul-list-container-accountDropDown"))
                )
            test = driver.find_element(by=By.ID, value="ul-list-container-accountDropDown")
            accounts_dropdown_in = test.find_elements(by=By.CSS_SELECTOR, value="li")
            account_label = accounts_dropdown_in[x].text
            accounts_dropdown_in[x].click()
            sleep(1)
            # Type in ticker
            ticker_box = driver.find_element(by=By.CSS_SELECTOR, value="#equitySymbolLookup-block-autocomplete-validate-input-field")
            WebDriverWait(driver, 10).until(
                expected_conditions.element_to_be_clickable(ticker_box)
            )
            ticker_box.send_keys(stock)
            ticker_box.send_keys(Keys.RETURN)
            sleep(1)
            # Check if symbol not found is displayed

            ## Not working
            try:
                driver.find_element(by=By.CSS_SELECTOR,
                                    value="body > div.app-body > ap122489-ett-component > div > order-entry > div.eq-ticket.order-entry__container-height > div > div > form > div.order-entry__container-content.scroll > div:nth-child(2) > symbol-search > div > div.eq-ticket--border-top > div > div:nth-child(2) > div > div > div > pvd3-inline-alert > s-root > div > div.pvd-inline-alert__content > s-slot > s-assigned-wrapper")
                print(f"Error: Symbol {stock} not found")
                return None
            except:
                pass

            # Set buy/sell
            if action == "buy":
                buy_button = driver.find_element(by=By.CSS_SELECTOR,
                                                 value="#tradeActions-container > span:nth-child(1) > label")
                buy_button.click()
            elif action == "sell":
                sell_button = driver.find_element(by=By.CSS_SELECTOR,
                                                  value="#tradeActions-container > span:nth-child(2) > label")
                sell_button.click()
            else:
                print(f"Error: Invalid action {action}")
                return None
            # Set amount (and clear previous amount)
            amount_box = driver.find_element(by=By.CSS_SELECTOR, value="#tradeQuantity-text-input-field")
            amount_box.clear()
            amount_box.send_keys(amount)
            # Set market/limit
            market_button = driver.find_element(by=By.CSS_SELECTOR,
                                                    value="#tradeOrderTypeOptions-container > span:nth-child(1) > label")
            market_button.click()

            # Time in Force, Selects Daytime.
            timeinforce_button = driver.find_element(by=By.CSS_SELECTOR, value = "#tradeExecutionOptions-container > span:nth-child(1) > label")
            timeinforce_button.click()
            # Preview order
            WebDriverWait(driver, 10).until(check_if_page_loaded)
            sleep(1)
            preview_button = driver.find_element(by=By.CSS_SELECTOR, value="#previewOrder")
            preview_button.click()
            # Wait for page to load
            WebDriverWait(driver, 10).until(check_if_page_loaded)
            sleep(1)
            # Place order
            if not DRY:
                # Check for error popup and clear it if the account cannot sell the stock for some reason.
                try:
                    place_button = driver.find_element(by=By.CSS_SELECTOR, value="#submitOrder")
                    place_button.click()

                    # Wait for page to load
                    WebDriverWait(driver, 10).until(check_if_page_loaded)
                    sleep(1)
                    # Send confirmation
                    message = f"Chase {account_label}: {action} {amount} shares of {stock}"
                    print(message)
                    if ctx:
                        await ctx.send(message)
                except NoSuchElementException:
                    # Check for error
                    print("Error exception missing.(Coder notes)")
                    # Unknown of what error is shown, empty for now
                # Send confirmation
            else:
                message = f"DRY: Chase {account_label}: {action} {amount} shares of {stock}"
                print(message)
                if ctx:
                    await ctx.send(message)
            sleep(3)
        except Exception as e:
            print(e)
            traceback.print_exc()
            continue
