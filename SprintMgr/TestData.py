import random
import operator

def getTestData():
	results = '''
1	Gregory Bauge (France)	9.854	 
2	Robert Foerstemann (Germany)	9.873	 
3	Kevin Sireau (France)	9.893	 
4	Chris Hoy (Great Britain)	9.902	 
5	Matthew Glaetzer (Australia)	9.902	 
6	Jason Kenny (Great Britain)	9.953	 
7	Edward Dawkins (New Zealand)	9.963	 
8	Shane Perkins (Australia)	9.965	 
9	Mickael Bourgain (France)	9.966	 
10	Stefan Boetticher (Germany)	9.983	 
11	Seiichiro Nakagawa (Japan)	10.003	 
12	Matthew Archibald (New Zealand)	10.034	 
13	Scott Sunderland (Australia)	10.040	 
14	Miao Zhang (People's Republic of China)	10.061	 
15	Hersony Canelon (Venezuela)	10.077	 
16	Rene Enders (Germany)	10.077	 
17	Juan Peralta Gascon (Spain)	10.101	 
18	Michael Blatchford (United States Of America)	10.118	 
19	Sam Webster (New Zealand)	10.122	 
20	Kazunari Watanabe (Japan)	10.159	 
21	Ethan Mitchell (New Zealand)	10.163	 
22	Hodei Mazquiaran Uria (Spain)	10.163	 
23	Matthew Crampton (Great Britain)	10.167	 
24	Charlie Conord (France)	10.169	 
25	Nikita Shurshin (Russian Federation)	10.178	 
26	Damian Zielinski (Poland)	10.192
'''

	testData = []
	
	for n, line in enumerate(results.split('\n')):
		fields = line.split()
		if len(fields) < 2:
			continue
		bib = fields[0]
		first_name = ''
		last_name = ''
		team = ''
		qt = float(fields[-1])
		
		i = len(fields) - 2
		while 1:
			team = fields[i] + (' ' if team else '') + team
			if fields[i].startswith('('):
				break
			i -= 1
		team = team[1:-1]
				
		i -= 1
		last_name = fields[i]
		
		i -= 1
		while i > 0:
			first_name = fields[i] + (' ' if first_name else '') + first_name
			i -= 1
			
		testData.append( {
			'bib':bib,
			'first_name':first_name, 'last_name':last_name,
			'team':team,
			'qualifying_time':qt,
			'uci_points':1000-n,
		} )

	testData.reverse()
	return testData
	
def getRandomTestData( starters = 64 ):
	firstNames = '''
1. Noah
2. Liam
3. Jacob
4. Mason
5. William
6. Ethan
7. Michael
8. Alexander
9. Jayden
10. Daniel
11. Elijah
12. Aiden
13. James
14. Benjamin
15. Matthew
16. Jackson
17. Logan
18. David
19. Anthony
20. Joseph
21. Joshua
22. Andrew
23. Lucas
24. Gabriel
25. Samuel
26. Christopher
27. John
28. Dylan
29. Isaac
30. Ryan
31. Nathan
32. Carter
33. Caleb
34. Luke
35. Christian
36. Hunter
37. Henry
38. Owen
39. Landon
40. Jack
41. Wyatt
42. Jonathan
43. Eli
44. Isaiah
45. Sebastian
46. Jaxon
47. Julian
48. Brayden
49. Gavin
50. Levi
51. Aaron
52. Oliver
53. Jordan
54. Nicholas
55. Evan
56. Connor
57. Charles
58. Jeremiah
59. Cameron
60. Adrian
61. Thomas
62. Robert
63. Tyler
64. Colton
65. Austin
66. Jace
67. Angel
68. Dominic
69. Josiah
70. Brandon
71. Ayden
72. Kevin
73. Zachary
74. Parker
75. Blake
76. Jose
77. Chase
78. Grayson
79. Jason
80. Ian
81. Bentley
82. Adam
83. Xavier
84. Cooper
85. Justin
86. Nolan
87. Hudson
88. Easton
89. Jase
90. Carson
91. Nathaniel
92. Jaxson
93. Kayden
94. Brody
95. Lincoln
96. Luis
97. Tristan
98. Damian
99. Camden
100. Juan
'''

	lastNames = '''
1. Smith  
2. Johnson  
3. Williams  
4. Jones  
5. Brown  
6. Davis  
7. Miller  
8. Wilson  
9. Moore  
10. Taylor  
11. Anderson  
12. Thomas  
13. Jackson  
14. White  
15. Harris  
16. Martin  
17. Thompson  
18. Garcia  
19. Martinez  
20. Robinson  
21. Clark  
22. Rodriguez  
23. Lewis  
24. Lee  
25. Walker  
26. Hall  
27. Allen  
28. Young  
29. Hernandez  
30. King  
31. Wright  
32. Lopez  
33. Hill  
34. Scott  
35. Green  
36. Adams  
37. Baker  
38. Gonzalez  
39. Nelson  
40. Carter  
41. Mitchell  
42. Perez  
43. Roberts  
44. Turner  
45. Phillips  
46. Campbell  
47. Parker  
48. Evans  
49. Edwards  
50. Collins  
51. Stewart  
52. Sanchez  
53. Morris  
54. Rogers  
55. Reed  
56. Cook  
57. Morgan  
58. Bell  
59. Murphy  
60. Bailey  
61. Rivera  
62. Cooper  
63. Richardson  
64. Cox  
65. Howard  
66. Ward  
67. Torres  
68. Peterson  
69. Gray  
70. Ramirez  
71. James  
72. Watson  
73. Brooks  
74. Kelly  
75. Sanders  
76. Price  
77. Bennett  
78. Wood  
79. Barnes  
80. Ross  
81. Henderson  
82. Coleman  
83. Jenkins  
84. Perry  
85. Powell  
86. Long  
87. Patterson  
88. Hughes  
89. Flores  
90. Washington  
91. Butler  
92. Simmons  
93. Foster  
94. Gonzales  
95. Bryant   
96. Alexander  
97. Russell  
98. Griffin   
99. Diaz  
'''

	teams = '''
The Cyclomaniacs
Pesky Peddlers
Geared Up
Spoke & Mirrors
The Handlebar Army
Wheels of Steel
The Chaingang
Saddled & Addled
The Cyclepaths
Tour de Farce
Old Cranks
Magically Bikelicious
Look Ma No Hands!
Pedal Pushers
Kicking Asphault
Velociposse
Road Rascals
Spin Doctors
'''

	firstNames = [line.split('.')[1].strip() for line in firstNames.split('\n') if line.strip()]
	lastNames = [line.split('.')[1].strip() for line in lastNames.split('\n') if line.strip()]
	teams = [line.strip() for line in teams.split('\n') if line.strip()]
	bibs = list( range(100, 100+starters) )
	
	random.shuffle( firstNames )
	random.shuffle( lastNames )
	random.shuffle( teams )
	random.shuffle( bibs )
	
	testData = []
	for i, bib in enumerate(bibs):
		qt = random.gauss( 12.0, 0.5 )
		testData.append( {
				'bib':bib,
				'first_name':		firstNames[i%len(firstNames)],
				'last_name':		lastNames[i%len(lastNames)],
				'team':				teams[i%len(teams)],
				'qualifying_time':	qt,
				'uci_points':		i+20,
			}
		)

	testData.sort( key = lambda v: v['qualifying_time'], reverse=True )
	return testData

if __name__ == "__main__":
	print ( getTestData() )
	print ( getRandomTestData(100) )
