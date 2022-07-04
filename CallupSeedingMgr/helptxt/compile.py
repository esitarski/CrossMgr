import markdown
import glob
import os
import codecs
import zipfile
import shutil
from io import StringIO
from contextlib import contextmanager

HtmlDocFolder = 'CallupSeedingMgrHtmlDoc'

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
	
		md = markdown.Markdown(
				extensions=['toc', 'tables', 'sane_lists'], 
				#safe_mode='escape',
				output_format='html5'
		)

		with codecs.open('markdown.css', 'r', encoding='utf8') as f:
			style = f.read()
		with codecs.open('prolog.html', 'r', encoding='utf8') as f:
			prolog = f.read()
			prolog = prolog.replace( '<<<style>>>', style, 1 )
			del style
		with codecs.open('epilog.html', 'r', encoding='utf8') as f:
			epilog = f.read()

		contentDiv = '<div class="content">'
		
		with open('Links.md') as f:
			links = f.read()
			
		for fname in glob.glob("./*.md"):
			if fname.endswith('Links.md'):
				continue
			print(fname, '...')
			with codecs.open(fname, 'r', encoding='utf8') as f:
				input = StringIO()
				input.write( links )
				input.write( f.read() )
				
				htmlSave = html = md.convert( input.getvalue() )
				input.close()
				
				html = html.replace( '</div>', '</div>' + '\n' + contentDiv, 1 )
				if htmlSave == html:
					html = contentDiv + '\n' + html
				html += '\n</div>\n'
			with codecs.open( os.path.splitext(fname)[0] + '.html', 'w', encoding='utf8') as f:
				f.write( prolog )
				f.write( html )
				f.write( epilog )
			md.reset()

		'''
		# Put all the html files into a zipfile.
		ZipFileName = 'CrossMgrDocHtml.zip'
		zf = zipfile.ZipFile( ZipFileName, 'w' )
		for fname in glob.glob("./*.html"):
			zf.write( fname )
		zf.close()
		'''
		
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
