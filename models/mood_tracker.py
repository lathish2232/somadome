from db import db


class Songs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # entityType = db.Column(db.Text)
    # entityId = db.Column(db.Integer)
    # replace = db.Column(db.Boolean)
    # index = db.Column(db.Integer)
    musictype = db.Column(db.Text)
    musicfile = db.Column(db.LargeBinary)