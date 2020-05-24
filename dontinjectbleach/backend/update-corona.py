from requests import get
from bs4 import BeautifulSoup as BS
from datetime import timedelta, datetime
import csv

if __name__ == '__main__':
    for i in range(1, 1000):
        today = datetime.utcnow().date()
        yesterday = str(today - timedelta(days=i)).split("-")
        yesterday = "-".join([yesterday[1],yesterday[2],yesterday[0]])
        print(yesterday)
        URL = "https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_daily_reports/" + yesterday + ".csv"
        r = get(URL)
        bs = BS(r.content, "html.parser")
        
        with open("../corona-data/data" + yesterday + ".csv", "w+") as fout:
            writer = csv.writer(fout)
            for i in bs.find_all("tr", attrs={"class":"js-file-line"}):
                writer.writerow(i.get_text().strip().split("\n"))
            fout.close()