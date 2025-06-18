from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    print("index accessed")
    return "<h1>Hello World</h1>"

if __name__ == '__main__':
    app.run(debug=True)
