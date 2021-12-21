import requests
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

username = "mmonnneyy@gmail.com"
password = "23bccb72"


driver = webdriver.Chrome()



def find_elements_by_inner_text(inner_text):
	while (len(driver.find_elements_by_xpath(f'//*[text()[contains(., "{inner_text}")]]')) == 0):
		pass
	return driver.find_elements_by_xpath(f'//*[text()[contains(., "{inner_text}")]]')



def get_session_cookies(username,password):
	print("Logging in")
	login_url = "https://www.linkedin.com/login"
	driver.get(login_url)
	actions = ActionChains(driver)
	actions.send_keys(username).send_keys(Keys.TAB).send_keys(password).send_keys(Keys.TAB).send_keys(Keys.TAB).send_keys(Keys.TAB).send_keys(Keys.ENTER)
	actions.perform()
	cookies = {}
	selenium_cookies = driver.get_cookies()
	selenium_cookies_s = selenium_cookies
	for cookie in selenium_cookies:
		cookies[cookie['name']] = cookie['value']
	return cookies
	print(username, "logged in")





def get_user_job_history(username):
	pass 




def get_users_matching_criteria_url(past_job=[],current_job=[], education=[]):
	print("Determining search critera url")
	driver.get("https://www.linkedin.com/search/results/people/?origin=SWITCH_SEARCH_VERTICAL&sid=9~1")

	find_elements_by_inner_text("All filters")[0].click()
	for edu in education:
		print("adding education", edu)
		find_elements_by_inner_text("Add a school")[0].click()
		actions = ActionChains(driver)
		actions.send_keys(edu).pause(3).send_keys(Keys.DOWN).send_keys(Keys.ENTER).pause(3)
		actions.perform()
	for job in past_job:
		print("adding past job ", job)
		find_elements_by_inner_text("Add a company")[1].click()
		actions = ActionChains(driver)
		actions.send_keys(job).pause(3).send_keys(Keys.DOWN).send_keys(Keys.ENTER).pause(3)
		actions.perform()
	for job in current_job:
		print("adding current job ", job)
		find_elements_by_inner_text("Add a company")[0].click()
		actions = ActionChains(driver)
		actions.send_keys(job).pause(3).send_keys(Keys.DOWN).send_keys(Keys.ENTER).pause(3)
		actions.perform()
	url = driver.current_url
	find_elements_by_inner_text("Show results")[0].click()
	while driver.current_url == url:
		pass 
	
	return driver.current_url



cookies = get_session_cookies(username, password)
url = get_users_matching_criteria_url(education=["UC Berkeley", "Stanford"], past_job=["Cisco","Palo Alto Networks"])



