from flask import render_template, redirect, url_for, send_file, request, flash
from flask_login import login_required, current_user
import pandas as pd
from io import BytesIO, StringIO
from numpy import NaN
from datetime import datetime, timedelta
from os import environ


from . import sat
from app.forms import SatLoginForm, ConstanciaForm, CSVForm, FilterConstanciasForm
from app.models import Constancia
from app.services.firestore_service import get_constancias, constancia_add, constancias_add, download_file
from app.sql_models import ConstanciasModel
from app.services.permissions import admin_permission, user_permission

@sat.route("/my-constancias", methods=['GET', 'POST'])
@login_required
def my_constancias():
    page = request.args.get( "page", 1, type=int )
    owner = request.args.get( "owner", current_user, type=str ) if admin_permission.can() else current_user.username
    start_date = request.args.get( "start_date", None, type=str )
    end_date = request.args.get( "end_date", None, type=str )
    state = request.args.get( "state", None, type=str )
    tipo = request.args.get( "tipo", None, type=str )
    order_by = request.args.get( "order_by", "date_desc", type=str )
    type_search = request.form.get('type-search')
    if type_search == None:
        type_search = 0
    else:
        type_search = int(type_search)
    download = request.args.get( "download", None, type=str )

    if download == "Descargar":
        constancias = ConstanciasModel.query_by_filters(
            owner=owner,
            date_range=(start_date, end_date),
            state=state,
            tipo=tipo,
            page=page,
            order_by=order_by,
            pagination=False
        )
        constancias_df = {
            "ASESOR": [],
            "NOMBRE": [],
            "CURP/RFC": [],
            "TIPO": [],
            "FECHA": [],
        }
        for constancia in constancias:
            constancias_df["ASESOR"].append( current_user.username )
            constancias_df["CURP/RFC"].append( constancia.rfc if constancia.rfc else constancia.curp )
            constancias_df["NOMBRE"].append( constancia.name )
            constancias_df["TIPO"].append( "Fisica" if constancia.tipo == '1' else "Moral" )
            constancias_df["FECHA"].append( (constancia.date - timedelta( hours=6 )).strftime('%d/%m/%Y %H:%M:%S') )
        
        constancias_csv = BytesIO()
        constancias_df = pd.DataFrame( constancias_df )
        # constancias_df.to_csv( constancias_csv, index=False )
        excel = pd.ExcelWriter( constancias_csv, engine='xlsxwriter' )
        with excel as writer:
            constancias_df.to_excel( writer, sheet_name="Constancias", index=False )
            writer.save()
            writer.close()
        constancias_csv.seek(0)
        return send_file( constancias_csv, download_name="Constancias.xlsx", as_attachment=False )
    
    if request.method == 'POST':
        query_search = request.form.get('query-search')
        pagination = ConstanciasModel.query_by_new_filters(
            type=type_search,
            query=query_search,
            pagination=True
        )
        type_search = 2
    else:
        pagination = ConstanciasModel.query_by_filters(
            owner=owner,
            date_range=(start_date, end_date),
            state=state,
            tipo=tipo,
            page=page,
            order_by=order_by
        )

    precio = environ.get("COSTO_CONSTANCIA")
    precio = float(precio) if precio else 0
    context = {
        'pagination': pagination,
        "costo_u": precio,
        "usuario": current_user,
        "diferencia": timedelta( hours=6 ),
        "filter_form": FilterConstanciasForm(
            owner=owner,
            start_date=datetime.strptime(start_date, r"%Y-%m-%d") if start_date else None, #! corregir, tiene una diferencia de 6 horas
            end_date=datetime.strptime(end_date, r"%Y-%m-%d") if end_date else None,       #! corregir, tiene una diferencia de 6 horas
            state=state,
            tipo=tipo,
            page=page,
            order_by=order_by
        ),
        "type_search": type_search
    }
    return render_template('sat/my_constancias.html.jinja', **context)

