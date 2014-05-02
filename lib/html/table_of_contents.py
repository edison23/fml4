# Creating table of contents
# Probably should be merged with "replace_strings.py" somehow
import re, os, sys
import lists

def main(parameters):
	script_path = os.path.dirname(os.path.abspath(sys.argv[0]))
	
	f_in, f_out, options, settings = parameters
	# Auxiliary file with list of headings, images and so on
	f_aux = open(os.path.join(script_path, "tempfiles", "auxf.fml"), "r")

	# Auxiliary file with TOC in FML markup (now empty)
	f_toc = open(os.path.join(script_path, "tempfiles", "toc.fml"), "w+")

	for line in f_in:
		# If line begins and ends with "print_toc" (except the <br> shit) -> let's print TOC
		if "print_toc" == line.strip().rstrip("<br>"):
			for line in f_aux:
				item = re.match(r"^head: id (\d+); lvl (\d+); name (.*)$", line)
				if item:
					lvl = int(item.group(2)) - 1
					if lvl < 0:
						lvl = 0
					toc_item = "\t" * lvl + "+ [url=#" + str(item.group(1)) + " " + item.group(3) + "]\n"
					f_toc.write(toc_item)
			
			# Add empty line at the end of TOC file - otherwise list will not be closed
			f_toc.write("\n")
			f_toc.seek(0)
			
			# TODO - load the universal_html converters instead of it's own here
			
			# f_toch - the file for writing html version of toc must be opened here and then closed,
			# bcs since it is opened in the tuple it doesnt work the way it does when it's opened in 
			# function call (doesnt close itself)
			f_toch = open(os.path.join(script_path, "tempfiles", "toc.html"), "w")
			parameters = (f_toc, f_toch, [], settings)
			lists.main(parameters)
			f_toch.close()

			f_out.write('<div class="toc">\n')
			f_out.write(open(os.path.join(script_path, "tempfiles", "toc.html"), "r").read())
			f_out.write('</div>')
	
		else:
			f_out.write(line)

	f_aux.close()