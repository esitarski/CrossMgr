import os
from collections import namedtuple
import Utils

BatchAttr = namedtuple('BatchAttr', 'name uiname filecode func ftp note getFName')

batchPublishAttr = (
	BatchAttr('Html',	_('Html'),			'html', 		'menuPublishHtmlRaceResults', True, _('as .html file'),
		lambda fnameBase: fnameBase + '.html'),
	BatchAttr('IndexHtml',	_('Index Html'),'indexhtml', 	'menuPublishHtmlIndex', True, _('index.html for all CrossMgr races in folder'),
		lambda fnameBase: os.path.join(os.path.dirname(fnameBase), 'index.html')),
	BatchAttr('Pdf',	_('Pdf'),			'pdf',  		'menuPrintPDF', True, _('as .pdf file'),
		lambda fnameBase: fnameBase + '.pdf'),
	BatchAttr('Excel',	_('Excel'), 		'excel', 		'menuPublishAsExcel', True, _('as .xlsx file'),
		lambda fnameBase: fnameBase + '.xlsx'),
		
	BatchAttr('RaceDB',	_('RaceDB'),	None,				'menuPublishAsRaceDB', False, _('upload results to RaceDB database'),
		None),
	
	BatchAttr('USAC',	_('USAC'),			'usacexcel',	'menuExportUSAC', True, _('as .xls upload file'),
		lambda fnameBase: fnameBase + '-USAC.xls'),
	BatchAttr('UCI',	_('UCI'),			'uciexcel',		'menuExportUCI', True, _('as .xlsx upload file'),
		None),
	BatchAttr('VTTA',	_('VTTA'),	 		'vttaexcel', 	'menuExportVTTA', True, _('as .xlsx file'),
		lambda fnameBase: fnameBase + '-VTTA.xlsx'),
	BatchAttr('JPResults',	_('JPResults'),	 		'jpresultsexcel', 	'menuExportJPResults', True, _('as .xlsx file'),
		lambda fnameBase: fnameBase + '-JP.xlsx'),
	BatchAttr('WebScorer', _('WebScorer'),	'webscorertxt',	'menuExportWebScorer', True, _('as .txt upload file'),
		lambda fnameBase: fnameBase + '-WebScorer.txt'),
	BatchAttr('Facebook', _('Facebook'),	None,			'menuPrintPNG', False, _('as .png upload files in Facebook folder'),
		None ),
)

batchPublishRaceAttr = ['publishFormat' + attr.name for attr in batchPublishAttr] + ['publishFormatBikeReg']
formatFilename = { attr.filecode: attr.getFName for attr in batchPublishAttr }

def setDefaultRaceAttr( obj ):
	for attr in batchPublishRaceAttr[:4]:
		setattr( obj, attr, 1 )
