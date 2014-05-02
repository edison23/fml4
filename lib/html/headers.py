# Adding headers, CSS, JS, footers etc. to the plain HTML file.
# edison23

import json, os, sys

def main(parameters):
	script_path = os.path.dirname(os.path.abspath(sys.argv[0]))

	f_in, f_out, options, settings = parameters
	style, font = options
	# Load settings
	styles = json.load(open(os.path.join(script_path, "settings", "html_styles.json"), "rb" ))
	fonts = json.load(open(os.path.join(script_path, "settings", "html_fonts.json"), "rb" ))

	# Order of appendices (since json structure isn't sorted)
	order = styles["order"]

	# For each part open the appropriate files and append them to output
	for item in order:
		if item in styles[style]:
			
			# Body of the document
			if item == "body":
				print "Printing body of the document into target."
				for line in f_in:
					f_out.write(line)
				f_out.write("\n")
			
			# Everything else 
			else:
				print "Printing {} into target.".format(item)
				
				d_item = styles[style][item]	# just lazyness
				
				# If the item has specified afixed (prefix, suffix) -> print them
				if item in styles["afixes"]:
					f_out.write("\n" + styles["afixes"][item][0] + "\n")
				
				# If the item was "style", then we should attempt to append font 
				if item == "style":
					try:
						f = open(os.path.join(script_path, "inc", fonts[font]))
						for line in f:
							f_out.write(line)
						f_out.write("\n")
						f.close()
					except:
						print "File {} doesn't exist.".format(str(fonts[font]))
					
				# Print every file specified in the category (like 2 CSS files)
				for value in d_item:
					try:
						f = open(os.path.join(script_path, "inc", value), "r")
						for line in f:
							f_out.write(line)
						f_out.write("\n")
						f.close()
					except:
						print "File " + str(value) + " doesn't exist."
				
				if item in styles["afixes"]:
					f_out.write("\n" + styles["afixes"][item][1] + "\n")
