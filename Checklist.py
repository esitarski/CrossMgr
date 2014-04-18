
import wx
import wx.gizmos
import io
import os
import rsonlite
import Model
import Utils

_raceStatusNames = [u'NotStarted'.lower(), u'Finished'.lower(), u'Running'.lower()]
def _checkRaceStatus( race, val ):
	val = val.lower()
	if val not in _raceStatusNames:
		raise ValueError( u'Unknown option: "RaceStatus = {}"'.format(val) )
	return (val == _raceStatusNames[0 if race.isUnstarted() else 1 if race.isFinished() else 2])

def _toBool( s ):
	if s[:1] not in 'TtYy1FfNn0':
		raise ValueError( u'Unknown boolean value "{}"'.format(s) )
	return s[:1] in 'TtYy1'

_processRequirementLookup = {
	u'RaceStatus'.lower():	_checkRaceStatus,
	u'TimeTrial'.lower(): 	lambda race, v: getattr(race, 'isTimeTrial', False) == _toBool(v),
	u'ChipReader'.lower(): 	lambda race, v: getattr(race, 'enableJChipIntegration', False) == _toBool(v),
	u'Camera'.lower(): 		lambda race, v: getattr(race, 'enableUSBCamera', False) ==_toBool(v),
}

class Task( object ):
	NotDone = 0
	Partial = 1
	Done = 2

	def __init__( self ):
		self.title = u''
		self.note = u''
		self.status = self.NotDone
		self.expand = True
		self.requires = []
		self.subtasks = []

	def meetsRequirements( self ):
		race = Model.race
		if not race:
			return False
		
		success = True
		for req, val in self.requires:
			try:
				if not _processRequirementLookup[req.lower()]( race, val ):
					success = False
			except KeyError:
				raise ValueError( u'Unknown Requirement "{}"'.format(req) )
		
		return success
		
	def setStatus( self, s = Done ):
		self.status = s
		if s != self.Partial:
			for i in self.subtasks:
				i.setStatus( s )
		
	def appendRequires( self, req, val ):
		self.requires.append( (req, val) )
		
	def appendSubtask( self, task ):
		self.subtasks.append( task )
		
	def validate( self ):
		self.meetsRequirements()
		for t in self.subtasks:
			t.meetsRequirements()
		return True
		
	def pprint( self, indent = u'  ', indent_level = 0 ):
		print '{}task'.format( indent*indent_level )
		print '{}title = {}'.format( indent*(indent_level+1), self.title )
		if self.note:
			print '{}note = {}'.format( indent*(indent_level+1), self.note )
		print '{}status = {}'.format( indent*(indent_level+1), ['NotDone', 'Partial', 'Done'][self.status] )
		if self.requires:
			print '{}requires'.format( indent*(indent_level+1) )
		for req, val in self.requires:
			print '{}{} = {}'.format( indent*(indent_level+2), req, val )
		if self.subtasks:
			print '{}subtasks'.format( indent*(indent_level+1) )
			for task in self.subtasks:
				task.pprint( indent, indent_level + 2 )

def _setTitle( task, val ):
	task.title = unicode(val[0])

def _setNote( task, val ):
	task.note = unicode(val[0])

def _setRequires( task, requires ):
	for r in requires:
		task.appendRequires( unicode(r[0]), unicode(r[1][0]))

def _setSubtasks( task, subtasks ):
	for s in subtasks:
		task.appendSubtask( _createTask(s) )
		
_processTokenLookup = dict(
	title		= _setTitle,
	note		= _setNote,
	requires 	= _setRequires,
	subtasks 	= _setSubtasks
)

def _createTask( task_data ):
	assert task_data[0] == 'task', 'Missing "task" keyword.  Line: "{}"'.format( task_data )
	task = Task()
	for key, val in task_data[1]:
		_processTokenLookup[key.lower()](task, val)
	return task

