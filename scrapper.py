import requests
import html5lib
import re
import json

from bs4 import BeautifulSoup 
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from googlesearch import search #modulename -- google
from selenium.webdriver.common.proxy import Proxy, ProxyType

#my modules
import mail as emailclient

# file paths
keywordfile = './keywords.txt'
urlfile = './urls.txt'
emailfile = './emails.txt'
messagefile='./messagefile'
dumpfile='./dumpfile.txt'

#email and password
myemail = 'ajinr@virtualmaze.co.in'
mypassword = 'reset@369'


#proxy url
proxyurl="http://pubproxy.com/api/proxy?google=true&https=true&user_agent=true"

def log(string):
    print(string)


def getDataFromFile(filePath):  #read the given file and returns lines in the file as a list
    lines = []
    with open(filePath, 'r') as file:
        line = file.readline()
        while line:
            lines.append(line.rstrip())
            line = file.readline()
    return list(set(lines))

def getProxy(url):
    response=requests.get(url)
    proxyresponse=response.json()["data"][0]
    return proxyresponse['ipPort']


def getLinksFromGoogle(query, limit): # returns google search results url in a list 
    log('getting links for keyword ' + query)
    urls = []
    for url in search(query, num=10, stop=limit, pause=2):
        urls.append(url)
    log('getting links for keyword ' + query + 'completed')
    return urls



def writeDataToAFile(data, filepath):  # writes given urls into a file
    with open(filepath, 'a+') as file:
        for value in data:
            file.write(value + '\n')


def getUrls(keywords, urlfile):  
    for key in keywords:
        urls = getLinksFromGoogle(key, limit=50)
        writeDataToAFile(urls, urlfile)

def getDynamicSourceCode(url): #get dynamic source code of the given url and returns it
    log("getting dynamic sourceCode for url " + url)
    driver = webdriver.Firefox()
    driver.set_page_load_timeout(30)
    try:
        driver.get(url)
        try:
            alert = driver.switch_to.alert()
            alert.dismiss()
        except:
            print("")
    except TimeoutException:
        log('request timed out' + url)
        driver.close()
        return None
    except:
        log('error in getting source for ' + url)
        driver.close()
        return None
    source=driver.page_source
    formattedsource=BeautifulSoup(source,'html5lib')
    driver.close()
    return formattedsource

def getEmailFromSource(dynamicsourcecode):  #returns a list of emails in the source code
    emailre=r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+" 
    emails=re.findall(emailre, dynamicsourcecode.get_text())
    return list(set(emails))
    

def getPhoneNumbers(sourcecode): #returns a list of phone numbers in the source code
    phonenumberlist=[]
    try:
      phoneno= sourcecode.select("a[href*=callto]")[0].text
      if phoneno:
          phonenumberlist.append(phoneno)
    except:
        print(' ')
    phonere=[r'\(?\b[2-9][0-9]{2}\)?[-. ]?[2-9][0-9]{2}[-. ]?[0-9]{4}\b', r'\(?\b[2-9][0-9]{2}\)?[-][2-9][0-9]{2}[-][0-9]{4}\b']
    
    for regex in phonere:
      phonenos=re.findall(regex,sourcecode.get_text())
      phonenumberlist=phonenumberlist+phonenos

    return list(set(phonenumberlist))
        

def dumpData(dumpfile,emails,phonenumbers , url):  #dump phonenumbers and emails into a file
    with open(dumpfile,'a+') as dfile:
        emailstring='  '.join(str(e) for e in emails)
        phonenumberstring='  '.join(str(e) for e in phonenumbers)
        dfile.write("url --- " + url + "\n")
        dfile.write("emails -- " + emailstring + '\n')
        dfile.write("phonenumbers -- " + phonenumberstring + '\n\n\n')





def scrapContactDetails(urlfile,emailfile):
    urls=getDataFromFile(urlfile) 
    for url in urls:
        dynamicsourcecode=getDynamicSourceCode(url)
        if dynamicsourcecode!=None:
            emails=getEmailFromSource(dynamicsourcecode)
            phonenumbers=getPhoneNumbers(dynamicsourcecode)
            dumpData(dumpfile,emails , phonenumbers ,url)
            writeDataToAFile(emails,emailfile)

def sendEmailToClients(emailfile,messagefile):
    message = emailclient.getMsg(messagefile)
    emails = getDataFromFile(emailfile)
    emailclient.sendMail(emails, message, myemail, mypassword)


def main():  #main function
     keywords = getDataFromFile(keywordfile)
     getUrls(keywords, urlfile)
     scrapContactDetails(urlfile,emailfile)
     # sendEmailToClients(emailfile,messagefile)

main()

