from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

class Person(db.Model):
    """Model for the Person table"""
    __tablename__ = 'person'

    uID = db.Column(db.Integer, primary_key = True)
    password = db.Column(db.String)
    name = db.Column(db.String)
    gender = db.Column(db.String)
    age = db.Column(db.Integer)

class Vendor(db.Model):
    """Model for the Vendor table"""
    __tablename__ = 'vendor'

    vID = db.Column(db.String, primary_key = True)
    vname = db.Column(db.String)
    name = db.Column(db.String)
    address = db.Column(db.String)
    district = db.Column(db.String)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    rating = db.Column(db.Float)
    icon = db.Column(db.String)

class Review(db.Model):
    """Model for the Review table"""
    __tablename__ = 'review'

    rID = db.Column(db.String)
    author = db.Column(db.String)
    description = db.Column(db.String)
    rating = db.Column(db.Float)
    vID = db.Column(db.String, db.ForeignKey('vendor.vID'), primary_key = True)

class Category(db.Model):
    """Model for the Category table"""
    __tablename__ = 'category'

    cName = db.Column(db.String, primary_key = True)

class Like(db.Model):
    """Model for the Like table"""
    __tablename__ = 'like'

    uID = db.Column(db.Integer, db.ForeignKey('person.uID'), primary_key = True)
    vID = db.Column(db.String, db.ForeignKey('vendor.vID'), primary_key = True)

class Has(db.Model):
    """Model for the Has table"""
    __tablename__ = 'has'

    cName = db.Column(db.String, db.ForeignKey('category.cName'), primary_key = True)
    vID = db.Column(db.String, db.ForeignKey('vendor.vID'), primary_key = True)












