# File operations for FML converter
import os, shutil, re, sys

script_path = os.path.dirname(os.path.abspath(sys.argv[0]))

def move_finished(input, output):
	global script_path

	# If the target directory doesn't exist, ask whether to create it.
	if not os.path.exists(os.path.dirname(output)):
		print "Target path doesnt exist. Create? (y/n)",
		
		if raw_input() == "y": 	# this could be done better.
			print "Creating directory {}".format(os.path.dirname(output))
			os.makedirs(os.path.dirname(output))
		
		else:
			print "Aborting, cleaning up tempfiles."
			clean_up()
			return False

	# If the target path is directory, it means the filename wasn't specified
	# therefore the input filename will be used.
	# Ext is 'html', because there is no suppoert for other formats yet. Should
	# be generalized.
	if os.path.isdir(output):
		output = os.path.join(output, os.path.basename(input) + ".html")

	# Copy the temporary output to desired destination
	print "Copying output to target path."
	shutil.copyfile(os.path.join(script_path, "tempfiles", "out_h.html"), output)
	
	# Copy images found in document to document's destination
	# Info about what images where found is stored in auxiliary file
	# (alongside headings and doc title and maybe other stuff in future)
	out_files = os.path.join(os.path.dirname(output), ".files")
	in_files = os.path.join(os.path.dirname(input), ".files")
	
	for line in open(os.path.join(script_path, "tempfiles", "auxf.fml")):
		if re.match(r"^img: .*", line):
			img = re.match(r"^img: (.*)", line).group(1)
			
			# If in dest folder is not .files/, create it (that's where
			# images are linked to)
			if not os.path.exists(out_files):
				os.makedirs(out_files)

			# Skip the existing files
			if not os.path.exists(os.path.join(out_files, img)):
				if os.path.exists(os.path.join(in_files, img)):
					print "Copying file {}".format(os.path.join(in_files, img))
					shutil.copyfile(os.path.join(in_files, img), os.path.join(out_files, img))
				else:
					print "File {} doesn't exist.".format(os.path.join(in_files, img))
			else:
				print "File {} already exists, ignoring.".format(os.path.join(out_files, img))
	print "Operation completed."
	clean_up()
	return True

def clean_up():
	# Clean up the tempfiles
	for file in os.listdir(os.path.join(script_path, "tempfiles")):
		if os.path.isfile(os.path.join("tempfiles", file)):
			print "Removing {}".format(os.path.join(script_path, "tempfiles", file))
			try:
				os.remove(os.path.join("tempfiles", file))
			except:
				print "Failed to remove {}".format(os.path.join(script_path, "tempfiles", file))