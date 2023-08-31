from flask import Blueprint

robot = Blueprint('robot', __name__)

from . import views