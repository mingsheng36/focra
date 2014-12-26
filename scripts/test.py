from selenium import webdriver
driver = webdriver.PhantomJS(executable_path='C:\phantomjs-1.9.8-windows\phantomjs.exe')
import sys
driver.get(sys.argv[1])
print (driver.page_source).encode('utf-8')
driver.quit()