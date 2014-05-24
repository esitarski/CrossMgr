import re

reVariable = re.compile( u'\{=[^}]+\}' )

def TemplateSubstitute( s, keyValues ):
	iLast = 0
	components = []
	for m in reVariable.finditer(s):
		components.append( s[iLast:m.start()] )
		components.append( keyValues.get(m.group()[2:-1], m.group() ) )
		iLast = m.end()
	components.append( s[iLast:] )
	return u''.join(components)
		
if __name__ == '__main__':
	s = u'{=Organizer}: ({=City} {=StateProv} {=Country}) is {=Unknown} super!'
	keyValues = {
		u'Organizer':	u'Super Organizer',
		u'City':		u'Toronto',
		u'StateProv':	u'Ontario',
		u'Country':		u'Canada',
	}
	print TemplateSubstitute(s, keyValues)
