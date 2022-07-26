import dateutil.parser
import babel
from flask import Flask, render_template
from models.Venue import Venue
from models.Artist import Artist
from models.Show import Show
from models.db_file import db
from moment import Moment
from flask_migrate import Migrate
from routes.IndexController import index_bp
from routes.VenueController import venue_bp
from routes.ArtistController import artist_bp
from routes.ShowController import show_bp
from flask_wtf.csrf import CSRFProtect


# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)  # Create Flask Instance
moment = Moment(app)
csrf = CSRFProtect()   # protect against CSRF attacks
app.config.from_object('config')
db.init_app(app)    # Instantiate SqlAlchemy instance
csrf.init_app(app)
migrate = Migrate(app, db)


# Import and use Routes controllers and set prefixes for easy navigation
app.register_blueprint(index_bp)
app.register_blueprint(venue_bp, url_prefix='/venues')
app.register_blueprint(artist_bp, url_prefix='/artists')
app.register_blueprint(show_bp, url_prefix='/shows')


# ----------------------------------------------------------------------------#
# Error Handlers.
# ----------------------------------------------------------------------------#
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default launch :
if __name__ == '__main__':
    app.run(port=9000)
