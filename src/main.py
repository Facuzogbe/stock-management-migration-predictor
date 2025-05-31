# src/main.py
from app import create_app  # usa la de __init__.py, que tiene static_folder bien puesto

app = create_app()

if __name__ == "__main__":
    print(app.url_map)  # debug
    app.run(debug=True)
