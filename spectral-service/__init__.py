import os
import sys

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
            
        # Stores all data from splatalogue.csv as an array of dictionaries
        file = open('spectral-data/splatalogue.csv')
        lines = file.readlines()
        for i in range(len(lines)):
            words = lines[i].strip().split(':')
            for ii in range(len(words)):
                if(words[ii] == 'NULL'):
                    words[ii] = '0'
            lines[i] = make_dict(words)
            
        # If filter data has been POSTed, remove unwanted requests
        if request.method == 'POST':
            # While loops are used because the length of lines changes when
            # an item is removed
            if request.form['transition'] != '':
                i = 0
                while i < len(lines):
                    if (lines[i]['s_name_noparens']
                        != request.form['transition']):
                        del lines[i]
                    else:
                        i = i + 1
            if request.form['description'] != '':
                i = 0
                while i < len(lines):
                    if (lines[i]['chemical_name']
                        != request.form['description']):
                        del lines[i]
                    else:
                        i = i + 1
            if request.form['minrest'] != '':
                i = 0
                while i < len(lines):
                    if (lines[i]['orderedfreq']/1000 
                        < float(request.form['minrest'])):
                        del lines[i]
                    else:
                        i = i + 1
            if request.form['maxrest'] != '':
                i = 0
                while i < len(lines):
                    if (lines[i]['orderedfreq']/1000
                        > float(request.form['maxrest'])):
                        del lines[i]
                    else:
                        i = i + 1
            if request.form['minsky'] != '':
                i = 0
                while i < len(lines):
                    if (lines[i]['orderedfreq']/500 
                        < float(request.form['minsky'])):
                        del lines[i]
                    else:
                        i = i + 1
            if request.form['maxsky'] != '':
                i = 0
                while i < len(lines):
                    if (lines[i]['orderedfreq']/500
                        > float(request.form['maxsky'])):
                        del lines[i]
                    else:
                        i = i + 1
        
        # Return only the data needed for the current page
        page_length = 10
        page = int(page)
        return flask.jsonify(lines[(page-1) * page_length 
                                   : (page*page_length)])
            
    app.run(port=8080)
        
    return app
    
create_app()


