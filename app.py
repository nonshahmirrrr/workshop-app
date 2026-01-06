from flask import Flask

import auth

import customers
import vehicles
import mechanics
import services
import records
import bills
import parts

app = Flask(__name__)
import os
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-secret")


auth.init_app(app)

# ✅ ADD THIS LINE
app.register_blueprint(auth.bp)

app.register_blueprint(customers.bp)
app.register_blueprint(vehicles.bp)
app.register_blueprint(mechanics.bp)
app.register_blueprint(services.bp)
app.register_blueprint(records.bp)
app.register_blueprint(bills.bp)
app.register_blueprint(parts.bp)

if __name__ == "__main__":
    app.run(debug=True)
