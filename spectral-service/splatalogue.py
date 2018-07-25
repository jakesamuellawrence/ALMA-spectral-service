import math

import flask
from flask import request
import werkzeug

bp = flask.Blueprint('splatalogue', __name__)

cache = []

@bp.route('/spectral/splatalogue', methods=('POST',))
def splatalogue():                              
    # Splatalogue endpoint. Returns an array of objects made from 
    # splatalogue.csv. If filter form is POSTed it will send back
    # only the appropriate data
    
    global cache
    
    page = get_page()
    page_length = get_page_length()
    
    transition = get_transition()
    description = get_description()
    minrest = get_minrest()
    maxrest = get_maxrest()
    minsky = get_minsky()
    maxsky = get_maxsky()
    
    if cache == []:
        cache = read_splatalogue()
    
    filtered_data = get_filtered_data(cache, page, page_length,
                                      transition, description,
                                      minrest, maxrest,
                                      minsky, maxsky)
    
    return flask.jsonify(filtered_data)
    
def get_page():
    # Get page from URL arguments and validate it exists
    # and is a number
    page = request.args.get('page')
    if page is None:
        werkzeug.exceptions.abort(400,
                                  'A value for page was not sent when '
                                  'making the request. '
                                  'Format the request as so: '
                                  '/spectral/splatalogue?page=<page>'
                                  '&page_length=<page_length>')
    try:                            
        page = int(request.args.get('page'))
    except ValueError:
        werkzeug.exceptions.abort(422,
                                  'page could not be cast to int. '
                                  'Page must be a number')
    if page < 1:
        werkzeug.exceptions.abort(400,
                                  'page is out of range. page must be '
                                  'more than 0')
    return page

def get_page_length():
    # Get page_length from URL arguments and validate it exists
    # and is a number
    page_length = request.args.get('page_length')
    if page_length is None:
        werkzeug.exceptions.abort(400,
                                  'A value for page_length was not sent '
                                  'when making the request. '
                                  'Format the request as so: '
                                  '/spectral/splatalogue?page=<page>'
                                  '&page_length=<page_length>')
    try:
        page_length = int(page_length)
    except ValueError:
        werkzeug.exceptions.abort(422,
                                  'page_length could not be cast to an '
                                  'int. page_length must be an number')
    return page_length

def get_transition():
    # Gets the transition filter from the POSTed form
    transition = request.form['transition']
    return transition
 
def get_description():
    # Gets the description filter from the POSTed form
    description = request.form['description']
    return description
    
def get_minrest():
    # Gets the minrest filter from the POSTed form,
    # validates that it's a number, and casts it to a float
    minrest = request.form['minrest']
    if minrest != '':
        try:
            minrest = float(minrest)
        except ValueError:
            werkzeug.exceptions.abort(422,
                                      'minrest could not be cast to '
                                      'a float. minrest must be'
                                      'a real number')
    return minrest
    
def get_maxrest():
    # Gets the maxrest filter from the POSTed form,
    # validates that it's a number, and casts it to a float
    maxrest = request.form['maxrest']
    if maxrest != '':
        try:
            maxrest = float(maxrest)
        except ValueError:
            werkzeug.exceptions.abort(422,
                                      'maxrest could not be cast to '
                                      'a float. minrest must be'
                                      'a real number')
    return maxrest
    
def get_minsky():
    # Gets the minsky filter from the POSTed form,
    # validates that it's a number, and casts it to a float
    minsky = request.form['minsky']
    if minsky != '':
        try:
            minsky = float(minsky)
        except ValueError:
            werkzeug.exceptions.abort(422,
                                      'minsky could not be cast to '
                                      'a float. minrest must be'
                                      'a real number')
    return minsky
    
def get_maxsky():
    # Gets the maxsky filter from the POSTed form,
    # validates that it's a number, and casts it to a float
    maxsky = request.form['maxsky']
    if maxsky != '':
        try:
            maxsky = float(maxsky)
        except ValueError:
            werkzeug.exceptions.abort(422,
                                      'maxsky could not be cast to '
                                      'a float. minrest must be'
                                      'a real number')
    return maxsky
    
def read_splatalogue():
    # Read all of the data in from splatalogue.csv
    file = open('spectral-data/splatalogue.csv')
    lines = file.readlines()
    return lines
    
def get_filtered_data(lines, page, page_length, 
                      transition, description, 
                      minrest, maxrest,
                      minsky, maxsky):
    # Checks if each line matches the filters and returns only the only the
    # ones appropriate for the current page
    to_return = []
    i = 0
    found = 0
    while i < len(lines) and found < page*page_length:
        words = lines[i].strip().split(':')
        for ii in range(len(words)):
            if(words[ii] == 'NULL'):
                words[ii] = '0'
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
            found = found + 1
            if found > (page-1) * page_length:
                to_return.append(make_dict(words))
        i = i + 1
    
    if found <= (page-1) * page_length:
        max_pages = math.ceil(found/page_length)
        werkzeug.exceptions.abort(400,
                                  'page out of range. page must be '
                                  'between 1 and {0}'.format(max_pages))
    
    
    return to_return
    
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


    
    
    
    