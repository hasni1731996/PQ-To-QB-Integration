import os
import time

import cryptocode
import django
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "OAuth2DjangoSampleApp.settings")
django.setup()

from django.contrib.auth.models import User
from sampleAppOAuth2.constants import BASE_URL_PROJECT, PASSWORD_SECRET_KEY, SYNC_PROJECT_CHOICE_KEY, \
    SYNC_VENDOR_CHOICE_KEY, SYNC_COST_CODE_CHOICE_KEY, SYNC_EXPENSE_CHOICE_KEY, SYNC_CUSTOMER_INVOICES_CHOICE_KEY
from sampleAppOAuth2.models import SyncUserTasks

logger = logging.getLogger(__name__)


def sleep():
    return time.sleep(5)


def sync_tasks():
    all_users = SyncUserTasks.objects.all()
    for user in all_users:
        user_choices = [choice.id for choice in user.choices.all()]
        user_ = User.objects.get(id=user.user.id)
        options = webdriver.ChromeOptions()
        options.headless = True
        driver = webdriver.Chrome('sampleAppOAuth2/jobs/chromedriver', options=options)
        wait = WebDriverWait(driver, 300)  # (seconds)  300 seconds -> 5minutes
        driver.get(BASE_URL_PROJECT)
        sleep()
        driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/form/div[1]/input").send_keys(
            user.user.username)
        driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/form/div[2]/input").send_keys(
            cryptocode.decrypt(user_.authtoken_set.get(user_id=user_).user_encrypted_password, PASSWORD_SECRET_KEY))
        driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/form/button").click()
        sleep()

        if SYNC_PROJECT_CHOICE_KEY in user_choices:
            # Get customer page
            driver.get(BASE_URL_PROJECT + "customers/")
            logger.info("On Customers page")
            sleep()
            driver.find_element_by_xpath('//*[@id="sync-btn"]').click()
            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="sync-btn"]')))
            sleep()

        if SYNC_VENDOR_CHOICE_KEY in user_choices:
            # Get Vendors page
            driver.get(BASE_URL_PROJECT + "vendors/")
            logger.info("On Vendors page")
            sleep()
            driver.find_element_by_xpath('//*[@id="sync-vendor"]').click()
            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="sync-vendor"]')))
            sleep()

        if SYNC_COST_CODE_CHOICE_KEY in user_choices:
            # Get CostCodes page
            driver.get(BASE_URL_PROJECT + "costcodes/")
            logger.info("On Cost-Codes page")
            sleep()
            driver.find_element_by_xpath('//*[@id="sync-codes"]').click()
            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="sync-codes"]')))
            sleep()
        if SYNC_CUSTOMER_INVOICES_CHOICE_KEY in user_choices:
            # Get CustomerInv page
            driver.get(BASE_URL_PROJECT + "custInv/")
            logger.info("On CustomerInv page")
            sleep()
            driver.find_element_by_xpath('//*[@id="sync-custInv"]').click()
            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="sync-custInv"]')))
            sleep()

        if SYNC_EXPENSE_CHOICE_KEY in user_choices:
            # Get Expenses page
            driver.get(BASE_URL_PROJECT + "expenses/")
            logger.info("On Expenses page")
            sleep()
            driver.find_element_by_xpath('//*[@id="sync-btn"]').click()
            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="sync-btn"]')))
            sleep()
            driver.close()


if __name__ == '__main__':
    sync_tasks()
