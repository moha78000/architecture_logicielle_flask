from flask import Flask
from archilog import config
from archilog.views.web_ui import web_ui , register_error_handlers
from dotenv import load_dotenv
from archilog.views.api import api , spec


load_dotenv()


def create_app():
    app = Flask(__name__)
        
    
    # Enregistrement de la documentation Swagger avant l'enregistrement des routes
    spec.register(api)
   
   
    # Enregistrement des blueprints

    app.register_blueprint(web_ui)
    app.register_blueprint(api)
    register_error_handlers(app) 
    
    

    # Configuration de l'application
    app.config["SECRET_KEY"] = config.SECRET_KEY  

    
    
        
    return app
