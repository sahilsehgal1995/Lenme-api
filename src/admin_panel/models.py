from src import db, BaseMixin


class Log(db.Model, BaseMixin):

    action = db.Column(db.String(55), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    updated_data = db.Column(db.String(1024))
    updated_model = db.Column(db.String(125))
