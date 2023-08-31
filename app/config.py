from os import environ

class Config:
    SESSION_COOKIE_NAME = 'session'
    SAT_PASSWORD = environ.get('SAT_PASSWORD')

class TestingConfig( Config ):
    """Set Flask configuration vars"""
    SECRET_KEY = "secure key" #os.environ.get('SECRET_KEY')
    # DEBUG = True
    SQLALCHEMY_DATABASE_URI = f"postgresql://postgres:password@localhost:5432/rfc-actas"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    

class ProductionConfig( Config ):
    """Set Flask configuration vars"""
    SECRET_KEY = environ.get('SECRET_KEY')
    uri = environ.get('DATABASE_URL')
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False   
    DEBUG = False
    TESING = False


class HeroConfig( Config ):
    """Set Flask configuration vars"""
    SECRET_KEY = environ.get('SECRET_KEY')
    DEBUG = False
    TESING = False