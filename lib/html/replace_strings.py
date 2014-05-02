# Replaces strings for things as date, document title and such
# Alfa version and very very bad one. Dev should commit seppuku.
import re, os, sys
from time import gmtime, strftime

def main(parameters):
	script_path = os.path.dirname(os.path.abspath(sys.argv[0]))
	
	f_in, f_out, options, settings = parameters
	f_aux = open(os.path.join(script_path, "tempfiles", "auxf.fml"), "r")

	for line in f_in:
		if "print_doc_title" in line:
			title = re.match(r"^title: (.*?)$", f_aux.read(), re.MULTILINE)
			if title:
				title = title.group(1)
			else:
				title = settings["default_doc_title"]
			line = line.replace("print_doc_title", title)
			f_out.write(line)

		elif "print_last_updated" in line:
			# TODO: Make this user-changable
			line = line.replace("print_last_updated", '<div id="last_update">\n\tLast update: ' + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ' UTC\n</div>')
			f_out.write(line)

		
		else:
			f_out.write(line)

