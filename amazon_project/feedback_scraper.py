from datetime import datetime
import selenium
from flask import current_app
from selenium import webdriver
from dateparser.search import search_dates
import time
from selenium.webdriver.common.by import By


class SellerFeedbackScraper:
    def __init__(self):
        caps = webdriver.DesiredCapabilities.PHANTOMJS
        caps["phantomjs.page.settings.userAgent"] = "Mozilla/5.0 (X11; Linux x86_64) " \
                                                    "AppleWebKit/53 (KHTML, like Gecko) Chrome/15.0.87"
        self.driver = webdriver.PhantomJS(desired_capabilities=caps)

    def scrape(self, seller_id, marketplace):
        self.driver.get("https://www.amazon." + marketplace + "/sp?seller=" + str(seller_id))
        try:
            return self.parse()
        except Exception as e:
            current_app.logger.error(str(datetime.now()) + str(e))
            return []

    def parse(self):
        next_page = True
        feedback_list = []
        while next_page:
            try:
                try:
                    table_id = self.driver.find_element_by_xpath("//*[@id='feedback-table']")
                    # get all of the rows in the table
                    rows = table_id.find_elements_by_xpath(".//tr[@class='feedback-row']")
                    for row in rows:
                        feedback = {}
                        rating_string = row.find_element_by_xpath(".//th/div/i/span").get_attribute("innerHTML")
                        feedback['rating'] = int(rating_string.split(' ')[0])
                        col_2 = row.find_element(By.TAG_NAME, "td")
                        feedback['text'] = col_2.find_element_by_xpath('.//*[@id="-text" or @id="-expanded"]'
                                                                       ).get_attribute("innerHTML")
                        try:
                            div = col_2.find_element_by_xpath(
                                ".//*[@class='a-section a-spacing-top-small feedback-suppressed']")
                            value = div.value_of_css_property("display")
                            if value == 'none':
                                feedback['deleted'] = 0
                            else:
                                feedback['deleted'] = 1
                        except selenium.common.exceptions.NoSuchElementException:
                            feedback['deleted'] = 0
                        s = col_2.find_element_by_xpath('.//div/div[2]/span').text
                        try:
                            date = search_dates(s, settings={'TIMEZONE': 'UTC'})[0][1].date()
                        except TypeError:
                            date = None
                        if date is None or date > datetime.today().date():
                            feedback['date'] = ""
                        else:
                            feedback['date'] = str(date)
                        feedback_list.append(feedback)
                except selenium.common.exceptions.WebDriverException:
                    current_app.logger.error(str(datetime.now()) + "Selenium did not find Element(s)")
                    return []
                self.driver.find_element_by_xpath("//*[@id='feedback-next-link']").click()
                current_app.logger.info(str(datetime.now()) + " Clicking NEXT PAGE")
                time.sleep(10)
            except selenium.common.exceptions.ElementNotVisibleException:
                next_page = False
        return feedback_list
