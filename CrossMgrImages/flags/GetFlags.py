
import os
import urllib2
from bs4 import BeautifulSoup

page = urllib2.urlopen( 'https://en.wikipedia.org/wiki/List_of_IOC_country_codes' )
soup = BeautifulSoup( page.read() )

code = ''
for td in soup.find_all('td'):
	if td.get('align',None) == 'center' and len(td.string) == 3 and td.string.upper() == td.string:
		code = td.string
		continue
	if not td.img:
		continue
	img = td.img
	if 'thumbborder' not in img.get('class',[]):
		continue
	src = img['src']
	if not src.startswith('//upload.'):
		continue

	print code
	with open( '{}.png'.format(code), 'wb' ) as f:
		f.write( urllib2.urlopen('http:' + src).read() )
