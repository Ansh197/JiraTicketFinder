from flask import Flask,request,render_template
from services.predictor import find_similar_tickets

app = Flask(__name__)

@app.route('/',methods = ['GET','POST'])
def home():
    result = None
    if request.method == 'POST':
        ticketNumber = request.form.get('ticketNumber')
        ticketNumber = ticketNumber
        print(ticketNumber)
        res = find_similar_tickets(ticketNumber, top_k=5)
        if res[0] == False:
            return render_template('ticketNotFound.html')
        else :
            result = res[1]

    return render_template('ticketForm.html',result = result)


