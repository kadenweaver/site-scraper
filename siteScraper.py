import requests
from email.message import EmailMessage
from bs4 import BeautifulSoup
import pickle
import os.path
from os import path
from datetime import datetime
import smtplib
import argparse
import sys

##use these global variables to edit the automated email sender and the password required to use that account
SCRIPT_EMAIL_ADDRESS = 'user_email_address@email_service.com'
SCRIPT_EMAIL_PASSWORD = 'password_hash'

def sendEmailText(sending, receiving, emailBody):
    gmail_user = sending
    gmail_password = SCRIPT_EMAIL_PASSWORD

    sent_from = gmail_user
    to = [receiving]
    body = emailBody.encode("ascii", "ignore").decode().strip()


    msg = EmailMessage()
    msg.set_content(body)

    msg['Subject'] = 'CL Update'
    msg['From'] = gmail_user
    msg['To'] = receiving

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.send_message(msg)
        server.quit()

        print('Email sent!')
    except Error as error:
        print('Something went wrong...\n')
        print(error)





def searchSingleKeyWord(keyWord, mainCity, cities):
    URL = 'https://' + mainCity + '.craigslist.org/search/sss?query=' + keyWord + '&purveyor-input=all'
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    links = soup.find_all('a')
    repeatLinks = set()
    historicLinks = set()
    historicLinksPath = "historicLinks" + "_" + keyWord + "_" + mainCity + ".p"
    if(path.exists(historicLinksPath)):
        historicLinks = pickle.load( open( historicLinksPath, "rb" ) )
    newLinks = [x for x in links if len(x.contents) > 0]
    newLinkNames = [x for x in newLinks if x.contents[0] != '\n' and x.contents[0] != 'save search']
    newLinkHRefs = [x for x in newLinkNames if x.get('href') != '#' and x.get('href') not in historicLinks and len([y for y in cities if y in x.get('href')]) > 0]
    responseText = ""
    if(len(newLinkHRefs) > 0):
      now = datetime.now()
      responseText = responseText + 'New ' + keyWord + ' links in ' + mainCity +'\n\n'
      for link in newLinkHRefs:
       names = link.contents[0]
       fullLink = link.get('href')
       if(fullLink not in repeatLinks):
           repeatLinks.add(fullLink)
           historicLinks.add(fullLink)
           responseText = responseText + names + '\n' + fullLink + '\n'
    else:
        responseText = responseText + ("There are no new " +  keyWord + " links.\n")
    if(len(historicLinks) > 0):
       pickle.dump( historicLinks, open( historicLinksPath, "wb" ) )

    return(responseText)

def searchMultipleKeyWords(listOfKeyWords, mainCity, cities):
    fullReport = ""
    for keyWord in listOfKeyWords:
        fullReport = fullReport + searchSingleKeyWord(keyWord, mainCity, cities) + '\n'

    return(fullReport)
    
    
##parsing methods
##take in command line arguments and format the input for the main method
def stringSingleOrListParse(inputString):
    if (not isinstance(inputString, str)) :
        raise argparse.ArgumentTypeError('String value of format {keyword(,) (keyword)(,)...} required.')
    try:
        if (',' in inputString):
            return inputString.split(",")
        else:
            return [str(inputString)]
    except:
        raise argparse.ArgumentTypeError('String value of format {keyword(,) (keyword)(,)...} required.')
        

def stringSingleReturn(inputString):
    try:
        return str(inputString)
    except:
        raise argparse.ArgumentTypeError('String value of format {city} required.')

        
def parseArgsAndStart():

    parser = argparse.ArgumentParser(description='Simple site scraper that queries CraigsList for a given search keyword and city')
    
    ## args are keyword(s) (list), city (string), and viable cities (list)
    parser.add_argument('keywords', type=stringSingleOrListParse,
        help='a string containing one or more keywords, separated by commas')
    parser.add_argument('city', type=stringSingleReturn,
        help='a string representing the city to search in lower case')
    parser.add_argument('viableCities', type=stringSingleOrListParse,
        help='a string containing one or more cities, separated by commas')
    parser.add_argument('recipient', type=stringSingleReturn,
        help='a string containing the recipient email address.')
    if(len(sys.argv) != 5):
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()
    
    ##inner functions are called to request the desired web page, construct the email body, and send the email
    emailText = ""
    emailText = emailText + searchMultipleKeyWords(args.keywords, args.city, args.viableCities)
    sendEmailText(SCRIPT_EMAIL_ADDRESS, args.recipient, emailText)


##don't forget to call the parse method to kick off the script
parseArgsAndStart()
