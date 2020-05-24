from requests import get
from bs4 import BeautifulSoup as BS
from datetime import timedelta, datetime
import csv

def updateCorona():
    with open("dontinjectbleach/corona-data/day.txt", "r") as fin:
        prev=fin.read().split("\n")
        prev, other = prev[0], prev[1]

        
    today = datetime.utcnow().date()
    yesterday = str(today - timedelta(days=1)).split("-")
    yesterday = "-".join([yesterday[1],yesterday[2],yesterday[0]])


    if prev != yesterday:
        URL = "https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_daily_reports/" + yesterday + ".csv"
        try:
            r = get(URL)
        except:
            yesterday = str(today - timedelta(days=2)).split("-")
            yesterday = "-".join([yesterday[1],yesterday[2],yesterday[0]])
            URL = "https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_daily_reports/" + yesterday + ".csv"
        bs = BS(r.content, "html.parser")
        
        with open("dontinjectbleach/corona-data/day.txt", "w") as fout:
            fout.write(yesterday + "\n" + other)
            fout.close()
        
        with open("dontinjectbleach/corona-data/data" + yesterday + ".csv", "w+") as fout:
            writer = csv.writer(fout)
            for i in bs.find_all("tr", attrs={"class":"js-file-line"}):
                writer.writerow(i.get_text().strip().split("\n"))
            fout.close()
            
        condense_corona()
            
