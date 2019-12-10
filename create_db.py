from package import create_app, db

if __name__ == '__main__':
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    db.create_all()
