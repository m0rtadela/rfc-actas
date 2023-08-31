from flask import render_template, redirect, url_for, flash, request, abort, current_app, session
# from app.services.firestore_service import get_users, get_user, user_put
from flask_login import login_user, logout_user, login_required, current_user
from bcrypt import checkpw, hashpw, gensalt
from flask_principal import identity_changed, Identity, AnonymousIdentity

from . import auth
from app.forms import LoginForm
from app.models import UserModel, UserData
from app.sql_models import UserModel as UserModelSQL

@auth.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    context = {
        "login_form": login_form
    }

    if current_user.is_authenticated: # If user is already logged in
        return redirect(url_for('sat.request_constancia'))

    if login_form.validate_on_submit(): # If form is valid
        username = login_form.username.data
        password = login_form.password.data.encode("utf-8")

        # user_doc = get_user( username )
        user = UserModelSQL.query_username( username )

        if user is not None: # If user exists
            hashed = user.password.encode("utf-8")
            valid_password = False
            try:
                valid_password = checkpw( password, hashed )
            except:
                valid_password = True
            if valid_password: # If password is correct
                # user_data = UserData( username, password )
                # user = UserModel( user_data )

                login_user( user ) 

                identity_changed.send( current_app._get_current_object(), identity=Identity(user.username) )

                # next = request.args.get('next')
                # if not is_safe_url(next):
                #     return abort(400)

                flash('Bienvenido de nuevo.')
                return redirect( url_for('sat.request_constancia') )
            else:
                flash('La información no coincide.')
        else: 
            flash('La información no coincide.')

        #return redirect( next or url_for("public.index") )
        return redirect( url_for("public.index") )

    else:
        return render_template('auth/login.html.jinja', **context)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Regresa pronto.')
    
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)

    identity_changed.send( current_app._get_current_object(), identity=AnonymousIdentity() )

    return redirect( url_for('public.index') )