from requests import get
from bs4 import BeautifulSoup as BS

r = get("https://coronavirus.1point3acres.com/en")
bs = BS(r.content, "html.parser")

print(bs)