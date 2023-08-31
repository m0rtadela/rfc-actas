from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_login import UserMixin

db = SQLAlchemy()

class UserModel(UserMixin, db.Model):
    __tablename__ = 'users'

    username = db.Column(db.String(20), primary_key=True)
    password = db.Column(db.String(80))
    role = db.Column(db.String(20))

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.role = 'user'

    def __repr__(self):
        return f"{self.username}"

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def query_username(cls, username):
        print(cls, username)
        return cls.query.filter_by(username=username).first()

    @classmethod
    def query_all(cls):
        return cls.query.all()

    @classmethod
    def query_all_user_role(cls):
        return cls.query.filter_by(role='user').all()

    @classmethod
    def query_all_admin_role(cls):
        return cls.query.filter_by(role='admin').all()
    
    @classmethod
    def query_all(cls):
        return cls.query.all()

    @classmethod
    def query_all_but(cls, username):
        return cls.query.filter(cls.username != username).all()

    @classmethod
    def delete_by_username(cls, username):
        cls.query.filter_by(username=username).delete()
        db.session.commit()

    def get_id(self):
        return self.username

    @classmethod
    def change_user_role(cls, username, role):
        user = cls.query.filter_by(username=username).first()
        user.role = role
        db.session.commit()

class ConstanciasModel(db.Model):
    __tablename__ = 'constancias'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rfc = db.Column(db.String(13))
    curp = db.Column(db.String(18))
    grupo = db.Column(db.String(20), default='N/A')
    name = db.Column(db.String(50))
    #? Pensar un campo con intentos de descarga, para que no se quede bloqueado en caso de que no se pueda descargar, pero primero hay que ver que no se atore el robot
    # first_last_name = db.Column(db.String(30))
    # second_last_name = db.Column(db.String(50))
    tipo = db.Column(db.String(2))
    owner = db.Column(db.String(20))
    date = db.Column(db.DateTime(timezone=True), server_default=func.now())
    state = db.Column(db.String(60), default='PENDING')
    file_url = db.Column(db.String(50))

    def __init__(self, rfc, curp, tipo, owner_id, state, date=None, grupo='N/A', name='N/A'):
        self.rfc = rfc
        self.curp = curp
        # self.name = name
        # self.first_last_name = first_last_name
        # self.second_last_name = second_last_name
        self.grupo = grupo
        self.tipo = tipo
        self.owner = owner_id
        self.date = date
        self.state = state  
        self.name = name

    def __repr__(self):
        return f"{self.rfc if self.rfc else self.curp}"

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def save_multiple_to_db(cls, constancias):
        db.session.add_all(constancias)
        db.session.commit()

    @classmethod
    def query_all(cls):
        return cls.query.all()

    @classmethod
    def delete_from_db(cls, id):
        cls.query.filter_by(id=id).delete()
        db.session.commit()

    @classmethod
    def query_download_pending(cls):
        return cls.query.filter_by(state='PENDING').order_by(cls.date.asc()).limit(10).all()

    @classmethod
    def update_state(cls, id, state, file_url="", name=""):
        cls.query.filter_by(id=id).update(dict(state=state, file_url=file_url, name=name[0:45]))
        db.session.commit()

    @classmethod
    def query_all_by_owner_page(cls, owner, page):
        return cls.query.filter_by(owner=owner).order_by(cls.date.desc()).paginate(page=page, per_page=15)

    @classmethod
    def query_all_by_owner(cls, owner):
        return cls.query.filter_by(owner=owner).all()

    @classmethod
    def query_by_filters(cls, date_range=None, owner=None, state=None, tipo=None, pagination=True, page=1, order_by='date_asc'):
        all_filters = []
        if date_range[0] and date_range[1]: #! Corregir, para que pueda buscar por un solo rango
            print("date_range")
            all_filters.append(cls.date.between(date_range[0], date_range[1]))
        if owner:
            print("owner", owner)
            all_filters.append(cls.owner == f"{owner}")
        if state:
            print("state")
            all_filters.append( cls.state.contains( state ) )
        if tipo:
            print("tipo", type( tipo))
            all_filters.append(cls.tipo == tipo)

        print(order_by)

        if order_by == 'date_asc':
            order_by = cls.date.asc()
        elif order_by == 'date_desc':
            order_by = cls.date.desc()

        if pagination:
            return cls.query.filter(*all_filters).order_by(order_by).paginate(page=page, per_page=15)
        else:
            return cls.query.filter(*all_filters).order_by(order_by).all()

    @classmethod
    def query_by_new_filters(cls, type=None, query=None, pagination=True, page=1, order_by='date_asc'):
        all_filters = []
        if type > 0:
            if type == 1:
                all_filters.append(cls.curp == query)
                all_filters.append(cls.rfc == query)
            elif type == 2:
                all_filters.append(cls.rfc == query)

        if order_by == 'date_asc':
            order_by = cls.date.asc()
        elif order_by == 'date_desc':
            order_by = cls.date.desc()

        if pagination:
            return cls.query.filter(*all_filters).order_by(order_by).paginate(page=page, per_page=15)
        else:
            return cls.query.filter(*all_filters).order_by(order_by).all()


        
