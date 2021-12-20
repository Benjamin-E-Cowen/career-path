import requests
import selenium
from selenium import webdriver

username = "mmonnneyy@gmail.com"
password = "23Bccb72"


driver = webdriver.Chrome()



def get_session_cookies(username,password):
	login_url = "https://www.linkedin.com/login"
