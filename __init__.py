"""Kredsløb Tømning"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from datetime import date
import time

DOMAIN = "kredslobtomning"

def setup(hass, config):
    # Set default values
    hass.states.set("kredslobtomning.restaffald_date", "Not found yet")
    hass.states.set("kredslobtomning.madaffald_date", "Not found yet")
    hass.states.set("kredslobtomning.plastaffald_date", "Not found yet")
    hass.states.set("kredslobtomning.kartoneraffald_date", "Not found yet")
    hass.states.set("kredslobtomning.metalaffald_date", "Not found yet")
    hass.states.set("kredslobtomning.glasaffald_date", "Not found yet")
    hass.states.set("kredslobtomning.restaffald_days_until", -1)
    hass.states.set("kredslobtomning.madaffald_days_until", -1)
    hass.states.set("kredslobtomning.plastaffald_days_until", -1)
    hass.states.set("kredslobtomning.kartoneraffald_days_until", -1)
    hass.states.set("kredslobtomning.metalaffald_days_until", -1)
    hass.states.set("kredslobtomning.glasaffald_days_until", -1)

    def handle_checkNextDates(call):
        """Handle the service call."""

        daysUntil, nextDates, nextTrashTypes = checkNextDates()

        for days, nextDate, trashType in zip(daysUntil, nextDates, nextTrashTypes):
            if trashType == "Restaffald":
                hass.states.set("kredslobtomning.restaffald_days_until", days)
                hass.states.set("kredslobtomning.restaffald_date", nextDate)
            if trashType == "Madaffald":
                hass.states.set("kredslobtomning.madaffald_days_until", days)
                hass.states.set("kredslobtomning.madaffald_date", nextDate)

    hass.services.register(DOMAIN, "checkNextDates", handle_checkNextDates)

    
    # Return boolean to indicate that initialization was successful.
    return True 

def checkNextDates():
    address = 'Bronzealdervej 177, 8210 Aarhus V'

    browser = setupBrowser()
    acceptCookies(browser)
    status, text = enterAddressAndGetText(browser)
    if status == False:
        return

    emptyDates = getEmptyDates(text)
    daysUntil, nextDates, nextTrashTypes = getNextDates(emptyDates)

    return daysUntil, nextDates, nextTrashTypes
    

def setupBrowser():
    url = 'https://www.kredslob.dk/produkter-og-services/genbrug-og-affald/affaldsbeholdere/toemmekalender'

    # open browser
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')  # Last I checked this was necessary.
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)

    # load page
    driver.get(url)

    return driver

def acceptCookies(driver_):
    # Accept cookies
    driver_.find_element(By.XPATH, '//button[text()="Accepter alle"]').click()
    driver_.implicitly_wait(10)

def enterAddressAndGetText(driver_):
    # find field 
    item = driver_.find_element(By.CLASS_NAME, 'multiselect-search')

    # Enter address
    item.send_keys('Bronzealdervej 177, Hasle, 8210 Aarhus V')
    #item.send_keys('Bronzealdervej 2, Hasle, 8210 Aarhus V')
    time.sleep(2)
    item.send_keys(Keys.ENTER)
    time.sleep(2)

    # Click fortsæt
    item = driver_.find_element(By.XPATH, '//button[text()=" Fortsæt "]')
    item.click()
    #driver.find_element(By.XPATH, '//button[text()="Fortsæt"]').click()

    time.sleep(1)

    try:
        # Get text of tømnings-calender
        item = driver_.find_element(By.XPATH, '/html/body/main/div[2]/div/vue-collection-calendar/div/div[3]/div[1]/div[1]')
    except:
        print('Not a valid address')
        return False, ''
    
    return True, item.text

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

def getEmptyDates(text_):
    month = ''
    year = ''
    dato = ''
    weekday = ''
    trashType = ''
    splitText = text_.split('\n')
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
    
    return emptyDates

def getNextDates(emptyDates_):
    nextDates = []
    nextTrashTypes = []
    daysUntil = []
    today = date.today()
    for emptyDate in emptyDates_:
        print('{} bliver tømt {} den. {}. {} {}'.format(*emptyDate))
        if emptyDate[0] not in nextTrashTypes:
            nextTrashTypes.append(emptyDate[0])
            nextDates.append('{}. {} {}'.format(emptyDate[2], emptyDate[3], emptyDate[4]))
            garbageDate = date(int(emptyDate[4]), monthToInt(emptyDate[3]), int(emptyDate[2])) 
            daysUntil.append((garbageDate - today).days)
    
    return daysUntil, nextDates, nextTrashTypes