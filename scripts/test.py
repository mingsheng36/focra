from selenium import webdriver
driver = webdriver.PhantomJS(executable_path='C:\phantomjs-1.9.8-windows\phantomjs.exe')
driver.get('https://www.google.com.sg/')
print (driver.page_source).encode('utf-8')
driver.quit()