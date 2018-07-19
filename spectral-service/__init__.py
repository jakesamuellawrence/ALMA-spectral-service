import os
import flask

def create_app(test_config=None): # Application Factory. Creates an instance of the Flask class and sets things up
	app = flask.Flask(__name__) # __name__ is the name of the current Python module

	# Spectrum endpoint. Takes octile as an integer between 1 and 7 returns the data from the respectively numbered file in the form of List<List<double>>
	@app.route("/spectrum/<octile>")
	def test(octile):
		file = open("spectral-data/SKY.SPE000" + octile + ".trim", "r")
		#return("spectral-data/SKY.SPE000" + octile + ".trim" + file.read())
		to_return = [] # to_return is array of arrays, to be filled and then returned
		lines = file.readlines() # lines is array of strings, each string being a line in the file
		for line in lines:
			words = line.split() # Separates line into smaller strings with space as the delimiter
			for i in range(len(words)):
				words[i] = float(words[i])
			to_return.append(words)
		return(flask.jsonify(to_return))

	return(app)