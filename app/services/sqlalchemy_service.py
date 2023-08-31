from sqlalchemy import create_engine

class SQLAlchemyService:
    def __init__(self, db_uri):
        self.engine = create_engine(db_uri)

    def get_engine(self):
        return self.engine

    def get_session(self):
        return self.engine.session()

# Path: app\services\sqlalchemy_service.py
    