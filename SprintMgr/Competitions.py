import copy
import random
import Model
from Model import Competition, System, Event
from TestData import getTestData, getRandomTestData

def getCompetitions():
	competitions = [
		Competition( 'Track: Sprint Nations Cup and World Championships', [
			System( '1/16 Finals', [
				Event( 'N1 - -> 1A' ),
				Event( 'N2 - -> 2A' ),
				Event( 'N3 - -> 3A' ),
				Event( 'N4 - -> 4A' ),
				Event( 'N5 - N28 -> 5A' ),
				Event( 'N6 - N27 -> 6A' ),
				Event( 'N7 - N26 -> 7A' ),
				Event( 'N8 - N25 -> 8A' ),
				Event( 'N9 - N24 -> 9A' ),
				Event( 'N10 - N23 -> 10A' ),
				Event( 'N11 - N22 -> 11A' ),
				Event( 'N12 - N21 -> 12A' ),
				Event( 'N13 - N20 -> 13A' ),
				Event( 'N14 - N19 -> 14A' ),
				Event( 'N15 - N18 -> 15A' ),
				Event( 'N16 - N17 -> 16A' ),
				]),
			System( '1/8 Finals', [
				Event( '1A - 16A -> 1B' ),
				Event( '2A - 15A -> 2B' ),
				Event( '3A - 14A -> 3B' ),
				Event( '4A - 13A -> 4B' ),
				Event( '5A - 12A -> 5B' ),
				Event( '6A - 11A -> 6B' ),
				Event( '7A - 10A -> 7B' ),
				Event( '8A - 9A -> 8B' ),
			]),
			System( '1/4 Finals', [
				Event( '1B - 8B -> 1C', 3 ),
				Event( '2B - 7B -> 2C', 3 ),
				Event( '3B - 6B -> 3C', 3 ),
				Event( '4B - 5B -> 4C', 3 ),
			]),
			System( '1/2 Finals', [
				Event( '1C - 4C -> 1D1 - 1D2', 3 ),
				Event( '2C - 3C -> 2D1 - 2D2', 3 ),
			]),
			System( 'Finals', [
				Event( '1D2 - 2D2 -> 3R - 4R', 3 ),
				Event( '1D1 - 2D1 -> 1R - 2R', 3 ),
			]),
		]),
		
		Competition( 'Track: Sprint Olympic Games', [
			System( '1/32 Finals', [
				Event( 'N1 - N24 -> 1A1 - 1A2' ),
				Event( 'N2 - N23 -> 2A1 - 2A2' ),
				Event( 'N3 - N22 -> 3A1 - 3A2' ),
				Event( 'N4 - N21 -> 4A1 - 4A2' ),
				Event( 'N5 - N20 -> 5A1 - 5A2' ),
				Event( 'N6 - N19 -> 6A1 - 6A2' ),
				Event( 'N7 - N18 -> 7A1 - 7A2' ),
				Event( 'N8 - N17 -> 8A1 - 8A2' ),
				Event( 'N9 - N16 -> 9A1 - 9A2' ),
				Event( 'N10 - N15 -> 10A1 - 10A2' ),
				Event( 'N11 - N14 -> 11A1 - 11A2' ),
				Event( 'N12 - N13 -> 12A1 - 12A2' ),
			]),
			System( 'Repechages 1', [
				Event( '1A2 - 8A2 - 9A2 -> 1B' ),
				Event( '2A2 - 7A2 - 10A2 -> 2B' ),
				Event( '3A2 - 6A2 - 11A2 -> 3B' ),
				Event( '4A2 - 5A2 - 12A2 -> 4B' ),
			]),
			System( '1/16 Finals', [
				Event( '1A1 - 4B -> 1C1 - 1C2' ),
				Event( '2A1 - 3B -> 2C1 - 2C2' ),
				Event( '3A1 - 2B -> 3C1 - 3C2' ),
				Event( '4A1 - 1B -> 4C1 - 4C2' ),
				Event( '5A1 - 12A1 -> 5C1 - 5C2' ),
				Event( '6A1 - 11A1 -> 6C1 - 6C2' ),
				Event( '7A1 - 10A1 -> 7C1 - 7C2' ),
				Event( '8A1 - 9A1 -> 8C1 - 8C2' ),
			]),
			System( 'Repechages 2', [
				Event( '1C2 - 8C2 -> 1D1' ),
				Event( '2C2 - 7C2 -> 2D1' ),
				Event( '3C2 - 6C2 -> 3D1' ),
				Event( '4C2 - 5C2 -> 4D1' ),
			]),
			System( '1/8 Finals', [
				Event( '1C1 - 4D1 -> 1E1 - 1E2', 3 ),
				Event( '2C1 - 3D1 -> 2E1 - 2E2', 3 ),
				Event( '3C1 - 2D1 -> 3E1 - 3E2', 3 ),
				Event( '4C1 - 1D1 -> 4E1 - 4E2', 3 ),
				Event( '5C1 - 8C1 -> 5E1 - 5E2', 3 ),
				Event( '6C1 - 7C1 -> 6E1 - 6E2', 3 ),
			]),
			System( 'Repechages 3', [
				Event( '1E2 - 4E2 - 5E2 -> 1F1' ),
				Event( '2E2 - 3E2 - 6E2 -> 2F1' ),
			]),
			System( '1/4 Finals (5-8)', [
				Event( '4E1 - 5E1 -> 4G1 - R8', 3 ),
				Event( '3E1 - 6E1 -> 3G1 - R7', 3 ),
				Event( '2E1 - 1F1 -> 2G1 - R6', 3 ),
				Event( '1E1 - 2F1 -> 1G1 - R5', 3 ),
			]),
			System( '1/2 Finals', [
				Event( '1G1 - 4G1 -> 1H1 - 1H2', 3 ),
				Event( '2G1 - 3G1 -> 2H1 - 2H2', 3 ),
			]),
			System( 'Finals', [
				Event( '1H2 - 2H2 -> 3R - 4R', 3 ),
				Event( '1H1 - 2H1 -> 1R - 2R', 3 ),
			]),
		]),
		
		Competition( 'Track: Sprint Half WC', [
			System( '1/8 Finals', [
				Event( 'N1 - N16 -> 1B' ),
				Event( 'N2 - N15 -> 2B' ),
				Event( 'N3 - N14 -> 3B' ),
				Event( 'N4 - N13 -> 4B' ),
				Event( 'N5 - N12 -> 5B' ),
				Event( 'N6 - N11 -> 6B' ),
				Event( 'N7 - N10 -> 7B' ),
				Event( 'N8 - N9 -> 8B' ),
			]),
			System( '1/4 Finals', [
				Event( '1B - 8B -> 1C', 3 ),
				Event( '2B - 7B -> 2C', 3 ),
				Event( '3B - 6B -> 3C', 3 ),
				Event( '4B - 5B -> 4C', 3 ),
			]),
			System( '1/2 Finals', [
				Event( '1C - 4C -> 1D1 - 1D2', 3 ),
				Event( '2C - 3C -> 2D1 - 2D2', 3 ),
			]),
			System( 'Finals', [
				Event( '1D2 - 2D2 -> 3R - 4R', 3 ),
				Event( '1D1 - 2D1 -> 1R - 2R', 3 ),
			]),
		]),
		
		Competition( 'Track: Sprint Quarter WC', [
			System( '1/4 Finals', [
				Event( 'N1 - N8 -> 1C', 3 ),
				Event( 'N2 - N7 -> 2C', 3 ),
				Event( 'N3 - N6 -> 3C', 3 ),
				Event( 'N4 - N5 -> 4C', 3 ),
			]),
			System( '1/2 Finals', [
				Event( '1C - 4C -> 1D1 - 1D2', 3 ),
				Event( '2C - 3C -> 2D1 - 2D2', 3 ),
			]),
			System( 'Finals', [
				Event( '1D2 - 2D2 -> 3R - 4R', 3 ),
				Event( '1D1 - 2D1 -> 1R - 2R', 3 ),
			]),
		]),
		
		Competition( 'Track: Sprint Eighth WC + 2', [
			System( '5-6 Final', [
				Event( 'N5 - N6 -> 5R - 6R' ),
			]),
			System( '1/2 Finals', [
				Event( 'N1 - N4 -> 1C1 - 1C2', 3 ),
				Event( 'N2 - N3 -> 2C1 - 2C2', 3 ),
			]),
			System( 'Finals', [
				Event( '1C1 - 2C1 -> 1R - 2R', 3 ),
				Event( '1C2 - 2C2 -> 3R - 4R', 3 )
			]),
		]),
		
		Competition( 'Track: Sprint Sixteenth WC', [
			System( '1/2 Finals', [
				Event( 'N1 - N4 -> 1C1 - 1C2', 3 ),
				Event( 'N2 - N3 -> 2C1 - 2C2', 3 ),
			]),
			System( 'Finals', [
				Event( '1C1 - 2C1 -> 1R - 2R', 3 ),
				Event( '1C2 - 2C2 -> 3R - 4R', 3 )
			]),
		]),
		
		Competition( 'Track: Sprint Direct Final', [
			System( 'Finals', [
				Event( 'N1 - N2 -> 1R - 2R', 3 ),
			]),
		]),
	]
	
	#-----------------------------------------------------------------------------------------
	competitions.append(
		Competition( 'Track: Keirin 12-14', [
			System( '1st Round', [
				Event( 'N1 N4 N5 N8  N9 N12 N13 -> QA1 QA2 QA3 QA4 QA5 QA6 QA7' ),
				Event( 'N2 N3 N6 N7 N10 N11 N14 -> QB1 QB2 QB3 QB4 QB5 QB6 QB7' ),
			]),
			System( 'Small Final 7-12', [
				Event( 'QA4 QA5 QA6 QB4 QB5 QB6 -> 7R 8R 9R 10R 11R 12R' ),
			]),
			System( 'Final Round 1-6', [
				Event( 'QA1 QA2 QA3 QB1 QB2 QB3 -> 1R 2R 3R 4R 5R 6R' ),
			]),
		])
	)
	competitions.append(
		Competition( 'Track: Keirin 15-20', [
			System( '1st Round', [
				Event( 'N1 N6 N7 N12 N13 N18 N19 -> QA1 QA2 QA3 QA4 QA5 QA6 QA7' ),
				Event( 'N2 N5 N8 N11 N14 N17 N20 -> QB1 QB2 QB3 QB4 QB5 QB6 QB7' ),
				Event( 'N3 N4 N9 N10 N15 N16     -> QC1 QC2 QC3 QC4 QC5 QC6' ),
			]),
			System( 'Repechages', [
				Event( 'QA3 QA4 QB4 QB5 QC5 QC6 QA7 -> rA1 rA2 rA3 1EE 2EE 3EE' ),
				Event( 'QB3 QC3 QC4 QA5 QA6 QB6 QB7 -> rB1 rB2 rB3 4EE 5EE 6EE' ),
			]),
			System( '2nd Round (1/2 Finals)', [
				Event( 'QA1 QC1 QB2 rA1 rB2 rA3 -> FA1 FA2 FA3 FA4 FA5 FA6' ),
				Event( 'QB1 QA2 QC2 rB1 rA2 rB3 -> FB1 FB2 FB3 FB4 FB5 FB6' ),
			]),
			System( 'Small Final 7-12', [
				Event( 'FA4 FA5 FA6 FB4 FB5 FB6 -> 7R 8R 9R 10R 11R 12R' ),
			]),
			System( 'Final Round 1-6', [
				Event( 'FA1 FA2 FA3 FB1 FB2 FB3 -> 1R 2R 3R 4R 5R 6R' ),
			]),
		])
	)
	competitions.append(
		Competition( 'Track: Keirin 21', [
			System( '1st Round', [
				Event( 'N1 N6 N7 N12 N13 N18 N19 -> QA1 QA2 QA3 QA4 QA5 QA6 QA7' ),
				Event( 'N2 N5 N8 N11 N14 N17 N20 -> QB1 QB2 QB3 QB4 QB5 QB6 QB7' ),
				Event( 'N3 N4 N9 N10 N15 N16 N21 -> QC1 QC2 QC3 QC4 QC5 QC6 QC7' ),
			]),
			System( 'Repechages', [
				Event( 'QA3 QC4 QA5 QC6 QA7 -> rA1 rA2 1EE 2EE 3EE' ),
				Event( 'QB3 QB4 QB5 QB6 QB7 -> rB1 rB2 4EE 5EE 6EE' ),
				Event( 'QC3 QA4 QC5 QA6 QC7 -> rC1 rC2 7EE 8EE 9EE' ),
			]),
			System( '2nd Round (1/2 Finals)', [
				Event( 'QA1 QC1 QB2 rA1 rC1 rB2 -> FA1 FA2 FA3 FA4 FA5 FA6' ),
				Event( 'QB1 QA2 QC2 rB1 rA2 rC2 -> FB1 FB2 FB3 FB4 FB5 FB6' ),
			]),
			System( 'Small Final 7-12', [
				Event( 'FA4 FA5 FA6 FB4 FB5 FB6 -> 7R 8R 9R 10R 11R 12R' ),
			]),
			System( 'Final Round 1-6', [
				Event( 'FA1 FA2 FA3 FB1 FB2 FB3 -> 1R 2R 3R 4R 5R 6R' ),
			]),
		])
	)
	competitions.append(
		Competition( 'Track: Keirin 22-28', [
			System( '1st Round', [
				Event( 'N1 N8  N9 N16 N17 N24 N25 -> QA1 QA2 QA3 QA4 QA5 QA6 QA7' ),
				Event( 'N2 N7 N10 N15 N18 N23 N26 -> QB1 QB2 QB3 QB4 QB5 QB6 QB7' ),
				Event( 'N3 N6 N11 N14 N19 N22 N27 -> QC1 QC2 QC3 QC4 QC5 QC6 QC7' ),
				Event( 'N4 N5 N12 N13 N20 N21 N28 -> QD1 QD2 QD3 QD4 QD5 QD6 QD7' ),
			]),
			System( 'Repechages', [
				Event( 'QA3 QD4 QC5 QB6 QA7 -> rA1  1EE  2EE  3EE  4EE' ),
				Event( 'QB3 QC4 QB5 QA6 QD7 -> rB1  5EE  6EE  7EE  8EE' ),
				Event( 'QC3 QB4 QA5 QD6 QC7 -> rC1  9EE 10EE 11EE 12EE' ),
				Event( 'QD3 QA4 QD5 QC6 QB7 -> rD1 13EE 14EE 15EE 16EE' ),
			]),
			System( '2nd Round (1/2 Finals)', [
				Event( 'QA1 QD1 QB2 QC2 rA1 rD1 -> FA1 FA2 FA3 FA4 FA5 FA6' ),
				Event( 'QB1 QC1 QA2 QD2 rB1 rC1 -> FB1 FB2 FB3 FB4 FB5 FB6' ),
			]),
			System( 'Small Final 7-12', [
				Event( 'FA4 FA5 FA6 FB4 FB5 FB6 -> 7R 8R 9R 10R 11R 12R' ),
			]),
			System( 'Final Round 1-6', [
				Event( 'FA1 FA2 FA3 FB1 FB2 FB3 -> 1R 2R 3R 4R 5R 6R' ),
			]),
		])
	)
	competitions.append(
		Competition( 'Track: Keirin 29-42', [
			System( '1st Round', [
				Event( 'N1 N12 N13 N24 N25 N36 N37 -> QA1 QA2 QA3 QA4 QA5 QA6 QA7' ),
				Event( 'N2 N11 N14 N23 N26 N35 N38 -> QB1 QB2 QB3 QB4 QB5 QB6 QB7' ),
				Event( 'N3 N10 N15 N22 N27 N34 N39 -> QC1 QC2 QC3 QC4 QC5 QC6 QC7' ),
				Event( 'N4  N9 N16 N21 N28 N33 N40 -> QD1 QD2 QD3 QD4 QD5 QD6 QD7' ),
				Event( 'N5  N8 N17 N20 N29 N32 N41 -> QE1 QE2 QE3 QE4 QE5 QE6 QE7' ),
				Event( 'N6  N7 N18 N19 N30 N31 N42 -> QF1 QF2 QF3 QF4 QF5 QF6 QF7' ),
			]),
			System( 'Repechages', [
				Event( 'QA2 QF3 QE4 QD5 QC6 QB7 -> rA1  1EE  2EE  3EE  4EE' ),
				Event( 'QB2 QE3 QD4 QC5 QB6 QA7 -> rB1  5EE  6EE  7EE  8EE' ),
				Event( 'QC2 QD3 QC4 QB5 QA6 QF7 -> rC1  9EE 10EE 11EE 12EE' ),
				Event( 'QD2 QC3 QB4 QA5 QF6 QE7 -> rD1 13EE 14EE 15EE 16EE' ),
				Event( 'QE2 QB3 QA4 QF5 QE6 QD7 -> rE1 17EE 18EE 19EE 20EE' ),
				Event( 'QF2 QA3 QF4 QE5 QD6 QC7 -> rF1 21EE 22EE 23EE 24EE' ),
			]),
			System( '2nd Round (1/2 Finals)', [
				Event( 'QA1 QD1 QE1 rA1 rD1 rE1 -> FA1 FA2 FA3 FA4 FA5 FA6' ),
				Event( 'QB1 QC1 QF1 rB1 rC1 rF1 -> FB1 FB2 FB3 FB4 FB5 FB6' ),
			]),
			System( 'Small Final 7-12', [
				Event( 'FA4 FA5 FA6 FB4 FB5 FB6 -> 7R 8R 9R 10R 11R 12R' ),
			]),
			System( 'Final Round 1-6', [
				Event( 'FA1 FA2 FA3 FB1 FB2 FB3 -> 1R 2R 3R 4R 5R 6R' ),
			]),
		])
	)
	competitions.append(
		Competition( 'Track: Keirin 43-49', [
			System( '1st Round', [
				Event( 'N1 N14 N15 N28 N29 N42 N43 -> QA1 QA2 QA3 QA4 QA5 QA6 QA7' ),
				Event( 'N2 N13 N16 N27 N30 N41 N44 -> QB1 QB2 QB3 QB4 QB5 QB6 QB7' ),
				Event( 'N3 N12 N17 N26 N31 N40 N45 -> QC1 QC2 QC3 QC4 QC5 QC6 QC7' ),
				Event( 'N4 N11 N18 N25 N32 N39 N46 -> QD1 QD2 QD3 QD4 QD5 QD6 QD7' ),
				Event( 'N5 N10 N19 N24 N33 N38 N47 -> QE1 QE2 QE3 QE4 QE5 QE6 QE7' ),
				Event( 'N6  N9 N20 N23 N34 N37 N48 -> QF1 QF2 QF3 QF4 QF5 QF6 QF7' ),
				Event( 'N7  N8 N21 N22 N35 N36 N49 -> QG1 QG2 QG3 QG4 QG5 QG6 QG7' ),
			]),
			System( 'Repechages 1', [
				Event( 'QA2 QG2 QF3 QE4 QD5 QC6 QB7 -> rA1 rA2  1EE  2EE  3EE  4EE  5EE' ),
				Event( 'QB2 QA3 QG3 QF4 QE5 QD6 QC7 -> rB1 rB2  6EE  7EE  8EE  9EE 10EE' ),
				Event( 'QC2 QB3 QA4 QG4 QF5 QE6 QD7 -> rC1 rC2 11EE 12EE 13EE 14EE 15EE' ),
				Event( 'QD2 QC3 QB4 QA5 QG5 QF6 QE7 -> rD1 rD2 16EE 17EE 18EE 19EE 20EE' ),
				Event( 'QE2 QD3 QC4 QB5 QA6 QG6 QF7 -> rE1 rE2 21EE 22EE 23EE 24EE 25EE' ),
				Event( 'QF2 QE3 QD4 QC5 QB6 QA7 QG7 -> rF1 rF2 26EE 27EE 28EE 29EE 30EE' ),
			]),
			System( '1/4 Finals', [
				Event( 'QA1 QF1 QG1 rC1 rB2 rC2     -> SA1 SA2 SA3 SA4 SA5 SA6' ),
				Event( 'QB1 QE1 rA1 rD1 rA2 rD2     -> SB1 SB2 SB3 SB4 SB5 SB6' ),
				Event( 'QC1 QD1 rB1 rE1 rF1 rE2 rF2 -> SC1 SC2 SC3 SC4 SC5 SC6 SC7' ),
			]),
			System( 'Repechages 2', [
				Event( 'SA3 SA4 SB4 SB5 SC5 SC6 SC7 -> sA1 sA2 sA3 31EE 32EE 33EE 34EE' ),
				Event( 'SB3 SC3 SC4 SA5 SA6 SB6     -> sB1 sB2 sB3 35EE 36EE 37EE' ),
			]),
			System( '1/2 Finals', [
				Event( 'SA1 SC1 SB2 sA1 sB2 sA3 -> FA1 FA2 FA3 FA4 FA5 FA6' ),
				Event( 'SB1 SA2 SC2 sB1 sA2 sB3 -> FB1 FB2 FB3 FB4 FB5 FB6' ),
			]),
			System( 'Small Final 7-12', [
				Event( 'FA4 FA5 FA6 FB4 FB5 FB6 -> 7R 8R 9R 10R 11R 12R' ),
			]),
			System( 'Final Round 1-6', [
				Event( 'FA1 FA2 FA3 FB1 FB2 FB3 -> 1R 2R 3R 4R 5R 6R' ),
			]),
		])
	)
	'''
	competitions.append(
		Competition( 'Track: Keirin 50-56', [
			System( '1st Round', [
				Event( 'N1 N16 N17 N32 N33 N48 N49 -> QA1 QA2 QA3 QA4 QA5 QA6 QA7' ),
				Event( 'N2 N15 N18 N31 N34 N47 N50 -> QB1 QB2 QB3 QB4 QB5 QB6 QB7' ),
				Event( 'N3 N14 N19 N30 N35 N46 N51 -> QC1 QC2 QC3 QC4 QC5 QC6 QC7' ),
				Event( 'N4 N13 N20 N29 N36 N45 N52 -> QD1 QD2 QD3 QD4 QD5 QD6 QD7' ),
				Event( 'N5 N12 N21 N28 N37 N44 N53 -> QE1 QE2 QE3 QE4 QE5 QE6 QE7' ),
				Event( 'N6 N11 N22 N27 N38 N43 N54 -> QF1 QF2 QF3 QF4 QF5 QF6 QF7' ),
				Event( 'N7 N10 N23 N26 N39 N42 N55 -> QG1 QG2 QG3 QG4 QG5 QG6 QG7' ),
				Event( 'N8  N9 N24 N25 N40 N41 N56 -> QH1 QH2 QH3 QH4 QH5 QH6 QH7' ),
			]),
			System( 'Repechages 1', [
				Event( 'QA2 QH2 QG3 QF4 QE5 QD6 QC7 -> rA1 rA2  1EE  2EE  3EE  4EE  5EE' ),
				Event( 'QB2 QA3 QH3 QG4 QF5 QE6 QD7 -> rB1 rB2  6EE  7EE  8EE  9EE 10EE' ),
				Event( 'QC2 QB3 QA4 QH4 QG5 QF6 QE7 -> rC1 rC2 11EE 12EE 13EE 14EE 15EE' ),
				Event( 'QD2 QC3 QB4 QA5 QH5 QG6 QF7 -> rD1 rD2 16EE 17EE 18EE 19EE 20EE' ),
				Event( 'QE2 QD3 QC4 QB5 QA6 QH6 QG7 -> rE1 rE2 21EE 22EE 23EE 24EE 25EE' ),
				Event( 'QF2 QE3 QD4 QC5 QB6 QA7 QH7 -> rF1 rF2 26EE 27EE 28EE 29EE 30EE' ),
				Event( 'QG2 QF3 QE4 QD5 QC6 QB7     -> rG1 rG2 31EE 32EE 33EE 34EE' ),
			]),
			System( '1/4 Finals', [
				Event( 'QA1 QH1 rA1 rB2 rC2     -> SA1 SA2 SA3 SA4 SA5 SA6' ),
				Event( 'QB1 QG1 rB1 rA2 rD2     -> SB1 SB2 SB3 SB4 SB5 SB6' ),
				Event( 'QC1 QF1 rC1 rG1 rE2     -> SC1 SC2 SC3 SC4 SC5 SC6' ),
				Event( 'QD1 QE1 rD1 rF1 rF2 rG2 -> SD1 SD2 SD3 SD4 SD5 SD6 SD7' ),
			]),
			System( 'Repechages 2', [
				Event( 'SA3 SD3 SA5 SB5 SC6 SD6 -> sA1 sA2 35EE 36EE 37EE 38EE 39EE' ),
				Event( 'SB3 SA4 SD4 SC5 SB6 SD7 -> sB1 sB2 40EE 41EE 42EE 43EE 44EE' ),
				Event( 'SC3 SB4 SC4 SD5 SA6     -> sC1 sC2 45EE 46EE 47EE 48EE' ),
			]),
			System( '1/2 Finals', [
				Event( 'SA1 SD1 SB2 SC2 sA1 sC1 sB2 -> FA1 FA2 FA3 FA4 FA5 FA6' ),
				Event( 'SB1 SC1 SA2 SD2 sB1 sA2 sC2 -> FB1 FB2 FB3 FB4 FB5 FB6' ),
			]),
			System( 'Small Final 7-12', [
				Event( 'FA4 FA5 FA6 FB4 FB5 FB6 -> 7R 8R 9R 10R 11R 12R' ),
			]),
			System( 'Final Round 1-6', [
				Event( 'FA1 FA2 FA3 FB1 FB2 FB3 -> 1R 2R 3R 4R 5R 6R' ),
			]),
		])
	)
	'''

	#-----------------------------------------------------------------------------------------
	competitions.append(
		Competition( 'MTB: XCE 36', [
			System( 'Round 1', [
				Event( 'N1 N12 N13 N24 N25 N36 -> 1A 2A' ),
				Event( 'N6  N7 N18 N19 N30 N31 -> 3A 4A' ),
				Event( 'N3 N10 N15 N22 N27 N34 -> 5A 6A' ),
				Event( 'N4  N9 N16 N21 N28 N33 -> 1B 2B' ),
				Event( 'N2 N11 N14 N23 N26 N35 -> 3B 4B' ),
				Event( 'N5  N8 N17 N20 N29 N32 -> 5B 6B' ),
			]),
			System( '1/2 Finals', [
				Event( '1A 2A 3A 4A 5A 6A -> 1C 2C 3C 4C 5C 6C' ),
				Event( '1B 2B 3B 4B 5B 6B -> 1D 2D 3D 4D 5D 6D' ),
			]),
			System( 'Finals', [
				Event( '4C 5C 6C 4D 5D 6D -> 7R 8R 9R 10R 11R 12R' ),
				Event( '1C 2C 3C 1D 2D 3D -> 1R 2R 3R 4R 5R 6R' ),
			]),
		])
	)
	
	#-----------------------------------------------------------------------------------------
	competitions.append(
		Competition( 'MTB: XCE 12', [
			System( '1/2 Finals', [
				Event( 'N1 N3 N6 N7 N10 N12 -> 1C 2C 3C 4C 5C 6C' ),
				Event( 'N2 N4 N5 N8 N9  N11 -> 1D 2D 3D 4D 5D 6D' ),
			]),
			System( 'Finals', [
				Event( '4C 5C 6C 4D 5D 6D -> 7R 8R 9R 10R 11R 12R' ),
				Event( '1C 2C 3C 1D 2D 3D -> 1R 2R 3R 4R 5R 6R' ),
			]),
		])
	)
	
	#-----------------------------------------------------------------------------------------
	competitions.append(
		Competition( 'MTB: XCE 32', [
			System( '1/8 Finals', [
				Event( 'N1 N16 N17 N32 -> 1A1 1A2' ),
				Event( 'N8  N9 N24 N25 -> 2A3 2A4' ),
				Event( 'N5 N12 N21 N28 -> 3B1 3B2' ),
				Event( 'N4 N13 N20 N29 -> 4B3 4B4' ),
				Event( 'N2 N15 N18 N31 -> 5C1 5C2' ),
				Event( 'N7 N10 N23 N26 -> 6C3 6C4' ),
				Event( 'N3 N14 N19 N30 -> 7D1 7D2' ),
				Event( 'N6 N11 N22 N27 -> 8D3 8D4' ),
			]),
			System( '1/4 Finals', [
				Event( '1A1 1A2 2A3 2A4 -> 1E1 1E2' ),
				Event( '3B1 3B2 4B3 4B4 -> 2E3 2E4' ),
				Event( '5C1 5C2 6C3 6C4 -> 3F1 3F2' ),
				Event( '7D1 7D2 8D3 8D4 -> 3F3 3F4' ),
			]),
			System( '1/2 Finals', [
				Event( '1E1 1E2 2E3 2E4 -> 1G1 1G2 1G3 1G4' ),
				Event( '3F1 3F2 3F3 3F4 -> 2H1 2H2 2H3 2H4' ),
			]),
			System( 'Finals', [
				Event( '1G3 1G4 2H3 2H4 -> 5R 6R 7R 8R' ),
				Event( '1G1 1G2 2H1 2H2 -> 1R 2R 3R 4R' ),
			]),
		])
	)

	#-----------------------------------------------------------------------------------------
	competitions.append(
		Competition( 'MTB: XCE 16', [
			System( '1/4 Finals', [
				Event( 'N1 N8  N9 N16 -> 1E1 1E2' ),
				Event( 'N4 N5 N12 N13 -> 2E3 2E4' ),
				Event( 'N2 N7 N10 N15 -> 3F1 3F2' ),
				Event( 'N3 N6 N11 N14 -> 4F3 4F4' ),
			]),
			System( '1/2 Finals', [
				Event( '1E1 1E2 2E3 2E4 -> 1G1 1G2 1G3 1G4' ),
				Event( '3F1 3F2 4F3 4F4 -> 2H1 2H2 2H3 2H4' ),
			]),
			System( 'Finals', [
				Event( '1G3 1G4 2H3 2H4 -> 5R 6R 7R 8R' ),
				Event( '1G1 1G2 2H1 2H2 -> 1R 2R 3R 4R' ),
			]),
		])
	)
	
	competitions.append(
		Competition( 'MTB: XCE 8', [
			System( '1/2 Finals', [
				Event( 'N1 N4 N5 N8 -> 1G1 1G2 1G3 1G4' ),
				Event( 'N2 N3 N6 N7 -> 2H1 2H2 2H3 2H4' ),
			]),
			System( 'Finals', [
				Event( '1G3 1G4 2H3 2H4 -> 5R 6R 7R 8R' ),
				Event( '1G1 1G2 2H1 2H2 -> 1R 2R 3R 4R' ),
			]),
		])
	)
	
	competitions.append(
		Competition( 'MTB: XCE 6', [
			System( 'Finals', [
				Event( 'N1 N2 N3 N4 N5 N6 -> 1R 2R 3R 4R 5R 6R' ),
			]),
		])
	)
	
	competitions.append(
		Competition( 'MTB: XCE 4', [
			System( 'Finals', [
				Event( 'N1 N2 N3 N4 -> 1R 2R 3R 4R' ),
			]),
		])
	)
	
	#-----------------------------------------------------------------------------------------
	competitions.append(
		Competition( 'MTB: Four Cross 64', [
			System( 'Round 1', [
				Event( 'N64  N1 N33 N32 -> 32A  1A' ),
				Event( 'N17 N49 N16 N48 -> 17A 16A' ),
				Event( 'N40 N25 N57  N8 -> 25A  8A' ),
				Event( 'N41 N24 N56  N9 -> 24A  9A' ),
				Event( 'N29  N4 N36 N61 -> 29A  4A' ),
				Event( 'N45 N20 N13 N52 -> 20A 13A' ),
				Event( 'N28 N37  N5 N60 -> 28A  5A' ),
				Event( 'N44 N21 N12 N53 -> 21A 12A' ),
				Event( 'N34 N31 N63  N2 -> 31A  2A' ),
				Event( 'N47 N18 N50 N15 -> 18A 15A' ),
				Event( 'N39 N26  N7 N58 -> 26A  7A' ),
				Event( 'N10 N55 N23 N42 -> 23A 10A' ),
				Event( 'N30 N35 N62  N3 -> 30A  3A' ),
				Event( 'N19 N46 N51 N14 -> 19A 14A' ),
				Event( 'N38 N27  N6 N59 -> 27A  6A' ),
				Event( 'N43 N22 N11 N54 -> 22A 11A' ),
			]),
			System( 'Round 2', [
				Event( '32A 1A 17A 16A -> 1B 16B' ),
				Event( '25A 8A 24A  9A -> 8B  9B' ),
				Event( '29A 4A 20A 13A -> 4B 13B' ),
				Event( '28A 5A 21A 12A -> 5B 12B' ),
				Event( '31A 2A 18A 15A -> 2B 15B' ),
				Event( '26A 7A 23A 10A -> 7B 10B' ),
				Event( '30A 3A 19A 14A -> 3B 14B' ),
				Event( '27A 6A 22A 11A -> 6B 11B' ),
			]),
			System( 'Round 3', [
				Event( '1B 16B 8B  9B -> 1C 8C' ),
				Event( '4B 13B 5B 12B -> 4C 5C' ),
				Event( '2B 15B 7B 10B -> 2C 7C' ),
				Event( '3B 14B 6B 11B -> 3C 6C' ),
			]),
			System( 'Round 4', [
				Event( '1C 5C 4C 8C -> 1D 3D 5D 7D' ),
				Event( '2C 7C 3C 6C -> 2D 4D 6D 8D' ),
			]),
			System( 'Finals', [
				Event( '5D 6D 7D 8D -> 5R 6R 7R 8R' ),
				Event( '1D 2D 3D 4D -> 1R 2R 3R 4R' ),
			]),
		]),
	)
	
	# Derive Four Cross for 32 and 16 starters from 64 starters.
	for i in range(2):
		fcX = copy.deepcopy( competitions[-1] )
		fcX.systems.pop( 0 )
		fcX.starters //= 2
		fcX.name = 'MTB: Four Cross {}'.format(fcX.starters)
		for event in fcX.systems[0].events:
			event.composition = ['N{}'.format(c[:-1]) for c in event.composition]
		for system in fcX.systems:
			if system.name.startswith( 'Round' ):
				system.name = 'Round {}'.format(int(system.name.split()[1]) - 1)
		competitions.append( fcX )
	
	#-----------------------------------------------------------------------------------------
	
	competitions.append(
		Competition( 'Road: 16 3-Sprint Challenge', [
			System( '1/4 Finals', [
				Event( 'N1 N8  N9 N16 -> 1E1 1E2 1P1 1P2' ),
				Event( 'N4 N5 N12 N13 -> 2E3 2E4 2P3 2P4' ),
				Event( 'N2 N7 N10 N15 -> 3F1 3F2 3Q1 3Q2' ),
				Event( 'N3 N6 N11 N14 -> 4F3 4F4 4Q3 4Q4' ),
			]),
			System( '1/2 Finals', [
				Event( '1P1 1P2 2P3 2P4 -> 1S1 1S2 1S3 1S4' ),
				Event( '3Q1 3Q2 4Q3 4Q4 -> 2T1 2T2 2T3 2T4' ),
				Event( '1E1 1E2 2E3 2E4 -> 1G1 1G2 1G3 1G4' ),
				Event( '3F1 3F2 4F3 4F4 -> 2H1 2H2 2H3 2H4' ),
			]),
			System( 'Finals', [
				Event( '1S3 1S4 2T3 2T4 -> 13R 14R 15R 16R' ),
				Event( '1S1 1S2 2T1 2T2 -> 9R 10R 11R 12R' ),
				Event( '1G3 1G4 2H3 2H4 -> 5R 6R 7R 8R' ),
				Event( '1G1 1G2 2H1 2H2 -> 1R 2R 3R 4R' ),
			]),
		])
	)
	
	#-----------------------------------------------------------------------------------------
	'''
	def genN( iStart, iEnd, stride=1 ):
		return ' '.join( 'N{}'.format(i) for i in range(iStart, iEnd+1, stride) )
	
	def gen( suffix, iStart, iEnd, stride=1 ):
		return ' '.join( '{}{}'.format(i, suffix) for i in range(iStart, iEnd+1, stride) )
	
	competitions.append(
		Competition( 'Track: Track Endurance Eliminator', [
			System( 'Round 1', [
				Event( genN(1,96,4) + ' -> ' + gen('B',1,15) + ' ' +  gen('RepA',1,9) ),
				Event( genN(2,96,4) + ' -> ' + gen('B',16,30) + ' ' +  gen('RepA',10,18) ),
				Event( genN(3,96,4) + ' -> ' + gen('B',31,45) + ' ' +  gen('RepA',19,27) ),
				Event( genN(4,96,4) + ' -> ' + gen('B',46,60) + ' ' +  gen('RepA',28,36) ),
			]),
			System( 'Repechage A', [
				Event( gen('RepA', 1, 9) + ' ' +  gen('RepA',19,27) + ' -> ' + gen('B',61,66) ),
				Event( gen('RepA',10,18) + ' ' +  gen('RepA',28,36) + ' -> ' + gen('B',67,72) ),
			]),
			System( 'Round 2', [
				Event( gen('B',1,72,3) + ' -> ' + gen('C', 1, 8) + ' ' +  gen('RepB', 1,16) ),
				Event( gen('B',2,72,3) + ' -> ' + gen('C', 9,16) + ' ' +  gen('RepB',17,32) ),
				Event( gen('B',3,72,3) + ' -> ' + gen('C',17,24) + ' ' +  gen('RepB',33,48) ),
			]),
			System( 'Repechage B', [
				Event( gen('RepB', 1,16,2) + ' ' + gen('RepB',17,32,2) +                              ' -> ' + gen('C',25,30) ),
				Event( gen('RepB', 2, 8,2) + ' ' + gen('RepB',18,24,2) + ' ' +  gen('RepB',33,48,2) + ' -> ' + gen('C',31,36) ),
				Event( gen('RepB',10,16,2) + ' ' + gen('RepB',26,32,2) + ' ' +  gen('RepB',34,48,2) + ' -> ' + gen('C',37,42) ),
			]),
			System( 'Semi Finals', [
				Event( gen('C',1,42,2) + ' -> ' + gen('D', 1,10) + ' ' + gen('RepC', 1,11) ),
				Event( gen('C',2,42,2) + ' -> ' + gen('D',11,20) + ' ' + gen('RepC',12,22) ),
			]),
			System( 'Repechage C', [
				Event( gen('RepC',1,22) + ' -> ' + gen('D',21,24) ),
			]),
			System( 'Finals', [
				Event( gen('D',1,24) + ' -> ' + gen('R',1,24) ),
			]),
		]),
	)
	'''
	
	for i, c in enumerate(competitions):
		c.i = i
	return competitions

