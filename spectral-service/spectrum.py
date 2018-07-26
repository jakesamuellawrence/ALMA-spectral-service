import flask
import werkzeug

bp = flask.Blueprint('spectrum', __name__)

cache = [[],[],[],[],[],[],[]]

@bp.route('/spectral/spectrum/<octile>', methods=('GET',))
def spectrum(octile):
    # Spectrum endpoint. Takes octile as an integer between 1 and 7
    # returns the data from the respectively numbered file in the form of 
    # List<List<double>>
    
    global cache
    
    octile = validate_octile(octile)
    
    if cache[octile-1] == []:
        cache[octile-1] = read_spectral_data('spectral-data/SKY.SPE000' 
                                              + str(octile) + '.trim')

    return flask.jsonify(cache[octile-1])
    
   
def validate_octile(octile):
    # Validate that octile is a real number between 1 and 7 inclusive
    try:
        octile = int(octile)
    except ValueError:
        werkzeug.exceptions.abort(422, 
                                  'octile could not be cast to int. ' 
                                  'octile must be an integer between 1 ' 
                                  'and 7 inclusive'
                                  )
    if int(octile) < 1 or int(octile) > 7:
        werkzeug.exceptions.abort(404, 
                                  'octile ' + str(octile) + " doesn't "
                                  "exist. octile must be between 1 and 7 "
                                  "inclusive")
    return octile
    
def read_spectral_data(path):
    file = open(path, 'r')
    lines = file.readlines()
    for i in range(len(lines)):
        lines[i] = lines[i].split()
        for ii in range(len(lines[i])):
            lines[i][ii] = float(lines[i][ii])
    return lines