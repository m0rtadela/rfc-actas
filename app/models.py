from flask_login import UserMixin
from .services.firestore_service import get_user
import datetime

class UserData:
    def __init__(self, username, password):
        self.username = username
        self.password = password

class Constancia:
    def __init__(self, rfc, curp, tipo, owner_id, state="PENDING"):
        self.rfc = rfc
        self.curp = curp
        # self.name = name
        # self.first_last_name = first_last_name
        # self.second_last_name = second_last_name
        self.tipo = tipo
        self.owner_id = owner_id, #*this is a tuple and I don't know why
        self.date = datetime.datetime.now()
        self.state = state

class UserModel(UserMixin):
    def __init__(self, user_data):
        """
        param user_data : UserData
        """
        self.id = user_data.username
        self.password = user_data.password

    @staticmethod
    def query(user_id):
        user_doc = get_user( user_id )
        user_data = UserData( username=user_doc.id, password=user_doc.to_dict()['password'] )
        return UserModel(user_data)