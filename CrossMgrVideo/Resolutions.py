
# from https://webcamtests.com/resolution
resolutions = '''
Standard	Width×Height	Megapixels	Status
VGA	640×480	0.307	Unknown
SD	704×480	0.338	Unknown
DVD NTSC	720×480	0.346	Unknown
WGA	800×480	0.384	Unknown
SVGA	800×600	0.480	Unknown
DVCPRO HD	960×720	0.691	Unknown
XGA	1024×768	0.786	Unknown
HD	1280×720	0.922	Unknown
WXGA	1280×800	1.024	Unknown
SXGA−	1280×960	1.229	Unknown
SXGA	1280×1024	1.311	Unknown
UXGA	1600×1200	1.920	Unknown
FHD	1920×1080	2.074	Unknown
QXGA	2048×1536	3.146	Unknown
QSXGA	2560×2048	5.243	Unknown
QUXGA	3200×2400	7.680	Unknown
DCI 4K	4096×2160	8.847	Unknown
HXGA	4096×3072	12.583	Unknown
UW5K	5120×2160	11.059	Unknown
5K	5120×2880	14.746	Unknown
WHXGA	5120×3200	16.384	Unknown
HSXGA	5120×4096	20.972	Unknown
'''

resolutions = ['{1} [{0}]'.format(*line.split('\t')[:2]) for line in resolutions.split('\n') if line][1:]