# @sat.route("/download-constancias", methods=['GET'])
# @login_required
# def download_constancias():
#     owner = request.args.get( "owner", current_user, type=str ) if admin_permission.can() else current_user.username
#     start_date = request.args.get( "start_date", None, type=str )
#     end_date = request.args.get( "end_date", None, type=str )
#     state = request.args.get( "state", None, type=str )
#     tipo = request.args.get( "tipo", None, type=str )
#     order_by = request.args.get( "order_by", "date_desc", type=str )

#     constancias = ConstanciasModel.query_all_by_owner( current_user.username )
#     constancias_df = {
#         "RFC": [],
#         "CURP": [],
#         # "tipo": [],
#         # "status": [],
#         "Fecha": [],
#         "owner": []
#     }
#     for constancia in constancias:
#         constancias_df["RFC"].append( constancia.rfc )
#         constancias_df["CURP"].append( constancia.curp )
#         constancias_df["Fecha"].append( constancia.date )
#         constancias_df["owner"].append( current_user.username )

#     constancias_csv = BytesIO()
#     constancias_df = pd.DataFrame( constancias_df )
#     constancias_df.to_csv( constancias_csv, index=False )
#     constancias_csv.seek(0)
#     return send_file( constancias_csv, download_name="constancias.csv", as_attachment=False )


@sat.route("/request_constancia", methods=['GET', 'POST'])
@login_required
def request_constancia():
    constancia_form = ConstanciaForm()
    context = {
        # 'constancia_form': ConstanciaForm(formdata=None)
        'constancia_form': ConstanciaForm( tipo=request.args.get('tipo'), rfc=request.args.get('rfc'), curp=request.args.get('curp') ),
        "usuario": current_user
    }

    if constancia_form.validate_on_submit():
        # constancia = Constancia(
        #     rfc=constancia_form.rfc.data.upper(),
        #     curp=constancia_form.curp.data.upper(),
            # name=constancia_form.name.data.capitalize(),
            # first_last_name=constancia_form.first_last_name.data.capitalize(),
            # second_last_name=constancia_form.second_last_name.data.capitalize(),
        #     tipo=constancia_form.tipo.data,
        #     owner_id=current_user.id,
        #     state="PENDING"
        # )
        constancia = ConstanciasModel(
            rfc=constancia_form.rfc.data.upper(),
            curp=constancia_form.curp.data.upper(),
            # name=constancia_form.name.data.capitalize(),
            # first_last_name=constancia_form.first_last_name.data.capitalize(),
            # second_last_name=constancia_form.second_last_name.data.capitalize(),
            tipo=constancia_form.tipo.data,
            owner_id=current_user.username,
            # grupo=constancia_form.grupo.data, #* descomentar cuando se agregue el campo grupo
            state="PENDING",
            date=datetime.now()
        )

        if constancia_form.tipo.data == "1":
            if not (constancia.rfc or constancia.curp):
                flash("Debe ingresar al menos un RFC o CURP", "error")
                return redirect(url_for('sat.request_constancia'))
        else:
            if not constancia.rfc:
                flash("Debe ingresar un RFC", "error")
                return redirect(url_for('sat.request_constancia'))

        # constancia_add( constancia )
        print("Creando request")
        constancia.save_to_db()
        flash("Constancia agregada correctamente")
        # context['constancia_form'] = ConstanciaForm(formdata=None)
        return redirect(url_for('robot.start_search'))
    else:
        if request.method != "GET":
            flash("Error al agregar constancia", "error")
        return render_template('sat/constancia_form.html.jinja', **context)
    

