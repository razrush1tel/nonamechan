from package import create_app
import os

app = create_app()

if __name__ == "__main__":
    ctx = app.app_context()
    ctx.push()
    db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, host='0.0.0.0', debug=True)
