# Jiefeng Ou, Wesley Leon, Alexandru Cimpoiesu
# monky
# SoftDev
# P01: ArRESTed Development

from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template("home.html");

if __name__ == "__main__":
    app.debug = True
    app.run()
