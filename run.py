# run.py
import os
from app import app 
from app import manager



#app.run(debug=True)
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)
