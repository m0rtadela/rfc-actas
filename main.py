from flask import redirect, url_for
from app import create_app

app = create_app()

# waitress-serve --listen=127.0.0.1:5000 main:app 
#pyinstaller --onefile --paths=./venv/Lib/site-packages --add-data './app/templates;templates' --add-data './app/static;static' --add-data "venv\Lib\site-packages\flask_bootstrap\templates\bootstrap;/templates/bootstrap" .\main.py
#heroku git:remote -a rfc-actas 
#git push heroku master

if __name__ == "__main__":
    app.run()