from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Здравей от Techtrix ERP!"

if __name__ == "__main__":
    app.run(debug=True)