from flask import Flask, render_template

app = Flask(__name__)

## HTML 화면 보여주기
@app.route('/')
def homework():
    return render_template('index.html')

##push test
print("push")

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)