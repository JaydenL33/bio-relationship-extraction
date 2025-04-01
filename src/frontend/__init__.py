
from flask import Flask

app = Flask(__name__)
with app.app_context():
    from . import views  
    from . import models  

from .models import graph
try:
    graph.schema.create_uniqueness_constraint("User", "username")
except:
    pass
try:
    graph.schema.create_uniqueness_constraint("Tag", "name")
except:
    pass
try:
    graph.schema.create_uniqueness_constraint("Post", "id")
except:
    pass

