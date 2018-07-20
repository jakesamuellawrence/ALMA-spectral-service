import os
import flask

def create_app(test_config=None): # Application Factory. Creates an instance of the Flask class and sets things up
	app = flask.Flask(__name__) # __name__ is the name of the current Python module
	
	# Splatalogue endpoint. returns an array of objects made from splatalogue.csv
	@app.route("/splatalogue", methods=("GET",))
	def splatalogue():
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
		file = open("spectral-data/splatalogue.csv")
		lines = file.readlines()
		for i in range(len(lines)):
			words = lines[i].split(":") # Split(delimiter) separates the string and returns an array of strings
			for ii in range(len(words)):
				if(words[ii] == "NULL"):
					words[ii] = "0"
			lines[i] = makeDict(words)
		return(flask.jsonify(lines))
	return(app)