import os
from collections import namedtuple

BatchAttr = namedtuple('BatchAttr', 'name uiname filecode func ftp note getFName')

def fNew( suffix ):
	return lambda fNewBase: fNewBase + suffix

batchPublishAttr = (
	BatchAttr('Html',	_('Html'),			'html', 		'menuPublishHtmlRaceResults', True, _('as .html file'), fNew('.html') ),
	
	BatchAttr('IndexHtml',	_('Index Html'),'indexhtml', 	'menuPublishHtmlIndex', True, _('index.html for all CrossMgr races in folder'),
		lambda fNewBase: os.path.join(os.path.dirname(fNewBase), 'index.html')),
		
	BatchAttr('Pdf',	_('Pdf'),			'pdf',  		'menuPrintPDF', True, _('as .pdf file'), fNew('.pdf') ),
	BatchAttr('Excel',	_('Excel'), 		'excel', 		'menuPublishAsExcel', True, _('as .xlsx file'), fNew('.xlsx') ),

	BatchAttr('RaceDB',	_('RaceDB'),		None,			'menuPublishAsRaceDB', False, _('upload results to RaceDB database'), None),
	
	BatchAttr('UCI Dataride', _('UCI'),	'uciexcel',		'menuExportUCI', True, _('as .xlsx UCI Dataride upload, one file per category'), None),

	BatchAttr('USAC',	_('USAC'),			'usacexcel',	'menuExportUSAC', True, _('as .xls USAC upload file'), fNew('-USAC.xls') ),
	
	BatchAttr('VTTA',	_('VTTA'),	 		'vttaexcel', 	'menuExportVTTA', True, _('as .xlsx file'), fNew('-VTTA.xlsx') ),
	BatchAttr('JPResults',	_('JPResults'),	 'jpresultsexcel','menuExportJPResults', True, _('as .xlsx file'), fNew('-JP.xlsx') ),
	
	BatchAttr('WebScorer', _('WebScorer'),	'webscorertxt',	'menuExportWebScorer', True, _('as .txt WebScorer upload file'), fNew('-WebScorer.txt') ),
	BatchAttr('Facebook', _('Facebook'),	None,			'menuPrintPNG', False, _('as .png upload files in Facebook folder'), None ),
)

batchPublishRaceAttr = ['publishFormat' + attr.name for attr in batchPublishAttr] + ['publishFormatBikeReg']
formatFilename = { attr.filecode: attr.getFName for attr in batchPublishAttr }

def setDefaultRaceAttr( obj ):
	for attr in batchPublishRaceAttr[:4]:
		setattr( obj, attr, 1 )
