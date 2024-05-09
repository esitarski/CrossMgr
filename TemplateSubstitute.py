import re
from ReadSignOnSheet import BibInfo

reVariable = re.compile( r'\{=[^}]+\}' )

def TemplateSubstitute( s, keyValues ):
	bibInfo = BibInfo()
	
	iLast = 0
	components = []
	for m in reVariable.finditer(s):
		components.append( s[iLast:m.start()] )
		subkey = m.group()[2:-1]
		components.append( bibInfo.getSubValue(subkey) or keyValues.get(subkey, m.group() ) )
		iLast = m.end()
	components.append( s[iLast:] )
	return ''.join(components)
		
if __name__ == '__main__':
	s = '{=Organizer}: ({=City} {=StateProv} {=Country}) is {=Unknown} super!'
	keyValues = {
		'Organizer':	'Super Organizer',
		'City':			'Toronto',
		'StateProv':	'Ontario',
		'Country':		'Canada',
	}
	print( TemplateSubstitute(s, keyValues) )
