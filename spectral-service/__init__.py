import flask
import flask_cors

import spectrum
import splatalogue


def create_app(test_config=None): 
    # Application Factory. Creates an instance of the Flask class and 
    # sets things up
    app = flask.Flask(__name__)
    flask_cors.CORS(app)
    
    app.register_blueprint(spectrum.bp)
    app.register_blueprint(splatalogue.bp)
            
    app.run(port=8080)
        
    return app
    
create_app()