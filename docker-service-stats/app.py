from flask import Flask, render_template, redirect
import deviceInfo

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/info')
def info():
    deviceInfo.get_info()
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
