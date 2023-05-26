import wx
import wx.grid as gridlib
import sys
import Utils
import Model
from ReorderableGrid import ReorderableGrid

sameGap = '-'
sameTime = 's.t'

lastKey = None
def StageRaceGCToGrid( notebook ):
	notebook.DeleteAllPages()
	
	model = Model.model
	
	#---------------------------------------------------------------------------------------
	model.comments = {}
	model.lastKey = None
	def setComment( row, col, comment, style=None ):
		model.comments[(notebook.GetPageCount(), row, col)] = comment
	
	def getRiderInfo( bib ):
		rider = model.registration.bibToRider[bib]
		return '{}: {}'.format(bib, rider.results_name)
		
	def formatContext( context ):
		lines = []
		for c in context:
			if len(c) == 3:
				t, p, bib = c
				lines.append( '{}  {} ({})'.format(getRiderInfo(bib), Utils.formatTime(t), Utils.ordinal(p)) )
			elif len(c) == 2:
				p, bib = c
				lines.append( '{} ({})'.format(getRiderInfo(bib), Utils.ordinal(p)) )
			elif len(c) == 1:
				bib = c[0]
				lines.append( getRiderInfo(bib) )
			else:
				assert False
		return '\n'.join( lines )

	def formatContextList( context ):
		lines = [formatContext(c).replace('\n', ' - ') for c in context]
		return '\n'.join( lines )
	
	def getCommentCallback( grid ):
		page = notebook.GetPageCount()
		def callback( event ):
			model = Model.model
			x, y = grid.CalcUnscrolledPosition(event.GetX(),event.GetY())
			coords = grid.XYToCell(x,y).Get()
			key = (page, coords[0], coords[1])
			if key != model.lastKey:
				try:
					event.GetEventObject().SetToolTip(model.comments[key])
				except:
					event.GetEventObject().SetToolTip(u'')
				model.lastKey = key
			event.Skip()
		return callback
	
	#---------------------------------------------------------------------------------------
	def writeIC( stage ):
		ic_fields = ['gap'] + list(Model.IndividualClassification._fields[1:-1])
		riderFields = set( model.registration.getFieldsInUse() )
		headers = (
			['place', 'bib', 'last_name', 'first_name', 'team'] +
			(['uci_id'] if 'uci_id' in riderFields else []) +
			(['license'] if 'license' in riderFields else []) +
			list(ic_fields)
		)
		if headers[-1] == 'bib':
			headers = headers[:-1]
		
		grid = ReorderableGrid( notebook )
		stage.individual_gc = getattr(stage, 'individual_gc', [])
		grid.CreateGrid( len(stage.individual_gc), len(headers) )
		grid.EnableReorderRows( False )
		
		for col, h in enumerate(headers):
			attr = gridlib.GridCellAttr()
			attr.SetReadOnly()
			if h in Model.Result.NumericFields or any(t in h for t in ('place', 'time')):
				attr.SetAlignment( wx.ALIGN_RIGHT, wx.ALIGN_CENTRE )
			grid.SetColAttr( col, attr )
			grid.SetColLabelValue( col, Utils.fieldToHeader(h, True) )

		rowNum = 0
		gapLast = None
		timeLast = None
		for place, r in enumerate(stage.individual_gc, 1):
			try:
				rider = model.registration.bibToRider[r.bib]
			except KeyError:
				continue
		
			col = 0
			if r.retired_stage > 0:
				grid.SetCellValue( rowNum, col, 'AB' ); col += 1
			else:
				grid.SetCellValue( rowNum, col, str(place) ); col += 1
			
			grid.SetCellValue( rowNum, col, str(r.bib) ); col += 1
			grid.SetCellValue( rowNum, col, str(rider.last_name).upper()); col += 1
			grid.SetCellValue( rowNum, col, str(rider.first_name) ); col += 1
			grid.SetCellValue( rowNum, col, str(rider.team) ); col += 1
			
			if 'uci_id' in riderFields:
				grid.SetCellValue( rowNum, col, str(rider.uci_id) ); col += 1
			if 'license' in riderFields:
				grid.SetCellValue( rowNum, col, str(rider.license) ); col += 1
			
			if r.retired_stage == 0:
				grid.SetCellValue( rowNum, col, Utils.formatTime(r.gap, twoDigitHours=True) if gapLast != r.gap else sameGap )
				gapLast = r.gap
				col += 1
				
				timeCur = r.total_time_with_bonus_plus_penalty
				grid.SetCellValue( rowNum, col, Utils.formatTime(timeCur, twoDigitHours=True) if timeCur != timeLast else sameTime )
				timeLast = timeCur
				col += 1
				
				grid.SetCellValue( rowNum, col, Utils.formatTime(r.total_time_with_bonus_plus_penalty_plus_second_fraction, twoDigitHours=True, extraPrecision=True) ); col += 1
				grid.SetCellValue( rowNum, col, str(r.sum_of_places) ); col += 1
				grid.SetCellValue( rowNum, col, str(r.last_stage_place) ); col += 1
			
			rowNum +=1
			
		grid.GetGridWindow().Bind(wx.EVT_MOTION, getCommentCallback(grid))
		grid.AutoSize()
		return grid
	
	#---------------------------------------------------------------------------------------
	def writeTeamClass( stage ):
		
		headers = ['Place', 'Team', 'Gap', 'Combined\nTimes', 'Combined\nPlaces', 'Best\nRider GC']
		
		grid = ReorderableGrid( notebook )
		grid.CreateGrid( len(stage.team_classification), len(headers) )
		grid.EnableReorderRows( False )
		
		for col, h in enumerate(headers):
			attr = gridlib.GridCellAttr()
			attr.SetReadOnly()
			if h != 'Team':
				attr.SetAlignment( wx.ALIGN_RIGHT, wx.ALIGN_CENTRE )
			grid.SetColAttr( col, attr )
			grid.SetColLabelValue( col, h )
		
		rowNum = 0
		gapLast = None
		timeLast = None
		for place, tc in enumerate(stage.team_classification, 1):
			col = 0
			grid.SetCellValue( rowNum, col, str(place) ); col += 1
			grid.SetCellValue( rowNum, col, tc.team ); col += 1
			
			grid.SetCellValue( rowNum, col, Utils.formatTime(tc.gap, twoDigitHours=True) if tc.gap != gapLast else sameGap )
			gapLast = tc.gap
			col += 1
			
			timeCur = tc.sum_best_top_times.value
			grid.SetCellValue( rowNum, col, Utils.formatTime(timeCur, forceHours=True) if timeCur != timeLast else sameTime )
			timeLast = timeCur
			setComment( rowNum, col, formatContext(tc.sum_best_top_times.context), {'width':256} )
			col += 1
			
			grid.SetCellValue( rowNum, col, str(tc.sum_best_top_places.value) )
			setComment( rowNum, col, formatContext(tc.sum_best_top_places.context), {'width':256} )
			col += 1
			
			grid.SetCellValue( rowNum, col, str(tc.best_place.value) )
			setComment( rowNum, col, formatContext(tc.best_place.context), {'width':256} )
			col += 1
			rowNum +=1
			
		grid.GetGridWindow().Bind(wx.EVT_MOTION, getCommentCallback(grid))
		grid.AutoSize()
		return grid

	#---------------------------------------------------------------------------------------
	def writeTeamGC():
		headers = (
			['Place', 'Team', 'Gap', 'Combined\nTime'] +
			['{}s'.format(Utils.ordinal(i+1)) for i in range(len(model.all_teams))] +
			['Best\nRider GC']
		)
		
		grid = ReorderableGrid( notebook )
		grid.CreateGrid( len(model.team_gc) + len(model.unranked_teams), len(headers) )
		grid.EnableReorderRows( False )
		
		for col, h in enumerate(headers):
			attr = gridlib.GridCellAttr()
			attr.SetReadOnly()
			if h != 'Team':
				attr.SetAlignment( wx.ALIGN_RIGHT, wx.ALIGN_CENTRE )
			grid.SetColAttr( col, attr )
			grid.SetColLabelValue( col, h )
		
		rowNum = 0
		leaderTime = None
		gapLast = None
		timeLast = None
		for place, tgc in enumerate(model.team_gc, 1):
			col = 0
			grid.SetCellValue( rowNum, col, str(place) ); col += 1
			grid.SetCellValue( rowNum, col, str(tgc[-1]) ); col += 1
			
			combinedTime = tgc[0].value
			if leaderTime is None:
				leaderTime = combinedTime
			gap = combinedTime - leaderTime
			grid.SetCellValue( rowNum, col, Utils.formatTime(gap, twoDigitHours=True) if gap != gapLast else sameGap ); col += 1
			gapLast = gap
			
			grid.SetCellValue( rowNum, col, Utils.formatTime(combinedTime, forceHours=True) if combinedTime != timeLast else sameTime)
			timeLast = combinedTime
			setComment( rowNum, col, formatContextList(tgc[0].context), {'width':512} )
			col += 1
			
			for i in range(1, len(tgc)-2):
				if tgc[i].value:
					grid.SetCellValue( rowNum, col, str(tgc[i].value) )
					setComment( rowNum, col, u'\n'.join(tgc[i].context), {'width':128} )
				col += 1
			
			grid.SetCellValue( rowNum, col, str(tgc[-2].value) )
			setComment( rowNum, col, formatContext(tgc[-2].context), {'width':256} )
			col += 1
			
			rowNum +=1
		
		for team in model.unranked_teams:
			col = 0
			grid.SetCellValue( rowNum, col, 'DNF' ); col += 1
			grid.SetCellValue( rowNum, col, team ); col += 1
			rowNum +=1
	
		grid.GetGridWindow().Bind(wx.EVT_MOTION, getCommentCallback(grid))
		grid.AutoSize()
		return grid
	
	#---------------------------------------------------------------------------------------
	def writeSprintGC():
		if not model.sprint_gc:
			return
		
		riderFields = set( model.registration.getFieldsInUse() )
		headers = (
			['place', 'bib', 'last_name', 'first_name', 'team'] +
			(['uci_id'] if 'uci_id' in riderFields else []) +
			(['license'] if 'license' in riderFields else []) +
			['points', 'stage_wins', 'sprint_wins', 'GC']
		)
		
		grid = ReorderableGrid( notebook )
		grid.CreateGrid( len(model.sprint_gc), len(headers) )
		grid.EnableReorderRows( False )
		
		for col, h in enumerate(headers):
			attr = gridlib.GridCellAttr()
			attr.SetReadOnly()
			if h in Model.Result.NumericFields or h in {'place', 'points', 'stage_wins', 'sprint_wins', 'GC'}:
				attr.SetAlignment( wx.ALIGN_RIGHT, wx.ALIGN_CENTRE )
			grid.SetColAttr( col, attr )
			grid.SetColLabelValue( col, Utils.fieldToHeader(h, True) )
		
		rowNum = 0
		for place, r in enumerate(model.sprint_gc, 1):
			try:
				rider = model.registration.bibToRider[r[-1]]
			except KeyError:
				continue
		
			col = 0
			grid.SetCellValue( rowNum, col, str(place) ); col += 1			
			grid.SetCellValue( rowNum, col, str(rider.bib) ); col += 1
			grid.SetCellValue( rowNum, col, str(rider.last_name).upper()); col += 1
			grid.SetCellValue( rowNum, col, str(rider.first_name) ); col += 1
			grid.SetCellValue( rowNum, col, str(rider.team) ); col += 1
			
			if 'uci_id' in riderFields:
				grid.SetCellValue( rowNum, col, str(rider.uci_id) ); col += 1
			if 'license' in riderFields:
				grid.SetCellValue( rowNum, col, str(rider.license) ); col += 1

			for v in r[:-1]:
				grid.SetCellValue( rowNum, col, str(v) if v else '' ); col += 1
				
			rowNum +=1
			
		grid.AutoSize()
		return grid
		
	#---------------------------------------------------------------------------------------
	def writeKOMGC():
		if not model.kom_gc:
			return
		
		riderFields = set( model.registration.getFieldsInUse() )
		headers = (
			['place', 'bib', 'last_name', 'first_name', 'team'] +
			(['uci_id'] if 'uci_id' in riderFields else []) +
			(['license'] if 'license' in riderFields else []) +
			['KOM Total', 'HC Wins', 'C1 Wins', 'C2 Wins', 'C3 Wins', 'C4 Wins', 'GC']
		)
		
		grid = ReorderableGrid( notebook )
		grid.CreateGrid( len(model.kom_gc), len(headers) )
		grid.EnableReorderRows( False )
		
		for col, h in enumerate(headers):
			attr = gridlib.GridCellAttr()
			attr.SetReadOnly()
			if h in Model.Result.NumericFields or h in {'KOM Total', 'HC Wins', 'C1 Wins', 'C2 Wins', 'C3 Wins', 'C4 Wins', 'GC'}:
				attr.SetAlignment( wx.ALIGN_RIGHT, wx.ALIGN_CENTRE )
			grid.SetColAttr( col, attr )
			grid.SetColLabelValue( col, Utils.fieldToHeader(h, True) )
		
		rowNum = 0
		for place, r in enumerate(model.kom_gc, 1):
			try:
				rider = model.registration.bibToRider[r[-1]]
			except KeyError:
				continue
		
			col = 0
			grid.SetCellValue( rowNum, col, str(place) ); col += 1			
			grid.SetCellValue( rowNum, col, str(rider.bib) ); col += 1
			grid.SetCellValue( rowNum, col, str(rider.last_name).upper()); col += 1
			grid.SetCellValue( rowNum, col, str(rider.first_name) ); col += 1
			grid.SetCellValue( rowNum, col, str(rider.team) ); col += 1
			
			if 'uci_id' in riderFields:
				grid.SetCellValue( rowNum, col, str(rider.uci_id) ); col += 1
			if 'license' in riderFields:
				grid.SetCellValue( rowNum, col, str(rider.license) ); col += 1

			for v in r[:-1]:
				grid.SetCellValue( rowNum, col, str(v) if v else '' ); col += 1
				
			rowNum +=1
			
		grid.AutoSize()
		return grid
		
	#------------------------------------------------------------------------------------
	
	if model.stages:
		notebook.AddPage( writeIC(model.stages[-1]), 'IndividualGC' )
		if model.sprint_gc:
			notebook.AddPage( writeSprintGC(), 'SprintGC' )
		if model.kom_gc:
			notebook.AddPage( writeKOMGC(), 'KOMGC' )
		notebook.AddPage( writeTeamGC(), 'TeamGC' )
		for stage in reversed(model.stages):
			notebook.AddPage( writeIC(stage), stage.sheet_name + '-GC' )
			notebook.AddPage( writeTeamClass(stage), stage.sheet_name + '-TeamClass' )