@sat.route("/request_constancia_csv", methods=['GET', 'POST'])
@login_required
def request_constancia_csv():
    csv_form = CSVForm()

    context = {
        'csv_form': csv_form,
        "usuario": current_user
    }
    
    if csv_form.validate_on_submit():
        
        file = csv_form.csv_file.data
        if file:
            stream = StringIO( file.stream.read().decode("UTF8"), newline=None )
            csv = pd.read_csv( stream ).dropna( how="all" ).replace(NaN, "")\
                    .replace("fisica", "1").replace("moral", "2")

            if csv.empty:
                flash("El archivo no contiene datos", "error")
                return redirect(url_for('sat.request_constancia_csv'))

            if "RFC" not in csv.columns:
                flash("El archivo no contiene la columna RFC", "error")
                return redirect(url_for('sat.request_constancia_csv'))

            if "CURP" not in csv.columns:
                flash("El archivo no contiene la columna CURP", "error")
                return redirect(url_for('sat.request_constancia_csv'))

            if "TIPO" not in csv.columns:
                flash("El archivo no contiene la columna TIPO", "error")
                return redirect(url_for('sat.request_constancia_csv'))

            if "GRUPO" not in csv.columns:
                flash("El archivo no contiene la columna GRUPO", "error")
                return redirect(url_for('sat.request_constancia_csv'))

            if not all( [x in ["1", "2"] for x in csv["TIPO"].unique()] ):
                flash("El archivo contiene valores incorrectos o vacios en la columna TIPO", "error")
                return redirect(url_for('sat.request_constancia_csv'))

            #* descomentar cuando se agregue el campo grupo
            # if not all( [x in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"] for x in csv["GRUPO"].unique()] ):
            #     flash("El archivo contiene valores incorrectos o vacios en la columna GRUPO", "error")
            #     return redirect(url_for('sat.request_constancia_csv'))

            conditions = (csv['CURP'].str.len() != 18) | (csv['RFC'].str.len() > 13 ) | (csv['RFC'].str.len() < 12 ) & (csv['RFC'].str.len() > 0) 
            if not csv.loc[conditions].empty:
                flash("El archivo contiene RFC o CURP incorrectos", "error")
                return redirect(url_for('sat.request_constancia_csv'))


            # csv1 = csv.drop_duplicates( subset=['Nombre', 'Apellido Paterno', 'Apellido Materno'] )
            csv2 = csv.drop_duplicates( subset=['RFC', "TIPO"] )
            csv3 = csv.drop_duplicates( subset=['CURP', "TIPO"] )
            csv = pd.concat( [csv2, csv3] ).drop_duplicates()

            constancias = []

            for index, row in csv.iterrows():
                # constancia = Constancia(
                #     rfc=row["RFC"].upper(),
                #     curp=row["CURP"].upper(),
                #     # name=constancia_form.name.data.capitalize(),
                #     # first_last_name=constancia_form.first_last_name.data.capitalize(),
                #     # second_last_name=constancia_form.second_last_name.data.capitalize(),
                #     tipo=row["TIPO"].upper(),
                #     owner_id=current_user.id,
                #     state="PENDING"
                # )
                constancia = ConstanciasModel(
                    rfc=row["RFC"].upper(),
                    curp=row["CURP"].upper(),
                    # name=constancia_form.name.data.capitalize(),
                    # first_last_name=constancia_form.first_last_name.data.capitalize(),
                    # second_last_name=constancia_form.second_last_name.data.capitalize(),
                    grupo=row["GRUPO"],
                    tipo=row["TIPO"],
                    owner_id=current_user.username,
                    state="PENDING",
                    date=datetime.now()
                )
                constancias.append( constancia )
            # constancias_add( constancias )
            ConstanciasModel.save_multiple_to_db( constancias ) 
            flash("Se han agregado las constancias")
        else: 
            flash("No se ha seleccionado un archivo")
    return render_template('sat/constancias_csv.html.jinja', **context )

@sat.route("/download_constancia", methods=['POST'])
@login_required
def download_constancia():
    if request.form.get( 'file_url' ):
        file_url = request.form.get( 'file_url' )
        file, name = download_file(file_url)
        file.seek(0)
        return send_file( file, download_name=name, as_attachment=True )