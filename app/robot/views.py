from flask import render_template, send_file, request, redirect, url_for, flash, send_from_directory
from flask_login import login_required, current_user
from time import sleep
import pandas as pd
from numpy import NaN
from io import StringIO, BytesIO
import zipfile



from app.forms import SatLoginForm, ConstanciaForm, CSVForm, TestForm
from .SAT_robot import SatRobot
from . import robot
from .SAT_robot import SatRobot
from flask_cors import cross_origin


sat_robot = SatRobot()

# @robot.route('/login', methods=['GET', 'POST'])
# @login_required
# def login():
#     global cer, key
#     sat_login_form = SatLoginForm()
#     context ={
#         'sat_login_form': sat_login_form,
#         "logged": sat_robot.logged,
#         "usuario": current_user
#     }

#     if sat_login_form.validate_on_submit():

#         cer = BytesIO()
#         key = BytesIO()

#         sat_login_form.certificate.data.save( cer )
#         sat_login_form.private_key.data.save( key )
#         pswd = sat_login_form.password.data
        
#         login_result = sat_robot.login( pswd )

#         cer = None
#         key = None

#         if type( login_result ) == str:
#             flash( login_result, "error" )
#             return redirect( url_for( 'robot.login' ) )

#         sat_robot.get_cookies()

#         flash("Sesion iniciada en SAT")
#         sat_robot.logged = True
#         sat_robot.run_get_constancia()
#         sat_robot.run_interval_get_constancia()
        
#         return redirect(url_for('sat.request_constancia'))

#     # logged = sat_robot.validate_if_logged()

#     # if logged == "SESSION_OK":
#     #     context["logged"] = True
#     # if logged == "ACTAS_NO_SESSION":
#     #     sat_robot.get_cookies()
#     #     return redirect(url_for('robot.login'))
    
#     return render_template('sat/login.html.jinja', **context)

@robot.route('/nuke')
def nuke():
    global sat_robot
    app = sat_robot.quit()
    sat_robot = SatRobot()
    sat_robot.app = app
    return redirect(url_for('sat.request_constancia'))



            # memory_file = BytesIO()

            # # SITE_ROOT = os.path.realpath( os.path.dirname( os.path.dirname(__file__)))
            # with zipfile.ZipFile( memory_file , "w") as zip:
            #     for constancia in constancias:
            #         if constancia["constancia"].state is not "DESCARGADO":
            #             continue
            #         try:
            #             # file_path = os.path.join(SITE_ROOT, 'static', "files", "downloads", file)
            #             file_path = os.path.join( temp_directory.name, constancia["file_name"] )
            #             zip.write( file_path, arcname=constancia["file_name"] )
            #         except:
            #             constancia["constancia"].state = "ERROR"

            # memory_file.seek(0)
            # temp_directory.cleanup()
    

@robot.route('/')
@login_required
def index():
    return sat_robot.hola_mundo()

@robot.route('/cer')
@cross_origin()
def get_cer():
    # return send_from_directory("static", "files/cer.cer", as_attachment=True)
    cer = sat_robot.get_cer()
    if cer:
        print("cer", cer, type(cer))
        cer.seek(0)
        return send_file(cer, as_attachment=False, mimetype='application/pkix-cert', download_name='certificado.cer')
    else:
        return "No hay certificado"


@robot.route('/key')
@cross_origin()
def get_key():
    # return send_from_directory("static", "files/key.key", as_attachment=True)
    key = sat_robot.get_key()
    if key:
        print( "key", key, type(key) )
        key.seek(0)
        return send_file(key, as_attachment=False, mimetype='application/pkcs8', download_name='llave.key')
    else:
        return "No hay llave"

# @robot.route('/sat_close_session')
# @login_required
# def sat_close_session():
#     sat_robot.logged = False
#     sat_robot.remove_job()
#     try:
#         sat_robot.logout()
#     except:
#         pass
#     return redirect(url_for('sat.login'))

@robot.route('/start_search')
@login_required
def start_search():
    sat_robot.run_get_constancia()
    return redirect(url_for('sat.request_constancia'))