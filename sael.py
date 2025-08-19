from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd

url = "https://stockanalysis.com/list/indonesia-stock-exchange/"

driver = webdriver.Chrome()
driver.get(url)

# Keep scrolling until all rows load
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # wait for new rows to load
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Now extract table
table = driver.find_element(By.TAG_NAME, "table").get_attribute("outerHTML")
df = pd.read_html(table)[0]

df.to_csv("indonesia_stocks_full.csv", index=False)
print("✅ Saved", len(df), "rows")
driver.quit()
