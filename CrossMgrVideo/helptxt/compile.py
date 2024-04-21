import os
import re
import io
import glob
import base64
import shutil
import zipfile
import markdown
import datetime
from contextlib import contextmanager

HtmlDocFolder = 'CrossMgrVideoHtmlDoc'

@contextmanager 
def working_directory(directory): 
	original_directory = os.getcwd() 
	try: 
		os.chdir(directory) 
		yield directory 
	finally: 
		os.chdir(original_directory)
		
def fileOlderThan( srcFile, transFile ):
	try:
		return os.path.getmtime(srcFile) <= os.path.getmtime(transFile)
	except Exception:
		return False

reImage = re.compile( r'src="\.\/images\/([^"]+)"' )
def InlineImages( html ):
	while True:
		match = reImage.search( html )
		if not match:
			break
		fname = match.group(1)
		with open(os.path.join('images',fname), 'rb') as f:
			b64 = base64.b64encode( f.read() )
		sReplace = 'src="data:image/{};base64,{}'.format(
			os.path.splitext(fname)[1][1:],
			b64.decode(),
		)
		html = html.replace( match.group(0), sReplace )
	return html
		
def CompileHelp( dir = '.' ):
	with working_directory( dir ):
		# Check if any of the help files need rebuilding.
		doNothing = True
		for fname in glob.glob("./*.md"):
			fbase = os.path.splitext(os.path.basename(fname))[0]
			fhtml = os.path.join( '..', HtmlDocFolder, fbase + '.html' )
			if not fileOlderThan(fhtml, fname):
				doNothing = False
				break
		if doNothing:
			return
	
		md = markdown.Markdown(
				extensions=['toc', 'tables', 'sane_lists'], 
				#safe_mode='escape',
				output_format='html5'
		)

		with open('markdown.css', 'r', encoding='utf8') as f:
			style = f.read()
		with open('prolog.html', 'r', encoding='utf8') as f:
			prolog = f.read()
			prolog = prolog.replace( '<<<style>>>', style, 1 )
			del style
		with open('epilog.html', 'r', encoding='utf8') as f:
			epilog = f.read().replace('YYYY','{}'.format(datetime.datetime.now().year))

		contentDiv = '<div class="content">'
		
		with open('Links.md', 'r', encoding='utf8') as f:
			links = f.read()
			
		for fname in glob.glob("./*.txt"):
			print( fname, '...' )
			with open(fname, 'r', encoding='utf8') as f:
				input = io.StringIO()
				input.write( links )
				input.write( f.read() )
				
				htmlSave = html = md.convert( input.getvalue() )
				input.close()
				
				html = html.replace( '</div>', '</div>' + '\n' + contentDiv, 1 )
				if htmlSave == html:
					html = contentDiv + '\n' + html
				html += '\n</div>\n'
				html = InlineImages( html )
			with open( os.path.splitext(fname)[0] + '.html', 'w', encoding='utf8') as f:
				f.write( prolog )
				f.write( html )
				f.write( epilog )
			md.reset()

		# Put all the html files into a zipfile.
		ZipFileName = 'CrossMgrVideoDocHtml.zip'
		zf = zipfile.ZipFile( ZipFileName, 'w' )
		for fname in glob.glob("./*.html"):
			zf.write( fname )
		zf.close()
		
		# Copy all the files into the htmldoc directory.
		htmldocdir = os.path.join('..', HtmlDocFolder)
		if not os.path.exists( htmldocdir ):
			os.mkdir( htmldocdir )

		for fname in glob.glob( os.path.join(htmldocdir, '*.html') ):
			os.remove( fname )
		for fname in glob.glob("./*.html"):
			if not ('prolog' in fname or 'epilog' in fname):
				shutil.move( fname, htmldocdir )

if __name__ == '__main__':
	CompileHelp()
