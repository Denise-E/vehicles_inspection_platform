from flask import Flask

# Routers
from src.routes.user_router import users
from src.routes.vehicles_router import vehicles
from src.routes.bookings_router import bookings
from src.routes.inspection_router import inspections


app = Flask(__name__)


# Register blueprints - routes files connection
app.register_blueprint(users, url_prefix="/api/users")
app.register_blueprint(vehicles, url_prefix="/api/vehicles")
app.register_blueprint(bookings, url_prefix="/api/bookings")
app.register_blueprint(inspections, url_prefix="/api/inspections")


@app.route("/api/health", methods=['GET'])
def health():
    return {"msg": 'App running!'}, 200


if __name__ == "__main__":
    app.run(debug=True)