from selenium import webdriver
driver = webdriver.PhantomJS(executable_path='C:\phantomjs-1.9.8-windows\phantomjs.exe')
driver.get('http://localhost:8000')
print (driver.page_source).encode('utf-8')
driver.quit()