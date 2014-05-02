# -*- coding: utf-8 -*-
# Lists conversion

import json, re, os, sys

# Open dictionary with list keywords
# with open( "../../tagsets/itemize.json", "rb" ) as fp:
# 	bullet_keys = json.load(fp)
script_path = os.path.dirname(os.path.abspath(sys.argv[0]))
bullet_keys = json.load(open(os.path.join(script_path, "tagsets", "itemize.json"), "rb" ))
	
def main(parameters):
	f_in, f_out, _, settings = parameters
	# print os.path.abspath(f_in), "penis"
	# Initialize stack for lists
	list_stack = []
	noprocess = 0
	
	for line in f_in:
		# Decode from utf-8
		line = line.decode("utf-8")
		
		# check if line(s) can be processed
		if "</noprocess>" in line:	# this isn't very robust against errors like "</noprocess><noprocess>", but that shouldn't occur anyway
			f_out.write(line.encode("utf-8"))
			noprocess = 0
			continue	# dont process the line with tag any further
		
		if "<noprocess>" in line or noprocess == 1:
			f_out.write(line.encode("utf-8"))
			noprocess = 1
			continue
		
		# Control var for active lists
		active = False

		# If ordered or unordered list keyword was found:
		for key in bullet_keys:
			if re.match(r"^" + re.escape(key) + " ", line.strip("\t")):
				line, list_stack = bullets(line.rstrip(), key, list_stack)
				active = True
		# If there was no list found and there are some active, close them all
		if (not active) and (list_stack):
			line, list_stack = list_close(line, "", list_stack, all=1)
		line = line
		
		# Links
		line = re.sub(r"\[url=(.*?) (.*?)\]", r'<a href="\1">\2</a>', line)
		
		f_out.write(line.encode("utf-8"))
			
def list_new(line, uol, list_stack):
	line = "<" + bullet_keys[uol] + ">\n" + list_newline(line, uol)
	list_stack.append(uol)
	return line, list_stack

def list_newline(line, uol):
	# Get the original characters that are to be replaced
	c = re.escape(uol)
	
	# Count tabs and create appropriate tabs string equal to the one in the line 
	tabs = line.count("\t")
	tabs_string = tabs * "\t"
	
	line = re.sub(tabs_string + c + r" (.*)", "\t" + r"<li>\1</li>\n", line)
	
	return line

def list_close(line, uol, list_stack, all=0):
	temp_line = ""
	# Closing only one or some lists, not all
	if all == 0:
		# diff is difference between current level of list (i.e. number of tabs) 
		# and number of lists in the stack (that, obviously, need to be closed)
		diff = len(list_stack) - (line.count("\t") + 1)
		for i in xrange(diff):
			temp_line += "</" + bullet_keys[list_stack.pop()] + ">\n"
		line = temp_line + list_newline(line, uol)

	# Closing all lists
	elif all == 1:
		while list_stack:
			temp_line += "</" + bullet_keys[list_stack.pop()] + ">\n"
		line = temp_line + line

	return line, list_stack

def bullets(line, uol, list_stack):
	# If there is no list active
	if len(list_stack) == 0:
		line, list_stack = list_new(line, uol, list_stack)
	
	else:
		# If the number of tabs is higher/lower than number of lists active, create/close a list,
		# if equal, just add list item
		# (tabs begin at 0, lists at 1, thus a "+1" correction required)
		if (len(list_stack)) < (line.count("\t") + 1):
			line, list_stack = list_new(line, uol, list_stack)
		
		elif (len(list_stack)) == (line.count("\t") + 1):
			line = list_newline(line, uol)
		
		else:
			line, list_stack = list_close(line, uol, list_stack)	# closing only 1 list
	
	return line, list_stack
