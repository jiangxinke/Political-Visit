from newspaper import fulltext

html = requests.get(...).text
text = fulltext(html)
