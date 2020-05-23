from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, create_engine, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
import os
import logging
from datetime import datetime
from collections import namedtuple

from gensim.summarization.textcleaner import get_sentences

TWEETS_FILE = os.environ["TWEETS_FILE"]

Node = namedtuple("Node", "tweet created parent")

Base = declarative_base()


def timestamp():
    return datetime.now().strftime(("%Y-%m-%d %H:%m:%S"))


def insert_many(TWEETS_FILE, db_session):
    with open(TWEETS_FILE, 'r') as f:
        for i, line in enumerate(f.readlines()):
            line = line.strip("\n")
            if line != "":
                if len(line) <= 274:
                    logging.info(f"Line no. {i} processed with length {len(line)}.\n{line}")
                    db_session.add(Tweet(line, timestamp()))

                else:
                    logging.info(f"Line no. {i} too long ({len(line)}):\n{line}")
                    new_lines = get_sentences(line)
                    num_total = len(new_lines)

                    new_tweets = []
                    for i, line in enumerate(new_lines, start=1):
                        line = line + f" {str(i)}/{str(num_total)}"
                        if i == 1:
                            new_tweets.append(Tweet(line, ))

class Tweet(Base):
    __tablename__ = 'tweets'
    tweet_id = Column('tweet_id', Integer, primary_key=True)
    tweet = Column('tweet', String(280))

    created = Column('created', DateTime())
    parent_id = Column('parent_id', Integer, ForeignKey('Tweet.tweet_id'))
    parent = relationship('Tweet', backref=backref('child'),
                          remote_side=[id])

    def __init__(self, tweet, created, children=None):
        self.tweet = tweet
        self.created = created
        if children:
            self.children = children

    def update(self, tweet_id=None, tweet_body=None, tags=None, created=None):
        if tweet_body is not None:
            self.tweet_body = tweet_body
        if created is not None:
            self.created = created

    def dump(self):
        return dict([(k, v) for k, v in vars(self).items() 
                    if not k.startswith('_')])


def init_db(uri):
    engine = create_engine(uri, convert_unicode=True)
    db_session = scoped_session(sessionmaker(autocommit=True,
                                autoflush=True, bind=engine))
    Base.metadata.create_all(bind=engine)
    Base.query = db_session.query_property()

    with open(TWEETS_FILE, 'r') as f:
        for i, line in enumerate(f.readlines()):
            if f != "\n":
                if len(line) <= 280:
                    db_session.add(Tweet(line, datetime.now().strftime(("%Y-%m-%d %H:%m:%S"))))
                else:
                    logging.info(f"Line no. {i} too long ({len(line)}):\n{line}")

    return db_session

'''
Self-Referential Query Strategies
Querying of self-referential structures works like any other query:

# get all nodes named 'child2'
session.query(Node).filter(Node.data=='child2')
However extra care is needed when attempting to join along the foreign key from one level of the tree to the next. In SQL, a join from a table to itself requires that at least one side of the expression be “aliased” so that it can be unambiguously referred to.

Recall from Using Aliases in the ORM tutorial that the aliased() construct is normally used to provide an “alias” of an ORM entity. Joining from Node to itself using this technique looks like:

from sqlalchemy.orm import aliased

nodealias = aliased(Node)
SQLsession.query(Node).filter(Node.data=='subchild1').\
                join(Node.parent.of_type(nodealias)).\
                filter(nodealias.data=="child2").\
                all()
For an example of using aliased() to join across an arbitrarily long chain of self-referential nodes, see XML Persistence.
https://docs.sqlalchemy.org/en/13/orm/examples.html#examples-xmlpersistence

Configuring Self-Referential Eager Loading
Eager loading of relationships occurs using joins or outerjoins from parent to child table during a normal query operation, such that the parent and its immediate child collection or reference can be populated from a single SQL statement, or a second statement for all immediate child collections. SQLAlchemy’s joined and subquery eager loading use aliased tables in all cases when joining to related items, so are compatible with self-referential joining. However, to use eager loading with a self-referential relationship, SQLAlchemy needs to be told how many levels deep it should join and/or query; otherwise the eager load will not take place at all. This depth setting is configured via relationships.join_depth:

class Node(Base):
    __tablename__ = 'node'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('node.id'))
    data = Column(String(50))
    children = relationship("Node",
                    lazy="joined",
                    join_depth=2)

SQLsession.query(Node).all()
https://docs.sqlalchemy.org/en/13/orm/self_referential.html

'''