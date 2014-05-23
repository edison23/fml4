# Syntaxed code
import json, re, cgi, os, sys

def main(parameters):
	script_path = os.path.dirname(os.path.abspath(sys.argv[0]))

	f_in, f_out, _, settings = parameters
	# Open dictionary with keywords
	keywords = json.load(open(os.path.join(script_path, "tagsets", "syntax_hl.json"), "rb" ))
	
	op_bracket = settings["op_bracket"]
	ed_bracket = settings["ed_bracket"]

	active = 0
	syntax = 0
	
	for line in f_in:
		line = line.rstrip() + "\n"
		line = line.decode("utf-8")
					
		# If opening tag found, activate syntax processing
		if re.match(r"^" + op_bracket +"cs?$", line):
			line = cgi.escape(line)

			# If the tag was cs, switch on syntax highlighting
			if line == op_bracket.strip("\\") + "cs\n":
				syntax = 1
			
			line = "<noprocess>\n<pre>\n"
			active = 1
		
		# Closing tag found
		elif re.match(r"^" + ed_bracket +"$", line) and active == 1:
			line = cgi.escape(line)
			
			line = "</pre>\n</noprocess>\n"
			active = 0
			syntax = 0

		# If the line is within the the code, test each word and if it's in keywords, 
		# highlight it according to definition
		elif active == 1 and syntax == 1:
			line = cgi.escape(line)

			for word in keywords:
				# If the word is of type "block" (typically quotes), ending tag will be searched for and HLed the whole text
				if keywords[word]["type"] == "block":
					line = re.sub(
						word + r"(.*?)[" + keywords[word]["end"] + "\n]", 
						'<font color="' + keywords[word]['color'] + '"><' + keywords[word]["style"] +">" + word + r'\1' + keywords[word]["end"] + '</' + keywords[word]["style"] + '></font> ',
						line)
					
					# If the "endtag" was end of line, it was lost in substitution -> add it
					if not line.endswith("\n"):
						line += "\n"
				
				# "keyword" type is simply HLed and nothing else happens
				elif keywords[word]["type"] == "keyword":
					line = line.replace(word, '<font color="' + keywords[word]["color"] + '"><' + keywords[word]["style"] + '>' + word + '</' + keywords[word]["style"] + '></font>')
		
		# If code is active, only escape lines
		elif active == 1:
			line = cgi.escape(line)
		
		# Very very very very shitty rules for escaping characters []|... (btw, why is formating broken by pipe?!)
		# Also, it obviously doesnt work as reported by ximara
		line = line.replace("\[", u"\x10").replace("\]", u"\x11").replace("\|", u"\x12")

		f_out.write(line.encode("utf-8"))
