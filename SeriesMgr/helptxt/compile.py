import markdown
import glob
import os
import re
import io
import six
import base64
import zipfile
import shutil
import datetime
StringIO = six.moves.StringIO
from contextlib import contextmanager

HtmlDocFolder = 'SeriesMgrHtmlDoc'

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
	except:
		return False

reImage = re.compile( r'src="\.\/images\/([^"]+)"' )
def InlineImages( html ):
	while 1:
		match = reImage.search( html )
		if not match:
			break
		fname = match.group(1)
		with io.open(os.path.join('images',fname), 'rb') as f:
			b64 = base64.b64encode( f.read() )
		sReplace = 'src="data:image/{};base64,{}'.format(
			os.path.splitext(fname)[1][1:],
			b64,
		)
		html = html.replace( match.group(0), sReplace )
	return html
		
def CompileHelp( dir = '.' ):
	with working_directory( dir ):
		# Check if any of the help files need rebuilding.
		doNothing = True
		for fname in glob.glob("./*.txt"):
			fbase = os.path.splitext(os.path.basename(fname))[0]
			fhtml = os.path.join( '..', HtmlDocFolder, fbase + '.html' )
			if not fileOlderThan(fhtml, fname):
				doNothing = False
				break
		if doNothing:
			six.print_( 'Nothing to do.' )
			return
	
		md = markdown.Markdown(
				extensions=['toc', 'tables', 'sane_lists'], 
				#safe_mode='escape',
				output_format='html5'
		)

		with io.open('markdown.css', 'r') as f:
			style = f.read()
		with io.open('prolog.html', 'r') as f:
			prolog = f.read()
			prolog = prolog.replace( '<<<style>>>', style, 1 )
			del style
		with io.open('epilog.html', 'r') as f:
			epilog = f.read().replace('YYYY','{}'.format(datetime.datetime.now().year))

		contentDiv = '<div class="content">'
		
		with io.open('Links.md', 'r') as f:
			links = f.read()
			
		for fname in glob.glob("./*.txt"):
			six.print_( fname, '...' )
			with io.open(fname, 'r') as f:
				input = StringIO()
				input.write( links )
				input.write( f.read() )
				
				htmlSave = html = md.convert( input.getvalue() )
				input.close()
				
				html = html.replace( '</div>', '</div>' + '\n' + contentDiv, 1 )
				if htmlSave == html:
					html = contentDiv + '\n' + html
				html += '\n</div>\n'
				html = InlineImages( html )
			with io.open( os.path.splitext(fname)[0] + '.html', 'w' ) as f:
				f.write( prolog )
				f.write( html )
				f.write( epilog )
			md.reset()

		# Put all the html files into a zipfile.
		ZipFileName = 'SeriesMgrDocHtml.zip'
		zf = zipfile.ZipFile( ZipFileName, 'w' )
		for fname in glob.glob("./*.html"):
			if not ('prolog' in fname or 'epilog' in fname):
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
