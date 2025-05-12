from flask import Flask,request,render_template
from services.predictor import find_similar_tickets

app = Flask(__name__)

@app.route('/')
def home():
    name = 'Ansh'
    return render_template('index.html',name = name)

@app.route('/form',methods = ['GET','POST'])
def ticketForm():
    if request.method == 'POST':
        ticketNumber = request.form.get('ticketNumber')
        result = find_similar_tickets(ticketNumber, top_k=5)
        for i in result :
            for key in i :
                print(key," : ",i[key])
            print('\n')

    return render_template('ticketForm.html')

if __name__ == '__main__':
    app.run()


