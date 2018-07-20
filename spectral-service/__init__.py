import os
import flask
import sys
import werkzeug

def create_app(test_config=None): # Application Factory. Creates an instance of the Flask class and sets things up
	app = flask.Flask(__name__) # __name__ is the name of the current Python module
	
	# Splatalogue endpoint. returns an array of objects made from splatalogue.csv
	@app.route("/splatalogue/<name>,<minfreq>,<maxfreq>", methods=("GET",))
	def splatalogue(name, minfreq, maxfreq):
		def makeDict(data):
			# line_id : species_id : s_name_noparens : chemical_name : 
			# orderedfreq : resolved_QNs : sijmu2 :
			# lovas_int : E_up_K : planet : ism_hotcore : ism_diffusecloud : 
			# comet : ism_darkcloud : extragalactic :
			# agb_ppn_pn : top20
			return(
				{
					"line_id" 			: int(data[0]),
					"species_id"		: int(data[1]),
					"s_name_noparens" 	: str(data[2]),
					"chemical_name"		: str(data[3]),
					"ordered_freq"		: float(data[4]),
					"resolved_QNs"		: str(data[5]),
					"sijmu2"			: float(data[6]),
					"lovas_int"			: str(data[7]),
					"E_up_K"			: float(data[8]),
					"planet"			: bool(int(data[9])),
					"ism_hotcore"		: bool(int(data[10])),
					"ism_diffusecloud"	: bool(int(data[11])),
					"comet"				: bool(int(data[12])),
					"ism_darkcloud"		: bool(int(data[13])),
					"extragalactic"		: bool(int(data[14])),
					"agb_ppn_pn"		: bool(int(data[15])),
					"top20"				: int(data[16])
				}
			)
			
		to_return = []
		
		file = open("spectral-data/splatalogue.csv")
		lines = file.readlines() # lines is now an array of strings
		for i in range(len(lines)):
			words = lines[i].split(":") # Split(delimiter) separates the string and returns an array of strings
			for ii in range(len(words)):
				if(words[ii] == "NULL"):
					words[ii] = "0"
			lines[i] = makeDict(words)
		
		# lines is now an array of dictionaries
		
		# If minfreq and maxfreq are empty, set them to values which will always be true
		if minfreq == "empty":
			minfreq = 0
		if maxfreq == "empty":
			maxfreq = sys.maxsize # Maximum size for an integer without being automatically promoted to a long
		
		# apply filters to only return appropriate data
		for line in lines:
			if(name == "empty"):
				if(line["ordered_freq"] > float(minfreq) and line["ordered_freq"] < float(maxfreq)):
					to_return.append(line)
			else:
				if((line["chemical_name"].lower() == name.lower() or line["s_name_noparens"] == name) and (line["ordered_freq"] > float(minfreq) and line["ordered_freq"] < float(maxfreq))):
					to_return.append(line)
		# Check whether any results were found
		if(to_return == []):
			werkzeug.exceptions.abort(404, "No data matching filters")
		else:
			return(flask.jsonify(to_return))
	return(app)