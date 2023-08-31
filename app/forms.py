from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, RadioField, SelectField, DateField
from wtforms.validators import DataRequired, Length, Optional
from flask_wtf.file import FileField, FileRequired, FileAllowed

class RequiredIf(DataRequired):
    """Validator which makes a field required if another field is set and has a truthy value.

    Sources:
        - http://wtforms.simplecodes.com/docs/1.0.1/validators.html
        - http://stackoverflow.com/questions/8463209/how-to-make-a-field-conditionally-optional-in-wtforms
        - https://gist.github.com/devxoul/7638142#file-wtf_required_if-py
    """
    field_flags = ('requiredif',)
    def __init__(self, message=None, *args, **kwargs):
        super(RequiredIf).__init__()
        self.message = message
        self.conditions = kwargs

    # field is requiring that name field in the form is data value in the form
    def __call__(self, form, field):
        for name, data in self.conditions.items():
            other_field = form[name]
            if other_field is None:
                raise Exception('no field named "%s" in form' % name)
            if other_field.data == data and not field.data:
                DataRequired.__call__(self, form, field)
            Optional()(form, field)

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[ DataRequired(), Length(min=4, max=25) ], render_kw={"placeholder": "Usuario"})
    password = PasswordField('Contraseña', validators=[ DataRequired(), Length(min=8, max=80) ], render_kw={"placeholder": "Contraseña"})
    submit = SubmitField('Iniciar Sesión')

class SatLoginForm(FlaskForm):
    certificate = FileField('Certificado', validators=[ FileRequired(), FileAllowed(['cer'], 'Solo archivos .cer') ])
    private_key = FileField('Llave Privada', validators=[ FileRequired(), FileAllowed(['key'], 'Solo archivos .key') ])
    password = PasswordField('Contraseña', validators=[ DataRequired(), Length(min=8, max=80) ])
    submit = SubmitField('Iniciar Sesión')

class ConstanciaForm(FlaskForm):
    # tipo = RadioField('Tipo de Constancia', choices=[('1', 'Fisica'), ('2', 'Moral')], validators=[ DataRequired() ])
    tipo = SelectField('Tipo de Constancia', choices=[('1', 'Fisica'), ('2', 'Moral')], validators=[ DataRequired() ])
    curp = StringField('CURP', validators=[ Optional(), Length(min=18, max=18) ], render_kw={"autocomplete": "off"}) #! Poner en off el autocomplete
    rfc = StringField('RFC', validators=[ Optional(), Length(min=12, max=13) ], render_kw={"autocomplete": "off"})   #! Poner en off el autocomplete
    # grupo = SelectField('Grupo', choices=[('1', 'Grupo 1'), ('2', 'Grupo 2')], validators=[ DataRequired() ]) #* Descomentar cuando se tengan los grupos 
    submit = SubmitField('Obtener Constancia')

class CSVForm(FlaskForm):
    csv_file = FileField('Archivo CSV', validators=[ FileRequired(), FileAllowed(['csv'], 'Solo archivos .csv') ])
    submit = SubmitField('Obtener Constancias')

class TestForm(FlaskForm):
    code = BooleanField('Do you code?')
    code2 = RadioField(
        'If so, what languages do you use?',
        choices=[('python', 'python'), ('C++', 'C++')],
        validators=[RequiredIf(code=True)])
    submit = SubmitField('Submit')

class CreateUserForm(FlaskForm):
    username = StringField('Usuario', validators=[ DataRequired(), Length(min=4, max=20) ])
    password = PasswordField('Contraseña', validators=[ DataRequired(), Length(min=8, max=20) ])
    submit = SubmitField('Crear Usuario')

class FilterConstanciasForm(FlaskForm):
    tipo = SelectField('Tipo de Constancia', choices=[("", "Elige un valor"), ('1', 'Fisica'), ('2', 'Moral')], validators=[ Optional() ])
    state = SelectField('Estatus', choices=[("", "Elige un valor"),('PENDING', 'Pendiente'), ('DESCARGADO', 'Descargado'), ("ERROR", "Error")], validators=[ Optional() ])
    start_date = DateField('Fecha Inicio', validators=[ Optional() ])
    end_date = DateField('Fecha Fin', validators=[ Optional() ])
    owner = StringField('Usuario', validators=[ Optional() ])
    order_by = SelectField('Ordenar por', choices=[("date_desc", "Fecha descendiente"), ("date_asc", "Fecha ascendiente") ], validators=[ Optional() ])
    submit = SubmitField('Filtrar')
    download = SubmitField('Descargar')

class ChangeUserRoleForm(FlaskForm):
    username = StringField('Usuario', validators=[ DataRequired(), Length(min=4, max=20) ])
    role = SelectField('Rol', choices=[('admin', 'Administrador'), ('user', 'Usuario')], validators=[ DataRequired() ])
    submit = SubmitField('Cambiar Rol')