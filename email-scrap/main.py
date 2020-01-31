import http.cookiejar as cookielib
import pandas as pd
from pandas import ExcelWriter
import bs4
import mechanize
import json
from bs4 import BeautifulSoup
import requests
import urllib

client = requests.Session()

def read_data():
    df = pd.read_excel('old.xls')   
    return df['Email address - other'].to_numpy()

if __name__ == "__main__":
    emails = read_data()
    # Browser
    brow = mechanize.Browser()

    # Cookie Jar
    cj = cookielib.LWPCookieJar()
    brow.set_cookiejar(cj)

    # Browser options
    brow.set_handle_equiv(True)
    brow.set_handle_gzip(True)
    brow.set_handle_redirect(True)
    brow.set_handle_referer(True)
    brow.set_handle_robots(False)
    brow.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

    brow.addheaders = [('User-agent', 'Chrome')]
    brow.open('https://www.linkedin.com/login')

    # Select the second (index one) form (the first form is a search query box)
    brow.select_form(nr=0)

    # User credentials
    brow.form['session_key'] = 'test@email.com'
    brow.form['session_password'] = 'test'

    # Login
    response = brow.submit().read()
    data = list()
    for email in emails:
        soup = BeautifulSoup(brow.open('https://www.linkedin.com/sales/gmail/profile/viewByEmail/{}'.format(email)).read(), 'html5lib')
        first_last_name = soup.find('span', attrs={'id': 'li-profile-name'}, text=True)
        if first_last_name is None:
            data.append([None, None, email])
            continue
        else: 
            names_list = first_last_name.get_text().split(' ')

            if len(names_list) > 2:
               data.append([names_list[0], names_list[2], email])
            else:
              data.append([names_list[0], names_list[1], email])

    df = pd.DataFrame(data=data, columns=['first name', 'last name', 'email'])
    writer = ExcelWriter('new.xls')
    df.to_excel(writer,'Sheet1',index=False)
    writer.save()
