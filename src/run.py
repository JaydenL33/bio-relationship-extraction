from frontend import app

# app = create_app()

if __name__ == "__main__":
    # port = int(os.environ.get("PORT", 5000))
    app.jinja_env.auto_reload = True
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    # app.run(host='0.0.0.0')
    app.run()