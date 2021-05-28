from selenium.webdriver.chrome.options import Options
from linkedin_api import Linkedin
from selenium import webdriver
from bs4 import BeautifulSoup
import requests,time,threading,os

PATH = 'Downloads/chromedriver' # Location to your chromedriver
lock = threading.Lock()
keys = ' '

api = Linkedin('LinkedIn mail ID','LinkedIn Password')

def driver_auth():
    opts = Options()
    opts.add_argument("--headless")
    driver = webdriver.Chrome(PATH, options=opts)
    return driver

def scrape_linkedin(key,link):
    try:
        link = link.split('/')[-1]
        prof = api.get_profile(link)
        exp = prof['experience']
        edu = prof['education']
    except:
        print('Error in Profile !')
        return
    lock.acquire()
    if os.path.isfile(f"{keys}.csv"):
        f = open(f"{keys}.csv", "a")
    else:
        f = open(f"{keys}.csv", "w")
        headers = "Name,ProfileLink,OrganisationName,TimePeriod,Description,Email,Ph.No\n"
        f.write(headers)
    f.write(f'{key},{link},')
    i, flag = 0, 0
    for x in exp:
        flag = 1
        if i!=0: f.write(',,')
        try:
            comp = x['companyName'].replace(',','')
        except :
            comp = 'NULL'
        try:
            timePeriod = str(x['timePeriod']['startDate']['month'])+'/'+str(x['timePeriod']['startDate']['year'])+' - '+str(x['timePeriod']['endDate']['month'])+'/'+str(x['timePeriod']['endDate']['year'])
        except:
            timePeriod = 'NULL'
        try:
            title = x['title'].replace(',',' ')
        except :
            title = 'NULL'
        f.write(f"{comp},{timePeriod},{title}\n")
        i = i+1
    for e in edu:
        if not flag == 0:
            f.write(',,')
        try:
            scl_name = e['school']['schoolName'].replace(',','')
        except :
            scl_name  ='NULL'
        try:
            timePeriod = str(e['timePeriod']['startDate']['year'])+' - '+str(e['timePeriod']['endDate']['year'])
        except :
            timePeriod = 'NULL'
        try:
            domain = (e['degreeName']+'-'+e['fieldOfStudy']).replace(',',' ')
        except:
            domain = 'NULL'
        f.write(f"{scl_name},{timePeriod},{domain}\n")  
        flag = 1          
    contact = api.get_profile_contact_info(link)
    
    mail = contact['email_address']
    if str(mail)=='None':
        mail = 'NULL'
    else:
        mail = mail.replace(',','/')
    mob = contact['phone_numbers']
    if not len(mob)==0:
        nums = '/'.join(str(num) for num in mob)
    else:
        nums = 'NULL'
    f.write(f",,,,,{mail},{nums}\n\n")  
    print(f'\nProfile added...!')
    f.close()
    lock.release()

def google_search(link):
    html_text = requests.get(link).text
    soup = BeautifulSoup(html_text, "html.parser")
    cards = soup.find_all('div', class_='ZINbbc xpd O9g5cc uUPGi')
    for card in cards:
        head = card.h3.div.text.split('-')[0].strip()
        link = card.a['href'].split('%')[0].split('&')[0].split('=')[1]
        print(head,link)
        xy = threading.Thread(target=scrape_linkedin, args=(head,link))
        xy.start()

def get_links():
    global keys
    inst = input("Enter an Institute name : ")
    keys = input("Enter a Domain / Keyword : ")
    print(f"\nSearching - LinkedIn & {inst} for {keys}....\n")
    link = f'''https://www.google.com/search?q=site:in.linkedin.com "{inst}" AND "{keys}"'''
    
    links = []
    links.append(link)
    
    driver = driver_auth()
    driver.get(link)
    time.sleep(2)
    
    link = driver.find_element_by_xpath('''//div[@id = "center_col"]//div[@role = "navigation"]//table[@class = "AaVjTc"]//tr[@jsname ="TeSSVd"]''')
    for a in link.find_elements_by_xpath('.//a'):
        links.append(a.get_attribute('href'))
    driver.close()
    i=0
    for link in links:
        time.sleep(5)
        i=i+1
        google_search(link)

get_links()
print(f'\nScrapping & Saving results in {keys}.csv....\n')