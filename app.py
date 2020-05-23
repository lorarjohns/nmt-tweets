from flask import (
    render_template
)
import connexion
import datetime
import logging
from connexion import NoContent

import orm

db_session = None


def get_tweets(lower_bound=None):
    q = db_session.query(orm.Tweet)
    if lower_bound:
        q = q.filter(orm.Tweet.id > lower_bound)
    return [t.dump() for t in q]


def get_tweet(tweet_id):
    tweet = db_session.query(orm.Tweet).filter(orm.Tweet.id == tweet_id).one_or_none()
    return tweet.dump() if tweet is not None else ('Not found', 404)


def put_tweet(tweet_id, tweet):
    t = db_session.query(orm.Tweet).filter(orm.Tweet.id == tweet_id).one_or_none()
    tweet['id'] = tweet_id
    if t is not None:
        logging.info('Updating tweet %s..', tweet_id)
        t.update(**tweet)
    else:
        logging.info('Creating tweet %s..', tweet_id)
        tweet['created'] = datetime.datetime.utcnow()
        db_session.add(orm.Tweet(**tweet))
    db_session.commit()
    return NoContent, (200 if t is not None else 201)


def delete_tweet(tweet_id):
    tweet = db_session.query(orm.Tweet).filter(orm.Tweet.id == tweet_id).one_or_none()
    if tweet is not None:
        logging.info('Deleting tweet %s..', tweet_id)
        db_session.query(orm.Tweet).filter(orm.Tweet.id == tweet_id).delete()
        db_session.commit()
        return NoContent, 204
    else:
        return NoContent, 404


logging.basicConfig(level=logging.INFO)
db_session = orm.init_db('postgresql://usr:pass@0.0.0.0:5432/sqlalchemy')

app = connexion.FlaskApp(__name__)
app.add_api("openapi.yml")

application = app.app

@application.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route('/')
def home():
    '''
    return home.html
    from 0.0.0.0:8081
    '''

    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081, use_reloader=True, threaded=False)