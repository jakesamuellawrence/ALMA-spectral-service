import math

import flask
from flask import request
import werkzeug
from astroquery.splatalogue import Splatalogue
from astropy import units as u

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
    
    description = get_description()
    minrest = get_minrest()
    maxrest = get_maxrest()
    
    filtered_data = get_filtered_data(page, page_length,
                                      description,
                                      minrest, maxrest)
    
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
 
def get_description():
    # Gets the description filter from the POSTed form
    description = request.form['description']
    return description
    
def get_minrest():
    # Gets the minrest filter from the POSTed form,
    # validates that it's a number, and casts it to a float
    minrest = request.form['minrest']
    if minrest == '':
        werkzeug.exceptions.abort(400,
                                  'No value for minrest. minrest field '
                                  'must not be empty')
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
    if maxrest == '':
        werkzeug.exceptions.abort(400,
                                  'No value for maxrest. maxrest field must '
                                  'not be empty')
    try:
        maxrest = float(maxrest)
    except ValueError:
        werkzeug.exceptions.abort(422,
                                  'maxrest could not be cast to '
                                  'a float. maxrest must be'
                                  'a real number')
    return maxrest

def get_filtered_data(page, page_length,
                      description,
                      minrest, maxrest):
    # Gets the appropriate data from the splatalogue using the filters
    # and returns only the ones needed for the current page
    try:
        splatalogue_data = Splatalogue.query_lines(minrest*u.GHz,
                                                   maxrest*u.GHz,
                                                   chemical_name=description)
    except ValueError:
        return "No matching data found"
    if page > math.ceil(len(splatalogue_data)/page_length):
        werkzeug.exceptions.abort(400,
                                  'page out of bounds. Page must be between '
                                  '0 and '
                                  '{0}'.format(math.ceil(len(splatalogue_data)
                                                         /page_length)))
    to_return = []
    for i in range(len(splatalogue_data)):
        to_return.append(make_dict(splatalogue_data[i]))
    return to_return[(page-1) * page_length : page * page_length]
    
def make_dict(data):
    return({
        's_name_noparens' : str(data['Species']),
        'chemical_name' : str(data['Chemical Name']),
        'orderedfreq' : str(data['Freq-GHz(rest frame,redshifted)']),
        'resolved_QNs' : str(data['Resolved QNs']),
        'lovas_int' : str(data['Lovas/AST Intensity']),
        'E_up_K' : str(data['E_U (K)'])
    })
   