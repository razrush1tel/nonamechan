from package import create_app
import create_db

app = create_app()

if __name__ == "__main__":
    app.run(port=5000, host='0.0.0.0', debug=True)
