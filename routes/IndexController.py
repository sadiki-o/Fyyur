from models.Artist import Artist
from models.Venue import Venue
from sqlalchemy import desc
from flask import render_template, Blueprint

index_bp = Blueprint('home', __name__)


# Home page
#  ----------------------------------------------------------------
class IndexController():
    #  Home Page
    #  ----------------------------------------------------------------
    @index_bp.route('/')
    def index():
        # implemented the bonus feature that shows recent artists and venues
        recent_artists = Artist.query.order_by(Artist.created_at.desc()).limit(10).all()
        recent_venues = Venue.query.order_by(Venue.created_at.desc()).limit(10).all()
        results = {
            "recent_artists": recent_artists,
            "recent_venues": recent_venues
        }
        return render_template('pages/home.html', results=results)
