from models import Artist, Venue
from sqlalchemy import asc
from flask import render_template, Blueprint

index_blueprint = Blueprint('home', __name__)

class IndexController():
    @index_blueprint.route('/')
    def index():
        most_recent_artists = Artist.query.order_by(asc(Artist.created_at)).limit(10).all()
        most_recent_venues = Venue.query.order_by(asc(Venue.created_at)).limit(10).all()
        return render_template('pages/home.html', most_recent_artists=most_recent_artists,
                                                  most_recent_venues=most_recent_venues)