def createTasks( fname, fp ):
	try:
		tasks = rsonlite.loads( fp.read() )
	except Exception as e:
		Utils.writeLog( 'CheckList: Error: {} in "{}"'.format(e, fname) )
		tasks = rsonlite.loads( '''
task
    title = File Read Error
    note = {} in file "{}"\n'''.format(e, fname) )

	try:
		root = Task()
		root.title = 'root'
		_setSubtasks( root, tasks )
	except Exception as e:
		tasks = rsonlite.loads( '''
task
    title = File Content Error
    note = {} in file "{}"\n'''.format(e, fname) )
		root = Task()
		root.title = 'root'
		_setSubtasks( root, tasks )
	
	return root
	
class Checklist( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY, style = 0 ):
		wx.Panel.__init__(self, parent, id, style = style)
		
		self.Bind( wx.EVT_SIZE, self.onSize )
		
		isz = (16,16)
		il = wx.ImageList( *isz )
		self.checkedImage = il.Add(wx.Bitmap(os.path.join(Utils.getImageFolder(), 'ok-icon.png'), wx.BITMAP_TYPE_PNG))
		self.checkmarkImage = il.Add(wx.Bitmap(os.path.join(Utils.getImageFolder(), 'checkmark-icon.png'), wx.BITMAP_TYPE_PNG))
		self.uncheckedImage = il.Add(wx.Bitmap(os.path.join(Utils.getImageFolder(), 'checkbox_no.png'), wx.BITMAP_TYPE_PNG))
		self.partialCheckedImage = il.Add(wx.Bitmap(os.path.join(Utils.getImageFolder(), 'checkbox_partial.png'), wx.BITMAP_TYPE_PNG))
		self.xImage = il.Add(wx.Bitmap(os.path.join(Utils.getImageFolder(), 'x-icon.png'), wx.BITMAP_TYPE_PNG))
		
		self.SetBackgroundColour( wx.Colour(255,255,255) )
		self.tree = wx.gizmos.TreeListCtrl( self,
							style = wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS |
									wx.TR_NO_LINES | wx.TR_ROW_LINES )
		self.tree.SetImageList( il )
		self.tree.SetFont( wx.FontFromPixelSize( wx.Size(0,16), wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_NORMAL ) )
		self.imageList = il
		
		self.tree.AddColumn( _('Task (right click to change)') )
		self.tree.AddColumn( _('Note') )
		self.tree.SetMainColumn( 0 )
		self.tree.SetColumnWidth( 0, 450 )
		self.tree.SetColumnWidth( 1, 450 )
		
		self.tree.Bind( wx.EVT_TREE_ITEM_COLLAPSED, self.onTreeItemCollapsed )
		self.tree.Bind( wx.EVT_TREE_ITEM_EXPANDED, self.onTreeItemExpanded )
		self.tree.Bind( wx.EVT_TREE_ITEM_ACTIVATED, self.onTreeItemActivated )
		self.tree.Bind( wx.EVT_TREE_ITEM_RIGHT_CLICK, self.onTreeItemActivated )
		
		self.checklist = None
		self.refresh()

	def updateChecklist( self ):
		race = Model.race
		
		self.checklist = getattr( Model.race, 'checklist', None ) if race else None
		if self.checklist is None:
			searchDirs = []
			if Utils.getFileName():
				searchDirs.append( os.path.dirname(Utils.getFileName()) )
			searchDirs.extend( [os.path.expanduser('~'), Utils.getImageFolder(), os.path.dirname(__file__)] )
			
			for dir in searchDirs:
				fname = os.path.join(dir, 'CrossMgrChecklist.txt')
				try:
					fp = io.open(fname, 'r', encoding='utf-8')
				except Exception as e:
					continue
					
				self.checklist = createTasks( fname, fp )
				fp.close()
				
				if race:
					race.checklist = self.checklist
				break
	
	def setChanged( self ):
		try:
			Model.race.setChanged()
		except:
			pass
		
	def onSize( self, event ):
		width, height = self.GetSize()
		self.tree.SetColumnWidth( 1, max(200, width - self.tree.GetColumnWidth(0) - 8) )
		self.tree.SetSize( self.GetSize() )
		event.Skip()

	def onTreeItemCollapsed( self, event ):
		treeNode = event.GetItem()
		task = self.tree.GetPyData( treeNode )
		task.expand = False
		self.setChanged()

	def onTreeItemExpanded( self, event ):
		treeNode = event.GetItem()
		task = self.tree.GetPyData( treeNode )
		task.expand = True
		self.setChanged()

	def updateStatus( self, treeNode ):
		task = self.tree.GetPyData( treeNode )
		if self.tree.GetFirstChild(treeNode)[0].IsOk():
			img = [self.uncheckedImage, self.partialCheckedImage, self.checkmarkImage][task.status]
		else:
			img = [self.xImage, self.partialCheckedImage, self.checkedImage][task.status]
		self.tree.SetItemImage( treeNode, img, wx.TreeItemIcon_Normal )
		self.tree.SetItemImage( treeNode, img, wx.TreeItemIcon_Expanded )
		child = self.tree.GetFirstChild( treeNode )[0]
		while child.IsOk():
			self.updateStatus( child )
			child = self.tree.GetNextSibling( child )

	def onTreeItemActivated( self, event ):
		treeNode = event.GetItem()
		# If this is not a leaf node, skip it.
		if self.tree.GetFirstChild(treeNode)[0].IsOk():
			return
			
		task = self.tree.GetPyData( treeNode )
		task.status = task.NotDone if task.status else task.Done
		
		# Propagate the update child status to the parent.
		while 1:
			parentNode = self.tree.GetItemParent( treeNode )
			if not parentNode.IsOk():
				break
				
			allChildrenDone = True
			someChildrenDone = False
			childNode = self.tree.GetFirstChild( parentNode )[0]
			while childNode.IsOk():
				childTask = self.tree.GetPyData( childNode )
				if childTask.status == childTask.Done:
					someChildrenDone = True
				else:
					allChildrenDone = False
				childNode = self.tree.GetNextSibling( childNode )
				
			# Check if the parent has the correct status.
			parentTask = self.tree.GetPyData( parentNode )
			if allChildrenDone:			# All children done.
				if parentTask.status == parentTask.Done:
					break
				parentTask.status = parentTask.Done
			elif not someChildrenDone:	# No children done.
				if parentTask.status == parentTask.NotDone:
					break
				parentTask.status = parentTask.NotDone
			else:						# Some children done. 
				if parentTask.status == parentTask.Partial:
					break
				parentTask.status = parentTask.Partial
				
			treeNode = parentNode
		
		self.updateStatus( treeNode )
		self.setChanged()
		
	def expandTree( self, treeNode ):
		child, cookie = self.tree.GetFirstChild( treeNode )
		while child.IsOk():
			self.expandTree( child )
			child = self.tree.GetNextSibling( child )
		task = self.tree.GetPyData( treeNode )
		if task.expand:
			self.tree.Expand( treeNode )

	def addChildren( self, treeNode ):
		task = self.tree.GetPyData( treeNode )
		for t in task.subtasks:
			if t.meetsRequirements():
				child = self.tree.AppendItem(	treeNode,
												t.title,
												data = wx.TreeItemData(t) )
				self.tree.SetItemText( child, t.note, 1 )
				self.addChildren( child )

	def doCollapseAll( self, treeNode ):
		child, cookie = self.tree.GetFirstChild( treeNode )
		while child.IsOk():
			self.doCollapseAll( child )
			child = self.tree.GetNextSibling( child )
		self.tree.Collapse( treeNode )

	def refresh( self ):
		self.updateChecklist()
		self.tree.DeleteAllItems()
		root = self.tree.AddRoot( 'root', data = wx.TreeItemData(self.checklist) )
		self.addChildren( root )
		self.doCollapseAll( root )
		self.updateStatus( root )
		self.expandTree( root )
		
if __name__ == '__main__':
	race = Model.Race()
	race._populate()
	race.finishRaceNow()
	Model.setRace( race )
	
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(1024,600))
	checklist = Checklist(mainWin)
	checklist.refresh()
	
	mainWin.Show()
	app.MainLoop()
	
	'''
	with io.open('Checklist.txt', 'r', encoding='utf-8') as fp:
		root = createTasks( fp )
	root.pprint()
	root.validate()
	'''
