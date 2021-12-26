import requests
import selenium
from seleniumwire import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re
import json
import time



chrome_options = Options()
chrome_options.add_argument("--headless")
username = "username@email.com"
password = "password"


driver = webdriver.Chrome(options=chrome_options)
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
def api_request(url, headers = {"user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"}):
		with requests.session() as s:
		    s.cookies['li_at'] = cookies['li_at']
		    s.cookies["JSESSIONID"] = cookies['JSESSIONID']
		    s.headers = headers
		    s.headers["csrf-token"] = s.cookies["JSESSIONID"].strip('"')
		    response = s.get(url)
		    return response
class search:
	def get_company_id(company_name):
		url = f'https://www.linkedin.com/voyager/api/typeahead/hitsV2?keywords={company_name}&origin=OTHER&q=type&type=COMPANY'
		company_id_json = api_request(url).json()
		return company_id_json['elements'][0]['image']['attributes'][0]['miniCompany']['objectUrn'].split(":")[-1]
	def get_school_id(school_name):
		url = f'https://www.linkedin.com/voyager/api/typeahead/hitsV2?keywords={school_name}&origin=OTHER&q=type&type=SCHOOL'
		school_id_json = api_request(url).json()
		return school_id_json['elements'][0]['image']['attributes'][0]['miniSchool']['objectUrn'].split(":")[-1]
	def get_user_ids(company_id, school_id=-1, number_of_users=10):
		headers = {'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"', 'x-restli-protocol-version': '2.0.0', 'x-li-lang': 'en_US', 'sec-ch-ua-mobile': '?0', 'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36', 'x-li-page-instance': 'urn:li:page:d_flagship3_search_srp_people_load_more;U5E/E+RwRiqjmGH33DgMSw==', 'accept': 'application/vnd.linkedin.normalized+json+2.1', 'x-li-track': '{"clientVersion":"1.9.8202.10","mpVersion":"1.9.8202.10","osName":"web","timezoneOffset":-8,"timezone":"America/Los_Angeles","deviceFormFactor":"DESKTOP","mpName":"voyager-web","displayDensity":2,"displayWidth":2880,"displayHeight":1800}', 'sec-ch-ua-platform': '"macOS"', 'sec-fetch-site': 'same-origin', 'sec-fetch-mode': 'cors', 'sec-fetch-dest': 'empty', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-US,en;q=0.9'}

		user_ids = []
		start = 0
		while len(user_ids) < number_of_users:
			url = f'https://www.linkedin.com/voyager/api/search/dash/clusters?decorationId=com.linkedin.voyager.dash.deco.search.SearchClusterCollection-129&origin=FACETED_SEARCH&q=all&query=(keywords:%2C,flagshipSearchIntent:SEARCH_SRP,queryParameters:(pastCompany:List({company_id}),resultType:List(PEOPLE)' +  (f',schoolFilter:List({school_id})' if int(school_id) >= 0 else "") +  f'),includeFiltersInResponse:false)&start={start}'
			user_ids_json = api_request(url, headers).json()
			new_users_ids = list(filter(lambda user: user,map(lambda user: search.get_user_public_identifier(user['entityUrn'].split(":")[-1]), filter(lambda user: user['$type'] == 'com.linkedin.voyager.dash.identity.profile.Profile', user_ids_json['included']))))
			if not new_users_ids:
				break
			user_ids.extend(new_users_ids)
			start += 10
		return user_ids
	def get_user_public_identifier(user_id):
		url = f'https://www.linkedin.com/voyager/api/identity/profiles/{user_id}'
		user_info_json = api_request(url).json()
		if 'miniProfile' in user_info_json:
			return user_info_json['miniProfile']['publicIdentifier']
		return None
	def get_user_jobs(user_public_identifier):
		url = f'https://www.linkedin.com/voyager/api/identity/dash/profiles?q=memberIdentity&memberIdentity={user_public_identifier}&decorationId=com.linkedin.voyager.dash.deco.identity.profile.FullProfileWithEntities-93'
		all_user_jobs = api_request(url).json()
		user_jobs = []
		for job in all_user_jobs['elements'][0]['profilePositionGroups']['elements']:
			if 'company' in job:
				job_info = {}
				job_info['name']  = job['company']['name']
				job_info['url']   = job['company']['url']
				job_info['image'] = job['company']['logo']['vectorImage']['rootUrl'] + job['company']['logo']['vectorImage']['artifacts'][-1]['fileIdentifyingUrlPathSegment']
				user_jobs.append(job_info)
		return user_jobs

print("Logging user in, ", username)
cookies = get_session_cookies(username, password)
print("Logged user in, ", username)



company_name = "Google"
school_name = "uc Berkeley"
number_of_users = 50


print("Finding users matching criteria,", company_name, school_name, number_of_users)
users = search.get_user_ids(search.get_company_id(company_name), search.get_school_id(school_name), number_of_users)
print("Found Users")

company_counts = {}
company_images = {}
company_urls = {}
users_jobs = []

print("Looking at each users jobs")
for user in users:
	print("looking at user", user)
	user_jobs = search.get_user_jobs(user)
	for company in user_jobs:
		company_name = company['name'].replace("'","")
		company_counts[company_name] = company_counts.get(company_name, 0) + 1
		company_images[company_name] = company['image']
		company_urls[company_name] = company['url']
	users_jobs.append(list(map(lambda job: job['name'].replace("'","") ,user_jobs))[::-1])




saved_info = {}
saved_info['career_paths'] = users_jobs
saved_info['companies_images'] = company_images
saved_info['companies_counts'] = company_counts

print("uploading json")

output = "data =" +  f" '{json.dumps(saved_info)}' "
with open('../Back End/data.json', 'w') as f:
    f.write(output)




# people_links = get_users_matching_criteria_url(education=["UC Berkeley"], past_job=["Google"], name="John")

# job_descriptions  = []
# all_companies = {}
# company_counts = {}
# people_jobs = []

# for people_link in people_links:
# 	url = people_link
# 	driver.get(people_link)
# 	while driver.current_url == url:
# 		pass
# 	url = driver.current_url + "details/experience/"
# 	time.sleep(5)
# 	driver.get(url)
# 	soup = BeautifulSoup(driver.page_source, "html.parser")
# 	occupations_images_temp = list(map(lambda img: img.get('src', 'QWERTY').strip(), filter(lambda img: img.get('width',0) == '48',soup.find_all("img"))))
# 	occupations_temp = list(map(lambda img: img.get('alt', 'QWERTY').replace("logo","").strip(), filter(lambda img: img.get('width',0) == '48',soup.find_all("img"))))
# 	occupations = []
# 	occupations_images = []
# 	for idx in range(len(occupations_temp)):
# 		try:
# 			occupations.append(occupations_temp[idx])
# 			occupations_images.append(occupations_images_temp[idx])
# 		except:
# 			pass 



# 	for company, company_image in zip(occupations, occupations_images):
# 		all_companies[company] = company_image
# 		company_counts[company] = company_counts.get(company, 0) + 1
# 	people_jobs += [occupations[::-1]]

# # EXAMPLE
# # JD = [A, B, C ,D]
# # CT = [B, D, E]
# # career_paths = [[A,B,C,D], [B,D,E]]
# # companies_images{A: company_A_Logo, B: company_B_logo, ...}
# # company_counts[ A: 1, B: 2, C: 1, D: 2, E: 1]













# from seleniumwire import webdriver

# # import gzip
# # data = gzip.decompress(response.read())
# # text = data.decode('utf-8')


# url = "URL_OF_API_WE_WANT_TO_COMMUNICATE_WITH"
# driver.requests:

# #need requests
# r = requests.get(request.url, headers=request.headers)


# #get id
# facebook_query_return_as_json['data']['elements'][0]['image']['attributes'][0]['*miniCompany'].split(":")[-1]





#https://www.linkedin.com/search/results/people/?network=%5B%22O%22%5D&origin=FACETED_SEARCH&page=1&sid=b)g


#Request URL: 


# #get user publicIdentifier
# https://www.linkedin.com/voyager/api/identity/profiles/{user_id}
# r['miniProfile']['publicIdentifier']

# #get user jobs
# https://www.linkedin.com/voyager/api/identity/dash/profiles?q=memberIdentity&memberIdentity={user_public_id}&decorationId=com.linkedin.voyager.dash.deco.identity.profile.FullProfileWithEntities-93
# 'https://www.linkedin.com/voyager/api/identity/dash/profiles?q=memberIdentity&memberIdentity=jordan-chernof&decorationId=com.linkedin.voyager.dash.deco.identity.profile.FullProfileWithEntities-93'



# #each company
# r['elements'][0]['profilePositionGroups']['elements']
# #company name
# r['elements'][0]['profilePositionGroups']['elements'][1]['company']['name']
# #company url
# r['elements'][0]['profilePositionGroups']['elements'][1]['company']['url']
# #company  image
# r['elements'][0]['profilePositionGroups']['elements'][1]['company']['logo']['vectorImage']['rootUrl'] + r['elements'][0]['profilePositionGroups']['elements'][1]['company']['logo']['vectorImage']['artifacts'][-1]['fileIdentifyingUrlPathSegment']


