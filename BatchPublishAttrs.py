import Utils

with Utils.SuspendTranslation():
	batchPublishAttr = (
		(_('Html'),			'html', 		'menuPublishHtmlRaceResults'),
		(_('Pdf'),			'pdf',  		'menuPrintPDF'),
		(_('Excel'), 		'excel', 		'menuPublishAsExcel'),
		(_('USAC'),			'usacexcel',	'menuExportUSAC'),
		(_('UCI'),			'uciexcel',		'menuExportUCI'), 
		(_('WebScorer'),	'webscorertxt',	'menuExportWebScorer'),
	)

batchPublishRaceAttr = ['publishFormat' + attr[0] for attr in batchPublishAttr] + ['publishFormatBikeReg']

