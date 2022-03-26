
from pandas import concat
from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options
from shutil import which
from scrapy import Selector
import csv
from datetime import datetime
import requests
import html2text

h = html2text.HTML2Text()
h.ignore_links = True
h.ignore_images = True


startURL = "https://www.helloworld.rs/oglasi-za-posao/?isource=Helloworld.rs&icampaign=home-fancy-intro&imedium=site"
fileName = "helloworld.csv"
chromePath = "D:\Projects\chromedriver_97\chromedriver.exe"


def botInitialization():
    # Initialize the Bot
    chromeOptions = Options()
    # chromeOptions.add_argument("--headless")
    chromePath = which(chromePath)
    driver = webdriver.Chrome(executable_path=chromePath, options=chromeOptions)
    driver.maximize_window()
    return driver

driver = botInitialization()


with open(fileName, 'w', newline='', encoding="utf-8-sig") as csvfile:
    fieldnames = ['Title', "Skills", 'Location', "Company", "Content", "URL"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    driver.get(startURL)
    # sleep(2)

    while True:
        sleep(3)
        response = Selector(text=driver.page_source)
        jobURLs = response.css("h3 > a::attr(href)").extract()

        for url in jobURLs:
            print("scraping: " + url)
            html = requests.get("https://www.helloworld.rs" + url).content
            response = Selector(text=html)
            
            title = response.css("h1 > span::text").extract_first()
            location = response.css("div.gap-1 > p.text-sm.font-semibold::text").extract_first()
            
            company = response.css("h4 > a.link::text").extract_first()
            if not company:
                company = response.css("h4::text").extract_first()

            skills = response.css("div > button > span.inline-flex::text").extract()
            skills = [skill.strip() for skill in skills]
            skills = ", ".join(skills)
            content = response.css("div.__job-content").extract()[0]

            content = h.handle(content)

            content = content.replace("*", "")
            content = content.replace("\n\n", "\n")

            writer.writerow({'Title': title, 'Skills':skills, 'Location': location, 'Company': company, 'Content': content, 'URL': url})


        nextPage = driver.find_elements_by_css_selector("div.pagination > a.w-10.h-10")
        clicked = False
        for page in nextPage:
            try:
                if "la-angle-right" in page.find_element_by_css_selector("i").get_attribute("class"):
                    # click using js
                    driver.execute_script("arguments[0].click();", page)
                    print("Clicked")
                    clicked = True
                    break
            except:
                continue
        
        if not clicked:
            break


driver.close()
driver.quit()