from forms import VenueForm
from models.Venue import Venue
from flask import flash, render_template, Blueprint, request, redirect, url_for
from models.db_file import db
from models.Show import Show
import sys
from datetime import datetime

venue_bp = Blueprint('venues', __name__)


class VenueController:

    #  Get All Venues
    #  ----------------------------------------------------------------
    @venue_bp.route('/')
    def venues():
        areas = []
        locations = db.session.query(Venue.city, Venue.state).distinct()
        for location in locations:
            temp = {'location_name': F"city & state: {location[0]} / {location[1]}",
                    'venues': Venue.query.filter(Venue.city.like(location[0]) & Venue.state.like(location[1])).all()}
            areas.append(temp)

        return render_template('pages/venues.html', areas=areas)

    #  Search Venue
    #  ----------------------------------------------------------------
    @venue_bp.route('/search', methods=['POST'])
    def search_venues():
        s = F"%{request.form.get('search_term')}%"
        data = Venue.query.filter(Venue.name.ilike(s) | Venue.city.ilike(s) | Venue.state.ilike(s)).all()
        response = {
            "count": len(data),
            "data": data
        }
        return render_template('pages/search_venues.html', results=response,
                               search_term=request.form.get('search_term', ''))

    #  Get Venue Detail
    #  ----------------------------------------------------------------
    @venue_bp.route('/<int:venue_id>')
    def show_venue(venue_id):
        v = Venue.query.get(venue_id)
        upcoming_shows = []
        past_shows = []

        past_shows_query = db.session.query(Show).join(Venue).filter(Show.venue_id == venue_id).filter(
            Show.start_time < datetime.now()).all()
        for show in past_shows_query:
            past_shows.append({
                "artist_id": show.artist_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            })

        upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.venue_id == venue_id).filter(
            Show.start_time > datetime.now()).all()

        for show in upcoming_shows_query:
            upcoming_shows.append({
                "artist_id": show.artist_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            })

        final_venue = {
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "id": v.id,
            "name": v.name,
            "genres": v.genres,
            "city": v.city,
            "state": v.state,
            "address": v.address,
            "phone": v.phone,
            "website": v.website,
            "image_link": v.image_link,
            "facebook_link": v.facebook_link,
            "seeking_talent": v.seeking_talent,
            "seeking_description": v.seeking_description,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows)
        }
        return render_template('pages/show_venue.html', venue=final_venue)

    #  Create Venue
    #  ----------------------------------------------------------------
    @venue_bp.route('/create', methods=['GET'])
    def create_venue_form():
        form = VenueForm()
        return render_template('forms/new_venue.html', form=form)

    @venue_bp.route('/create', methods=['POST'])
    def create_venue_submission():
        form = VenueForm()

        if not form.validate_on_submit():
            print(form.errors)
            return render_template('forms/new_venue.html', form=form)
        try:
            name = request.form['name']
            city = request.form['city']
            state = request.form['state']
            address = request.form['address']
            genres = request.form.getlist('genres')
            phone = request.form['phone']
            image_link = request.form['image_link']
            facebook_link = request.form['facebook_link']
            website = request.form['website']
            seeking_talent = True if request.form.get('seeking_talent') is not None else False
            seeking_description = request.form['seeking_description']
            created_at = datetime.now()

            new_venue = Venue(name=name, address=address, city=city, state=state, phone=phone,
                              genres=genres, facebook_link=facebook_link, image_link=image_link,
                              website=website, seeking_talent=seeking_talent,
                              seeking_description=seeking_description,
                              created_at=created_at)
            db.session.add(new_venue)
            db.session.commit()
            areas = []
            locations = db.session.query(Venue.city, Venue.state).distinct()
            for location in locations:
                temp = {'location_name': F"city & state: {location[0]} / {location[1]}",
                        'venues': Venue.query.filter(
                            Venue.city.like(location[0]) & Venue.state.like(location[1])).all()}
                areas.append(temp)
            flash('Venue was successfully added')
            return render_template('pages/venues.html', areas=areas)
        except:
            db.session.rollback()
            print(sys.exc_info())
            return render_template('forms/new_venue.html', form=form)
        finally:
            db.session.close()

    #  Update Venue
    #  ----------------------------------------------------------------

    @venue_bp.route('/<int:venue_id>/edit', methods=['GET'])
    def edit_venue(venue_id):
        venue = Venue.query.get(venue_id)
        form = VenueForm(obj=venue)

        return render_template("forms/edit_venue.html", form=form, venue=venue)

    @venue_bp.route('/<int:venue_id>/edit', methods=['POST'])
    def edit_venue_submission(venue_id):
        form = VenueForm()
        venue = Venue.query.get(venue_id)

        if not form.validate_on_submit():
            print(form.errors)
            sep = '\n'
            return render_template('forms/edit_venue.html', venue=venue, form=form)
        try:
            venue.name = request.form['name']
            venue.city = request.form['city']
            venue.state = request.form['state']
            venue.genres = request.form.getlist('genres')
            venue.phone = request.form['phone']
            venue.image_link = request.form['image_link']
            venue.facebook_link = request.form['facebook_link']
            venue.website = request.form['website']
            venue.seeking_talent = True if request.form.get('seeking_talent') is not None else False
            venue.seeking_description = request.form['seeking_description']
            venue.created_at = datetime.now()
            db.session.commit()

            flash('Venue was successfully added')
            data = Venue.query.all()
            return render_template('pages/venues.html', venues=data)
        except:
            db.session.rollback()
            print(sys.exc_info())
            return render_template('forms/edit_venue.html', venue=venue, form=form, error="Update was unsuccessful")
        finally:
            db.session.close()

    #  Delete Venue
    #  ----------------------------------------------------------------

    @venue_bp.route('/delete', methods=['POST'])
    def delete_venue():
        try:
            venue_id = request.form['id']
            venue = Venue.query.get(venue_id)
            db.session.delete(venue)
            db.session.commit()
            flash('Venue was successfully deleted.')
            areas = []
            locations = db.session.query(Venue.city, Venue.state).distinct()
            for location in locations:
                temp = {'location_name': F"city & state: {location[0]} / {location[1]}",
                        'venues': Venue.query.filter(
                            Venue.city.like(location[0]) & Venue.state.like(location[1])).all()}
                areas.append(temp)
            return render_template("pages/venues.html", areas=areas)
        except:
            db.session.rollback()
            print(sys.exc_info())
            return render_template("pages/home.html", error="Unexpected error while deleting")
        finally:
            db.session.close()
