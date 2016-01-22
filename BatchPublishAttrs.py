import Utils
from collections import namedtuple

BatchAttr = namedtuple('BatchAttr', 'name uiname filecode func ftp note')

batchPublishAttr = (
	BatchAttr('Html',	_('Html'),			'html', 		'menuPublishHtmlRaceResults', True, _('as .html file')),
	BatchAttr('IndexHtml',	_('Index Html'),'indexhtml', 	'menuPublishHtmlIndex', True, _('index.html file for all CrossMgr races in folder')),
	BatchAttr('Pdf',	_('Pdf'),			'pdf',  		'menuPrintPDF', True, _('as .pdf file')),
	BatchAttr('Excel',	_('Excel'), 		'excel', 		'menuPublishAsExcel', True, _('as .xls file')),
	BatchAttr('USAC',	_('USAC'),			'usacexcel',	'menuExportUSAC', True, _('as .xls upload file')),
	BatchAttr('UCI',	_('UCI'),			'uciexcel',		'menuExportUCI', True, _('as .xls upload file')), 
	BatchAttr('WebScorer', _('WebScorer'),	'webscorertxt',	'menuExportWebScorer', True, _('as .txt upload file')),
	BatchAttr('Facebook', _('Facebook'),	None,			'menuPrintPNG', False, _('as .png upload files in Facebook folder')),
)

batchPublishRaceAttr = ['publishFormat' + attr.name for attr in batchPublishAttr] + ['publishFormatBikeReg']

def setDefaultRaceAttr( obj ):
	for attr in batchPublishRaceAttr[:4]:
		setattr( obj, attr, 1 )
