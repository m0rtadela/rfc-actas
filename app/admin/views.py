from flask import render_template, redirect, flash, url_for
from flask_login import login_required, current_user
from bcrypt import checkpw, hashpw, gensalt

from . import admin
from app.forms import CreateUserForm, ChangeUserRoleForm
from app.sql_models import UserModel
from app.services.permissions import admin_permission

@admin.before_request
@login_required
@admin_permission.require()
def before_request():
    pass

@admin.route('/create_usr', methods=['GET', 'POST'])
@login_required
def create_usr():
    create_usr_form = CreateUserForm()

    if create_usr_form.validate_on_submit():
        username = create_usr_form.username.data
        password = create_usr_form.password.data

        salt = gensalt()
        hashed_password = hashpw( password.encode('utf-8'), salt )

        print( len(hashed_password) )
        try:
            UserModel( username=username, password=hashed_password.decode("utf-8") )\
                .save_to_db()
            flash('Usuario creado exitosamente.')
        except:
            flash('El usuario ya existe.')
            return redirect( url_for('admin.create_usr') )

    context = {
        'create_usr_form': create_usr_form,
        "change_role_form": ChangeUserRoleForm,
        # "all_users": UserModel.query_all_user_role(),
        "all_users": UserModel.query_all_but( current_user.username ),
        "usuario": current_user
    }

    return render_template('admin/create_usr.html.jinja', **context)

@admin.route('/delete_usr/<string:username>')
@login_required
def delete_usr(username):
    if username == current_user.username:
        flash('No puedes eliminarte a ti mismo.')
        return redirect( url_for('admin.create_usr') )

    UserModel.delete_by_username( username )
    flash('Usuario eliminado exitosamente.')

    return redirect( url_for('admin.create_usr') )

@admin.route('/change_role', methods=['POST'])
def change_role():
    change_role_form = ChangeUserRoleForm()
    
    print("Change role: ", change_role_form.username.data, change_role_form.role.data)
    if change_role_form.validate_on_submit():
        username = change_role_form.username.data
        role = change_role_form.role.data

        print("Change role: ", username, role)
        UserModel.change_user_role( username, role )
        flash(f'Rol de {username} cambiado exitosamente a {role}')

    return redirect( url_for('admin.create_usr') )


