#coding:utf-8
from selenium import webdriver

#test
if __name__ == '__main__':
    driver = webdriver.Chrome()
    driver.get("https://www.baidu.com/")
    print driver.title
    print driver.page_source
    driver.quit()