# Main notes converter script

import lib.convert, file_ops
import argparse, json, re, os, sys
from sys import exit

# Func. to return list of files conforming with the mask in each
# directory and subdirectory. Recursive - that's why it's split
# from the create_filelist() function
script_path = os.path.dirname(os.path.abspath(sys.argv[0]))

def list_files(input, f_list, settings):
	for item in os.listdir(input):
		# If the path points to file and it conforms with mask -> write it
		if os.path.isfile(os.path.join(input, item)) and re.match(r"^" + settings["files_prefix"] + r".*?" + settings["files_suffix"] + r"$", item):
			f_list.write(os.path.abspath(os.path.join(input, item)) + "\n")
		
		# If the path is directory -> recursive call of this function
		elif os.path.isdir(os.path.join(input, item)):
			list_files(os.path.join(input, item), f_list, settings)

# Func. creates file list of files to be processed
def create_filelist(input, settings):
	global script_path
	f_list = open(os.path.join(script_path, "tempfiles", "filelist.lst"), "w+")
	list_files(input, f_list, settings)
	return f_list

# Process files in the file list
def cycle_thru_files(f_list, parameters):
	input, output, style, font, format, settings = parameters
	f_list.seek(0)
	for line in f_list:
		print line,
	print

	f_list.seek(0)
	for line in f_list:
		line = line.strip()
		print "\nProcessing file {}".format(line)
		
		# Convert file
		if not lib.convert.main(line, format, [style, font], settings):
			return False
		
		# Move & rename the final file, clean up temp files 
		# (abort if path doesnt exist and user didnt wish to create it)
		# print "peniiiiiiiiiiiiiiiiiiiiiiis", output + os.path.basename(line)
		if not file_ops.move_finished(input, os.path.join(output, os.path.basename(line) + ".html")):
			return False

# Detection of what shall we do with a drunken sailer
def detection(parameters):
	global script_path
	input, output, style, font, format, settings = parameters
	
	# Intput is directory -> search for files for processing
	if os.path.isdir(input):
		f_list = create_filelist(input, settings)
		cycle_thru_files(f_list, parameters)
	
	# input is file -> either file list (-> directly process one by one)
	# or single file (call directly conversion function)
	elif os.path.isfile(input):
		if os.path.basename(input) == settings["file_list_name"]:
			cycle_thru_files(open(input), parameters)
		else:
			print "\nProcessing file {}".format(input)
			lib.convert.main(input, format, [style, font], settings)
			file_ops.move_finished(input, output)
	else:
		print "Input file {} doesn't exist or is neither file or directory.".format(input)

# Load configuration files
try:
	settings = json.load(open(os.path.join(script_path, "settings", "general.json")))
	html_styles = json.load(open(os.path.join(script_path, "settings", "html_styles.json")))
	html_fonts = json.load(open(os.path.join(script_path, "settings", "html_fonts.json")))
except:
	print "Some of the configuration files could not be loaded. They might not exist or contain syntax errors.\nCheck the settings/ folder for following files:\nhtml_styles.json\nhtml_fonts.json\ngeneral.json"
	exit()

# Load possible styles to list so they can be listed as possible command-line parameters
# for user
style_choices = []
font_choices = []

for item in html_styles:
	style_choices.append(item)

for item in html_fonts:
	font_choices.append(item)

# Argument parser
parser=argparse.ArgumentParser(
    description="Fast Markup Language (FML) parser",
    epilog="For complete documentation see... oh wait, there is none, yet. Bad luck, sorry.")
parser.add_argument('input', help='input path/file')
parser.add_argument('output', help='output path/file')
parser.add_argument('-s', dest='style', help='target style', choices=style_choices, default='web')
parser.add_argument('-f', dest='font', help='target font', choices=font_choices, default='sans')
parser.add_argument('-v', '--version', action='version', version='%(prog)s 4.0')

args=parser.parse_args()

# "format" argument is now harcoded since other formats are not available
parameters = [args.input, args.output, args.style, args.font, "html", settings]
detection(parameters)