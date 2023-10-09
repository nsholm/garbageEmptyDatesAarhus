from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from datetime import date
import time


# Følg guide på https://stackoverflow.com/questions/62788496/insert-text-in-a-website-and-scrape-generated-request

url = 'https://www.kredslob.dk/produkter-og-services/genbrug-og-affald/affaldsbeholdere/toemmekalender'

# open browser
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')  # Last I checked this was necessary.
driver = webdriver.Chrome(options=options)
driver.implicitly_wait(10)

# load page
driver.get(url)

# Accept cookies
driver.find_element(By.XPATH, '//button[text()="Accepter alle"]').click()
driver.implicitly_wait(10)

# find field 
item = driver.find_element(By.CLASS_NAME, 'multiselect-search')

# Enter address
item.send_keys('Bronzealdervej 177, Hasle, 8210 Aarhus V')
#item.send_keys('Bronzealdervej 2, Hasle, 8210 Aarhus V')
time.sleep(2)
item.send_keys(Keys.ENTER)
time.sleep(2)

# Click fortsæt
item = driver.find_element(By.XPATH, '//button[text()=" Fortsæt "]')
item.click()
#driver.find_element(By.XPATH, '//button[text()="Fortsæt"]').click()

time.sleep(1)

try:
    # Get text of tømnings-calender
    item = driver.find_element(By.XPATH, '/html/body/main/div[2]/div/vue-collection-calendar/div/div[3]/div[1]/div[1]')
except:
    print('Not a valid address')
    exit()

def isMonthYear(text_):
    if len(text_.split(' ')) != 2:
        return False
    
    months = ['Januar', 'Februar', 'Marts', 'April', 'Maj', 'Juni', 'Juli', 'August', 'September','Oktober','November','December']

    if text_.split(' ')[0] in months:
        return True
    
    return False

def isGarbageType(text_):
    garbageTypes = ['Restaffald', 'Madaffald', 'Papir', 'Pap', 'Glas', 'Metal', 'Mad- og drikkekartoner']

    if text_ in garbageTypes:
        return True
    
    return False

def isDateType(text_):
    if len(text_.split(' ')) != 3:
        return False
    
    weekdays = ['Mandag', 'Tirsdag', 'Onsdag', 'Torsdag', 'Fredag', 'Lørdag', 'Søndag', 'Man.', 'Tirs.', 'Ons.', 'Tors.', 'Fre.', 'Lør.', 'Søn.']

    if text_.split(' ')[0] not in weekdays:
        return False
    
    if text_.split(' ')[1] not in ['den', 'd.']:
        return False
    
    return True

def monthToInt(month_):
    months = ['Januar', 'Februar', 'Marts', 'April', 'Maj', 'Juni', 'Juli', 'August', 'September','Oktober','November','December']

    return months.index(month_) + 1

month = ''
year = ''
dato = ''
weekday = ''
trashType = ''
splitText = item.text.split('\n')
emptyDates = []
for i in range(len(splitText)):
    text = splitText[i]

    if isMonthYear(text) == True:
        month = text.split(' ')[0]
        year = text.split(' ')[1]
    
    if isDateType(text):
        weekday = text.split(' ')[0]
        dato = text.split(' ')[2].replace('.','')
        c = i - 1
        while(isGarbageType(splitText[c])):
            trashType = splitText[c]
            emptyDates.append([trashType, weekday, dato, month, year])
            c -= 1

nextDates = []
nextTrashTypes = []
daysUntil = []
today = date.today()
for emptyDate in emptyDates:
    print('{} bliver tømt {} den. {}. {} {}'.format(*emptyDate))
    if emptyDate[0] not in nextTrashTypes:
        nextTrashTypes.append(emptyDate[0])
        nextDates.append('{}. {} {}'.format(emptyDate[2], emptyDate[3], emptyDate[4]))
        garbageDate = date(int(emptyDate[4]), monthToInt(emptyDate[3]), int(emptyDate[2])) 
        daysUntil.append((garbageDate - today).days)

print('\n')

for days, nextDate, trashType in zip(daysUntil, nextDates, nextTrashTypes):
    if days == 0:
        daysText = 'i dag'
    elif days == 1:
        daysText = 'om 1 dag'
    else:
        daysText = 'om {} dage'.format(days)
    print('{} bliver tømt {} den {}'.format(trashType, daysText, nextDate))