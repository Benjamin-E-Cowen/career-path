import requests
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

username = "mmonnneyy@gmail.com"
password = "23bccb72"


driver = webdriver.Chrome()








def get_session_cookies(username,password):
	login_url = "https://www.linkedin.com/login"
	driver.get(login_url)
	actions = ActionChains(driver)
	actions.send_keys(username)
	actions.send_keys(Keys.TAB)
	actions.send_keys(password)
	actions.send_keys(Keys.TAB)
	actions.send_keys(Keys.TAB)
	actions.send_keys(Keys.TAB)
	actions.send_keys(Keys.ENTER)
	actions.perform()



def get_user_job_history(username):
	pass 




def get_users_matching_criteria(past_jobs=[],current_job=[], education=[]):
	pass






cookies = get_session_cookies(username, password)