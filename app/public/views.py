from flask import redirect, url_for

from . import public

@public.route('/')
def index():
    return redirect( url_for('auth.login') )

@public.route('/hola_mundo')
def hola_mundo():
    return "Hola Mundo"