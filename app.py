from flask import Flask


app = Flask(__name__)

app.app_context().push()   #giving access of my current app to other modules
 
from controller import *
if __name__=="__main__":
    app.run(debug=True)


