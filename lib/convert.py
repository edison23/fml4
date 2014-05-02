# Main universal code convertor

from datetime import datetime
import shutil, os, sys
from universal_html import inline, lists, code, tables
from html import headers, table_of_contents, replace_strings

script_path = os.path.dirname(os.path.abspath(sys.argv[0]))

def convert_files(paramters):
	global script_path
	input, output, options, modules, settings = paramters
	tempfile = os.path.join(script_path, "tempfiles", "temp.tmp")
	f_temp = open(tempfile, "w+")
	f_out = open(output, "w+")

	paramters = (f_temp, f_out, options, settings)
	# Copy original file to temporary, process temp file and 
	# produce out file, then copy outfile (which is now in place 
	# of the original file) to the temp file and repeat the process
	# for each module listed in modules array.
	
	try:
		shutil.copyfile(input, tempfile)
	except IOError:
		print "Input path does not exist."
		return False

	for module in modules:
		module.main(paramters)
		f_temp.seek(0)
		f_out.seek(0)
		shutil.copyfile(output, tempfile)

	try:
		os.remove(tempfile)
	except:
		print "Failed to remove {}".format(tempfile)

	f_out.close()
	f_temp.close()

def main(input, format, options, settings):
	global script_path
	# Do the universal conversion
	modules = [code, tables, lists, inline]
	paramters = (input, os.path.join(script_path, "tempfiles", "out.html"), [], modules, settings)
	convert_files(paramters)

	# Now decide which format shall be used for output
	# HTML adds neccessary headers, footers etc.
	# Latex... we'll see, what that'll do, but it'll have to be
	# a full conversion again
	if format == "html":
		modules = [headers, table_of_contents, replace_strings]
		paramters = (os.path.join(script_path, "tempfiles", "out.html"), os.path.join(script_path, "tempfiles", "out_h.html"), options, modules, settings)
		convert_files(paramters)
		return True

	else:
		print "Format specified is not supported."
		return False
