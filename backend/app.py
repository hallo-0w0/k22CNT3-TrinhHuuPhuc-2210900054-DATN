from backend import create_app
from backend.models import *  # Import tất cả models để SQLAlchemy nhận diện

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
