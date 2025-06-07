from app import create_app, db
from flask_cors import CORS

app = create_app()
CORS(app, origins=["http://localhost:8080"], supports_credentials=True)



    

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()


if __name__ == '__main__':
    app.run(debug=True)