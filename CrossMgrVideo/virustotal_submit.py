#!/usr/bin/env python

__description__ = 'Program to submit files to VirusTotal'
__author__ = 'Didier Stevens'
__version__ = '0.0.3'
__date__ = '2013/12/10'

"""

Source code put in public domain by Didier Stevens, no Copyright
https://DidierStevens.com
Use at your own risk

History:
  2013/03/10: start based on virustotal-search.py version 0.0.5
  2013/04/19: refactoring; proxies; password protected ZIP file
  2013/09/22: bugfix error opening file
  2013/12/06: v0.0.3: extra error handling
  2013/12/10: handling when response_code not 1

Todo:
"""

import optparse
import six
import time
import sys
urllib = six.moves.urllib
import os
import zipfile

try:
    import poster
except:
    print('Module poster missing: https://pypi.python.org/pypi/poster')
    exit()

try:
    import json
    jsonalias = json
except:
    try:
        import simplejson
        jsonalias = simplejson
    except:
        print('Modules json and simplejson missing')
        exit()

VIRUSTOTAL_API2_KEY = '64b7960464d4dbeed26ffa51cb2d3d2588cb95b1ab52fafd82fb8a5820b44779'
HTTP_PROXY = ''
HTTPS_PROXY = ''

VIRUSTOTAL_SCAN_URL = 'https://www.virustotal.com/vtapi/v2/file/scan'

def VTHTTPScanRequest(filename, options):
    if filename.lower().endswith('.zip') and not options.zip:
        oZipfile = None
        file = None
        try:
            oZipfile = zipfile.ZipFile(filename, 'r')
            file = oZipfile.open(oZipfile.infolist()[0], 'r', 'infected')
            data = file.read()
            postfilename = oZipfile.infolist()[0].filename
        except:
            return None, sys.exc_info()[1]
        finally:
            if file:
                file.close()
            if oZipfile:
                oZipfile.close()
    else:
        file = None
        try:
            file = open(filename, 'rb')
            data = file.read()
            postfilename = filename
        except IOError as e:
            return None, str(e)
        finally:
            if file:
                file.close()
    params = []
    params.append(poster.encode.MultipartParam('apikey', VIRUSTOTAL_API2_KEY))
    params.append(poster.encode.MultipartParam('file', value=data, filename=os.path.basename(postfilename)))
    datagen, headers = poster.encode.multipart_encode(params)
    req = urllib.request.Request(VIRUSTOTAL_SCAN_URL, datagen, headers)
    try:
        if sys.hexversion >= 0x020601F0:
            hRequest = six.moves.urllib.request.urlopen(req, timeout=600)
        else:
            hRequest = six.moves.urllib.request.urlopen(req)
    except urllib2.HTTPError as e:
        return None, str(e)
    try:
        data = hRequest.read()
    except:
        return None, 'Error'
    finally:
        hRequest.close()
    return data, None

def File2Strings(filename):
    try:
        f = io.open(filename, 'r', encoding='utf-8')
    except:
        return None
    try:
        return [line.rstrip('\n') for line in f.readlines()]
    except:
        return None
    finally:
        f.close()

def SetProxiesIfNecessary():
    global HTTP_PROXY
    global HTTPS_PROXY

    dProxies = {}
    if HTTP_PROXY != '':
        dProxies['http'] = HTTP_PROXY
    if HTTPS_PROXY != '':
        dProxies['https'] = HTTPS_PROXY
    if os.getenv('http_proxy') != None:
        dProxies['http'] = os.getenv('http_proxy')
    if os.getenv('https_proxy') != None:
        dProxies['https'] = os.getenv('https_proxy')
    if dProxies != {}:
        sox.moves.urllib.request.install_opener(urllib2.build_opener(six.urllib.request.ProxyHandler(dProxies), poster.streaminghttp.StreamingHTTPSHandler()))

def VirusTotalSubmit(filenames, options):
	poster.streaminghttp.register_openers()

	SetProxiesIfNecessary()

	with io.open('virustotal.html', 'w', encoding='utf-8') as f:
		f.write( '<html>\n' )
		f.write( '<head>\n' )
		f.write( '<style>body { font-family:sans-serif; font-size:200%; }</style>\n' )
		f.write( '</head>\n' )
		f.write( '<body>\n' )
		for filename in filenames:
			if filename != filenames[0]:
				time.sleep(options.delay)
			jsonResponse, error = VTHTTPScanRequest(filename, options)
			if jsonResponse == None:
				f.write( '{}: Scan failed (jsonResponse=None)<br/>\n'.format( os.path.basename(filename)) )
			else:
				oResult = jsonalias.loads(jsonResponse)
				if oResult['response_code'] == 1:
					f.write( '{}: <a href="{}">VirusTotal Results</a><br/>\n'.format( os.path.basename(filename), oResult['permalink'] ) )
				else:
					f.write( '{}: Scan failed (response_code={}<br/>\n'.format( os.path.basename(filename), oResult['response_code']) )
		f.write( '</body>\n' )
		f.write( '</html>\n' )

def Main():
    global VIRUSTOTAL_API2_KEY

    oParser = optparse.OptionParser(usage='usage: %prog [options] file\n' + __description__, version='%prog ' + __version__)
    oParser.add_option('-d', '--delay', type=int, default=16, help='delay in seconds between queries (default 16s, VT rate limit is 4 queries per minute)')
    oParser.add_option('-k', '--key', default='', help='VirusTotal API key')
    oParser.add_option('-f', '--file', help='File contains filenames to submit')
    oParser.add_option('-z', '--zip', action='store_true', default=False, help='Submit the ZIP file, not the content of the ZIP file')
    (options, args) = oParser.parse_args()

    if not options.file and len(args) == 0:
        oParser.print_help()
        print('')
        print('  Source code put in the public domain by Didier Stevens, no Copyright')
        print('  Use at your own risk')
        print('  https://DidierStevens.com')
        return
    if os.getenv('VIRUSTOTAL_API2_KEY') != None:
        VIRUSTOTAL_API2_KEY = os.getenv('VIRUSTOTAL_API2_KEY')
    if options.key != '':
        VIRUSTOTAL_API2_KEY = options.key
    if VIRUSTOTAL_API2_KEY == '':
        print('You need to get a VirusTotal API key and set environment variable VIRUSTOTAL_API2_KEY, use option -k or add it to this program.\nTo get your API key, you need a VirusTotal account.')
    elif options.file:
        VirusTotalSubmit(File2Strings(options.file), options)
    else:
        VirusTotalSubmit(args, options)

if __name__ == '__main__':
    Main()
