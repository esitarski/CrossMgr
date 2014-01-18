import markdown
import glob
import os
import zipfile
import shutil
import cStringIO as StringIO
from contextlib import contextmanager

HtmlDocFolder = 'CrossMgrHtmlDoc'

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
			return
	
		md = markdown.Markdown(
				extensions=['toc', 'tables', 'sane_lists'], 
				#safe_mode='escape',
				output_format='html4'
		)

		with open('markdown.css') as f:
			style = f.read()
		with open('prolog.html') as f:
			prolog = f.read()
			prolog = prolog.replace( '<<<style>>>', style, 1 )
			del style
		with open('epilog.html') as f:
			epilog = f.read()

		contentDiv = '<div class="content">'
		
		with open('Links.md') as f:
			links = f.read()
			
		for fname in glob.glob("./*.txt"):
			print fname, '...'
			with open(fname) as f:
				input = StringIO.StringIO()
				input.write( links )
				input.write( f.read() )
				
				htmlSave = html = md.convert( input.getvalue() )
				input.close()
				
				html = html.replace( '</div>', '</div>' + '\n' + contentDiv, 1 )
				if htmlSave == html:
					html = contentDiv + '\n' + html
				html += '\n</div>\n'
			with open( os.path.splitext(fname)[0] + '.html', 'w' ) as f:
				f.write( prolog )
				f.write( html )
				f.write( epilog )
			md.reset()

		# Put all the html files into a zipfile.
		ZipFileName = 'CrossMgrDocHtml.zip'
		zf = zipfile.ZipFile( ZipFileName, 'w' )
		for fname in glob.glob("./*.html"):
			zf.write( fname )
		zf.close()
		
		# Copy all the files into the htmldoc directory.
		htmldocdir = os.path.join('..', HtmlDocFolder)
		for fname in glob.glob( os.path.join(htmldocdir, '*.html') ):
			os.remove( fname )
		for fname in glob.glob("./*.html"):
			if not ('prolog' in fname or 'epilog' in fname):
				shutil.move( fname, htmldocdir )

if __name__ == '__main__':
	CompileHelp()
