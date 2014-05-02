# Tables

import json, re

def main(parameters):
	f_in, f_out, _, settings = parameters
	table_active = False 	# indicator whether line is within table
	heading = True 	# Indicator line is first in table
	op_bracket = settings["op_bracket"]
	ed_bracket = settings["ed_bracket"]	
	for line in f_in:
		line = line.decode("utf-8")
		
		# Opening tag found
		if re.match(r"^" + op_bracket + "t", line):
			table_active = True
			
			# Find parameters of table (columns width)
			params = re.findall(r"-(\d+[px%]+)", line)
			
			# Redundant parameters of table (widths of columns) left here for future 
			# use (probably for other formats)
			cols = ""
			for i in xrange(len(params)):
				cols += "col" + str(i) + "=\"" + str(params[i]) + "\" "
			line = "<table " + cols + ">\n"
		
		# Closing tag found
		elif re.match(r"^" + ed_bracket + "$", line) and table_active:
			table_active = False
			heading = True
			line = "</table>\n"
		
		elif table_active:
			# Split the line by tabs to get values of columns
			columns = line.rstrip().split("\t")
			
			# If the line is first, loop thru columns "manually" and assing widths taken
			# from the head of the table (if there are any)
			if heading:
				line = "\t"
				
				for i in xrange(len(columns)):
					if i < len(params):
						width = params[i]
					else:
						width = ""
					line += "<th width=\"" + str(width) + "\">" + columns[i] + "</th>"
				
				line += "\n"
				heading = False
			
			# Ordinary table line
			else:
				line = "\t<tr><td>" + "</td><td>".join(columns) + "</td></tr>\n"
			
		f_out.write(line.encode("utf-8"))
		