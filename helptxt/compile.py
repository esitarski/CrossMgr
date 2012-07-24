import markdown
import glob
import os
import zipfile
import shutil
from contextlib import contextmanager

@contextmanager 
def working_directory(directory): 
	original_directory = os.getcwd() 
	try: 
		os.chdir(directory) 
		yield directory 
	finally: 
		os.chdir(original_directory)
		
def CompileHelp( dir = '.' ):
	with working_directory( dir ):
		md = markdown.Markdown(
				extensions=['toc', 'tables'], 
				safe_mode=True,
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
			
		for fname in glob.glob("./*.txt"):
			print fname, '...'
			with open(fname) as f:
				htmlSave = html = md.convert( f.read() )
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
		htmldocdir = os.path.join('..', 'htmldoc')
		for fname in glob.glob( os.path.join(htmldocdir, '*.html') ):
			os.remove( fname )
		for fname in glob.glob("./*.html"):
			if not ('prolog' in fname or 'epilog' in fname):
				shutil.move( fname, htmldocdir )

if __name__ == '__main__':
	CompileHelp()
