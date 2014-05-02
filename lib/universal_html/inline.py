# -*- coding: utf-8 -*-
# Convert inline tags and dividers (headings, titles, ...)
import re, json, os, sys
script_path = os.path.dirname(os.path.abspath(sys.argv[0]))

def main(parameters):
	global script_path
	f_in, f_out, _, settings = parameters
	head_id = 1 	# headers counter
	noprocess = 0 	# <pre> indicator - lines in <pre> are not searched for anything (except syntax HL)
	tags = [] 	# stack for nested tags

	
	# File for names of images, headings and such staff
	# that need to be saved externally.
	f_aux = open(os.path.join(script_path, "tempfiles", "auxf.fml"), "w+")
	
	for line in f_in:
		line = line.decode("utf-8")
		
		if "</noprocess>" in line:
			f_out.write(line.encode("utf-8"))
			noprocess = 0
			continue
		
		if "<noprocess>" in line or noprocess == 1:
			f_out.write(line.encode("utf-8"))
			noprocess = 1
			continue
			
		line = images(line, f_aux)
		head_id, line = headings(line, head_id, f_aux)
		line = dividers(line, f_aux)
		line = inline_format(line, tags, settings)
		line = add_br(line)
		line = replacements(line)
		
		line = line.replace(u"\x10", "[").replace(u"\x11", "]").replace(u"\x12", "|")

		f_out.write(line.encode("utf-8"))
	
	f_aux.close()

# Function to create headings from lines that begin with "$[number]"
def headings(line, head_id, f_aux):
	head = re.match(r"^\$(\d) (.*)", line)
	if head:
		line = '<h' + head.group(1) + ' id="' + str(head_id) + r'">' + head.group(2) + '</h' + head.group(1) +'>\n'
		
		# Write the heading to auxiliary file so TOC can be created
		f_aux.write(("head: id " + str(head_id) + "; lvl " + head.group(1) + "; name " + head.group(2) + "\n").encode("utf-8"))
		head_id += 1
	return head_id, line

# Function takes lines that begin with "$img", accepts optional arg "-[size]"
# (eg. "$img-s") which gives user option to tell how big the picture should be -
# s: small, m: medium, f: 100%. Follows oblig. name and opt. description.
def images(line, f_aux):
	if "$img" in line:
		width = re.match(r"^\$img(?:-([sml]))?", line)	# optional param with width - small/medium/large
		if width:
			width = width.group(1)
			if not width:
				width = ""
		else:
			return line
		
		name, desc = re.match(r"^\$img.*? (.+?)\s(.*)", line).groups()	# match name and description, if any desc
		if not desc:
			desc = ""
		f_aux.write("img: " + name + "\n")
		return "<div class=\"images " + width + "\"><a target=\"_blank\" href=\".files/" + name + "\"><img class=\"blahh\" src=\".files/" + name + "\" title=\"" + desc + "\" width=\"" + width + "\"></a><span class=\"desc\">" + desc + "</span></div><br>\n"
	return line

# General divider (in html creates <div class="[name]") - takes anything, that's why it's called last
def dividers(line, f_aux):
	title = re.match(r"^\$title (.*)", line.encode("utf-8"))
	if title:
		f_aux.write("title: " + str(title.group(1)) + "\n")
	line = re.sub(r"^\$([a-z]+) (.*)", r'<div class="\1">\2</div>', line)
	return line

# Inline format that has simple syntax - same beginning and ending tag.
# The tags and substitutions are taken from inline_format.json
# It processes the line in multiple passes,
# starting with from the deepest level of nesting, then continuing to the upper
# layers until there are no unparsed tages (regex returns null result)
# Tags that are opened and left unclosed are closed at the and of the line.	
def inline_format(line, tags, settings):
	global script_path

	op_bracket = settings["op_bracket"]
	ed_bracket = settings["ed_bracket"]
	intags = json.load(open(os.path.join(script_path, "tagsets", "inline_format.json"), "rb" ))
		
	res = re.match(r"(.*?)" + op_bracket + "([^ ]{1,3}) ([^" + op_bracket + "]+?)[" + ed_bracket + "|\n](.*)", line)
	while res:
		res_tag = res.group(2)
		if res.group(2) in intags:
			res_tag = intags[res_tag]
		line = res.group(1) + "<" + res_tag + ">" + res.group(3) + "</" + res_tag + ">" + res.group(4) + "\n"
		res = re.match(r"(.*?)" + op_bracket + "(.{1,3}) ([^" + op_bracket + "]+?)[" + ed_bracket + "|\n](.*)", line) # same as init search
	
	# Colored text - a bit more complicated that previous
	line = re.sub(r"" + op_bracket + "l=(.*?) (.*?)" + ed_bracket, r'<span style="color: \1">\2</span>', line)
	
	# Notes
	line = re.sub(r"^\{(\d+)\} - (.*$)", r'<span class="note">\1: \2</span>', line)
	line = re.sub(r"\{(\d+)\}", r"<sup><b>\1</b></sup>", line)

	# Links
	line = re.sub(r"" + op_bracket + "url=(.*?) (.*?)" + ed_bracket, r'<a href="\1">\2</a>', line)
	return line


# Add break line to any line that does not end with a tag.
# Imperfect, because it ignores also the lines that end only
# with a formatting end tag (like </i>), which may be many.
# And there's some magic in it too - adds <br> to images too
# if the condition doesnt include the empty line exclusion 
# 'and line.rstrip() != ""'.
# Also add break line if line contains only "|".
def add_br(line):
	if re.match(r"^\|$", line.strip()):
		line = "<br>\n"
	if not line.rstrip().endswith(">") and line.rstrip() != "":
		line = line.rstrip() + "<br>\n"
	return line

# Simple character replacements
def replacements(line):
	global script_path
	replace = json.load(open(os.path.join(script_path, "tagsets", "replace.json"), "rb" ))
	for key in replace:
		line = line.replace(key, replace[key])
	return line