def SetDefaultData( name = None, modifier = 0, random = False ):
	if name is None:
		name = 0
		
	model = Model.Model()

	if isinstance(name, int):
		model.competition = getCompetitions()[name]
	else:
		for i, competition in enumerate(getCompetitions()):
			if i == 0:
				model.competition = competition
				
			if name in competition.name:
				model.competition = competition
				break

	# Call setCompetition so that we set the correct heat numbers.
	model.setCompetition( model.competition, modifier )
	testData = getRandomTestData( competition.starters ) if random else getTestData()
	for attrs in testData:
		rider = Model.Rider( **attrs )
		model.riders.append( rider )
		
	model.setQualifyingInfo()
	return model
	
def DoRandomSimulation( model = None ):
	model = model or Model.model
	competition = model.competition
	state = competition.state
	while True:
		se = competition.getCanStart()
		if not se:
			break
		e = se[0][1]
		start = e.getStart()
		places = [c for c in e.composition if competition.state.inContention(c)]
		v = (sum(state.labels[p].qualifying_time for p in places) / float(len(places))) / 20.0
		places.sort( key = lambda p: random.gauss(state.labels[p].qualifying_time, v) )
		start.setPlaces( [(state.labels[p].bib, '', '0', '0') for p in places] )
		e.propagate()
		competition.propagate()

if __name__ == '__main__':
	for c in getCompetitions():
		print( c )
