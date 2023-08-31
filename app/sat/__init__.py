from flask import Blueprint

sat = Blueprint('sat', __name__)

from . import views