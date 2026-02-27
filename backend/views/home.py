from flask import Blueprint
#هنا بنشا البلو برينت بتاعي 
home = Blueprint('home', __name__)

#هنا الروات بكون ع حسب اسم البلوبرينت 
@home.route('/')
def home():
    return "Welcome"