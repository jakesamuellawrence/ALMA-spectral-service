import os
import sys
import math

import flask
from flask import request
import flask_cors
import werkzeug


def create_app(test_config=None): 
    # Application Factory. Creates an instance of the Flask class and 
    # sets things up
    app = flask.Flask(__name__)
    flask_cors.CORS(app)

    @app.route('/spectral/spectrum/<octile>', methods=('GET',))
    def spectrum(octile):
        # Spectrum endpoint. Takes octile as an integer between 1 and 7
        # returns the data from the respectively numbered file in the form of 
        # List<List<double>>
        # Validate that octile is a real number between 1 and 7 inclusive
        try:
            int(octile)
        except ValueError:
            werkzeug.exceptions.abort(422, 
                                      'octile could not be cast to int. ' 
                                      'octile must be an integer between 1' 
                                      'and 7 inclusive'
                                      )
        if int(octile) < 1 or int(octile) > 7:
            werkzeug.exceptions.abort(404, 
                                      'octile ' + str(octile) + " doesn't "
                                      "exist. octile must be between 1 and 7 "
                                      "inclusive")
        file = open('spectral-data/SKY.SPE000' + octile + '.trim', 'r')
        to_return = [] 
        lines = file.readlines()
        for line in lines:
            words = line.split()
            for i in range(len(words)):
                words[i] = float(words[i])
            to_return.append(words)
        return flask.jsonify(to_return)
    
    @app.route('/spectral/splatalogue/<page>', methods=('GET', 'POST'))
    def splatalogue(page):
        # Splatalogue endpoint. Returns an array of objects made from 
        # splatalogue.csv. If filter form is POSTed it will send back
        # only the appropriate data
        def make_dict(data):
            # line_id : species_id : s_name_noparens : chemical_name : 
            # orderedfreq : resolved_QNs : sijmu2 :
            # lovas_int : E_up_K : planet : ism_hotcore : ism_diffusecloud : 
            # comet : ism_darkcloud : extragalactic :
            # agb_ppn_pn : top20
            return(
                {
                    'line_id' : int(data[0]),
                    'species_id' : int(data[1]),
                    's_name_noparens' : str(data[2]),  # Transition
                    'chemical_name' : str(data[3]),  # Description
                    'orderedfreq' : float(data[4]),  # Skyfreq*500
                    'resolved_QNs' : str(data[5]),
                    'sijmu2' : float(data[6]),
                    'lovas_int' : str(data[7]),
                    'E_up_K' : float(data[8]),
                    'planet' : bool(int(data[9])),
                    'ism_hotcore' : bool(int(data[10])),
                    'ism_diffusecloud' : bool(int(data[11])),
                    'comet' : bool(int(data[12])),
                    'ism_darkcloud' : bool(int(data[13])),
                    'extragalactic' : bool(int(data[14])),
                    'agb_ppn_pn' : bool(int(data[15])),
                    'top20' : int(data[16])
                }
            )
        
        # Get filter inputs from the request
        transition = request.form['transition']
        description = request.form['description']
        minrest = request.form['minrest']
        maxrest = request.form['maxrest']
        minsky = request.form['minsky']
        maxsky = request.form['maxsky']
        
        # Validate the frequency filter inputs and cast them to floats
        if minrest != '':
            try:
                minrest = float(minrest)
            except ValueError:
                werkzeug.exceptions.abort(422,
                                          'minrest could not be cast to '
                                          'a float. minrest must be'
                                          'a real number')
        if maxrest != '':
            try:
                maxrest = float(maxrest)
            except ValueError:
                werkzeug.exceptions.abort(422,
                                          'maxrest could not be cast to '
                                          'a float. minrest must be'
                                          'a real number')
        if minsky != '':
            try:
                minsky = float(minsky)
            except ValueError:
                werkzeug.exceptions.abort(422,
                                          'minsky could not be cast to '
                                          'a float. minrest must be'
                                          'a real number')
        if maxsky != '':
            try:
                maxsky = float(maxsky)
            except ValueError:
                werkzeug.exceptions.abort(422,
                                          'maxsky could not be cast to '
                                          'a float. minrest must be'
                                          'a real number')
        
                                          
        # Stores all data from splatalogue.csv as an array of dictionaries
        # if it matches the filters
        to_return = []
        file = open('spectral-data/splatalogue.csv')
        lines = file.readlines()
        for i in range(len(lines)):
            words = lines[i].strip().split(':')
            for ii in range(len(words)):
                if(words[ii] == 'NULL'):
                    words[ii] = '0'
            # Check if it matches filters
            if (
               (transition == '' or transition.lower() == words[2].lower())
               and
               (description == '' or description.lower() == words[3].lower())
               and
               (minrest == '' or float(words[4])/1000 > minrest)
               and
               (maxrest == '' or float(words[4])/1000 < maxrest)
               and
               (minsky == '' or float(words[4])/500 > minsky)
               and
               (maxsky == '' or float(words[4])/500 < maxsky)
               ):               
                to_return.append(make_dict(words))
         
        page_length = 10
        # check that page is an int and is appropriate for the amount of 
        # data returned
        try:
            page = int(page)
        except ValueError:
            werkzeug.exceptions.abort(422,
                                      'page could not be cast to int. Page '
                                      'must be a number.')
        max_pages = math.ceil(len(to_return)/page_length)                              
        if page > max_pages or page < 1:
            werkzeug.exceptions.abort(400,
                                      'Page is outwith range of available '
                                      'pages. Page must be between 1 and '
                                      '{0}'.format(max_pages))
 
        # Return only the data needed for the current page
        return flask.jsonify(to_return[(page-1) * page_length 
                                   : (page*page_length)])
            
    app.run(port=8080)
        
    return app
    
create_app()


