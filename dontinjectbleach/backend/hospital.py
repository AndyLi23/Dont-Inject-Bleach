from requests import get
from bs4 import BeautifulSoup as BS
from datetime import timedelta, datetime
import csv



def search(city):
    try:
        URL = "https://doctor.webmd.com/hospital/results?so=&city=%s&state=%s&zip=%s" % (city.split(", ")[0], city.split(", ")[1], city.split(", ")[2])

        g = get(URL, allow_redirects=True)
        bs = BS(g.content, "html.parser")
        a = []
        for i in bs.find_all("li", attrs={"class": "result"}):
            temp = {}
            temp['href'], temp['name'] = "https://doctor.webmd.com" + i.findChild("a", href=True)['href'], i.findChild("a").get_text()
            temp["address"] = i.findChild("p", attrs={"class": "address"}).get_text(separator=", ").strip()
            y = 0
            for k in i.findChild("ul").find_all("li"):
                if y == 0:
                    temp["detail1"] = k.get_text()
                    y += 1
                else:
                    temp["detail2"] = k.get_text()
            a.append(temp)
        if len(a) < 1:
            return "Invalid Location"
        return a
    except:
        return "Invalid Location"