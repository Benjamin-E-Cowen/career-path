import requests
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re
import json




chrome_options = Options()
#chrome_options.add_argument("--headless")
username = "mmonnneyy@gmail.com"
password = "23bccb72"


driver = webdriver.Chrome(options=chrome_options)



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




def get_users_matching_criteria_url(past_job=[],current_job=[], education=[],name=""):
	print("Determining search critera url")
	url_c = driver.current_url
	driver.get("https://www.linkedin.com/search/results/people/?origin=SWITCH_SEARCH_VERTICAL&sid=9~1")
	while driver.current_url == url_c:
		pass 
	find_elements_by_inner_text("All filters")[0].click()
	for edu in education:
		print("adding education", edu)
		find_elements_by_inner_text("Add a school")[0].click()
		actions = ActionChains(driver)
		actions.send_keys(edu).pause(1).send_keys(Keys.DOWN).send_keys(Keys.ENTER).pause(1)
		actions.perform()
	for job in past_job:
		print("adding past job ", job)
		find_elements_by_inner_text("Add a company")[1].click()
		actions = ActionChains(driver)
		actions.send_keys(job).pause(1).send_keys(Keys.DOWN).send_keys(Keys.ENTER).pause(1)
		actions.perform()
	for job in current_job:
		print("adding current job ", job)
		find_elements_by_inner_text("Add a company")[0].click()
		actions = ActionChains(driver)
		actions.send_keys(job).pause(1).send_keys(Keys.DOWN).send_keys(Keys.ENTER).pause(1)
		actions.perform()
	url = driver.current_url
	find_elements_by_inner_text("Show results")[0].click()
	while driver.current_url == url:
		pass 	
	url = driver.current_url
	if name:
		url =  url[:48] + f'keywords={name}&' + url[48:]

	url =  url[:48] + f'page={0}&' + url[48:]
	print("url",url)
	

	people_links = []
	i = 0
	while not "No results found" in driver.page_source:
		i+=1
		url_old = driver.current_url

		url = url.replace(f'page={i-1}',f'page={i}')
		driver.get(url)
		while(driver.current_url == url_old):
			pass 
		soup = BeautifulSoup(driver.page_source, "html.parser")
		people = soup.find_all("li", class_="reusable-search__result-container")
		for person in people:
			persons_link = person.find_all("a", class_="app-aware-link")
			if len(persons_link) > 0 and "search" not in persons_link[0]['href']:
				people_links.append(persons_link[0]['href'])
	return people_links





cookies = get_session_cookies(username, password)
people_links = get_users_matching_criteria_url(education=["UCLA"], past_job=["Facebook"], name="John")

job_descriptions  = []
all_companies = {}
company_counts = {}
people_jobs = []

for people_link in people_links:
	driver.get(people_link)
	soup = BeautifulSoup(driver.page_source, "html.parser")

	exp_index = soup.text.index("Experience")
	edu_index = soup.text.index("Education")
	occupations_images_temp = list(map(lambda img: img.get('src', 'QWERTY'), soup.find_all("img")))
	occupations_temp = list(map(lambda img: img.get('alt', 'QWERTY').replace("logo","").strip(), soup.find_all("img")))
	occupations = []
	occupations_images = []
	for idx in range(len(occupations_temp)):
		try:
			if any(exp_index < img_index < edu_index for img_index in [m.start() for m in re.finditer(occupations_temp[idx], soup.text)]) and occupations_temp[idx]:
				occupations.append(occupations_temp[idx])
				occupations_images.append(occupations_images_temp[idx])
		except:
			pass 



	for company, company_image in zip(occupations, occupations_images):
		all_companies[company] = company_image
		company_counts[company] = company_counts.get(company, 0) + 1
	people_jobs += [occupations]



saved_info = {}
saved_info['career_paths'] = people_jobs
saved_info['companies_images'] = all_companies
saved_info['companies_counts'] = company_counts



output = "data =" +  f" '{json.dumps(saved_info)}' "
with open('../Back End/data.json', 'w') as f:
    f.write(output)














