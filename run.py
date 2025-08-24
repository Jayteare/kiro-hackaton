import os
from app import create_app, db

# Get configuration from environment
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)


@app.cli.command()
def init_db():
    """Initialize the database."""
    db.create_all()
    print("Database initialized!")


if __name__ == '__main__':
    app.run(debug=True)