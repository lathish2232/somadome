from db import db
from sqlalchemy import Column
from geoalchemy2 import Geometry
from datetime import date,timedelta
from geoalchemy2.shape import to_shape 
from geoalchemy2 import functions
# class TestTbl(db.Model):
#     id= db.Column(db.Integer, autoincrement=True, primary_key=True)
#     geoLocation=Column(Geometry('POINT'))

class TestTbl(db.Model):
    ownerId = db.Column(db.Integer, autoincrement=True, primary_key=True)
    location = db.Column(Geometry(geometry_type='POINT'))

    @classmethod
    def select_data(cls):
        return cls.query.first().json_fmt()
        
    def json_fmt(self):
        print(dir(functions.ST_AsGeoJSON(self.location)))
        return{
             "ownerId": self.ownerId,
            "location": functions.ST_AsGeoJSON(self.location),
        }

class ContentOwner(db.Model):
    
    __tablename__ = "content_owner"
    __table_args__ = {'extend_existing': True}
     
    ownerId = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(32), nullable=True)
    description = db.Column(db.Text, nullable=True)
    imageUrl = db.Column(db.String(80), nullable=True)

    @classmethod
    def find_by_id(cls, _id: int) -> "ContentOwner":
        return cls.query.filter_by(ownerId=_id).first()

    def json_fmt(self):
        return {
            "ownerId": self.ownerId,
            "name": self.name,
            "description": self.description,
            "imageUrl": self.imageUrl
        }

class Category(db.Model):

    __tablename__ = "category"
    __table_args__ = {'extend_existing': True}

    categoryId = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(32), nullable=True)
    imageUrl = db.Column(db.Text, nullable=True)

class Tier(db.Model):

    __tablename__ = "tier"
    __table_args__ = {'extend_existing': True}

    tierId = db.Column(db.Integer, autoincrement=True, primary_key=True)    
    name = db.Column(db.String(32),nullable=True )
    description = db.Column(db.Text, nullable=True)

    @classmethod
    def get_tier_ids(cls)->"Tier":
        tier_ids=cls.query.with_entities(Tier.tierId).all()
        result=[i for id in tier_ids for i in id]
        return result 

class Subscription(db.Model):

    __tablename__ = 'subscription'
    __table_args__ = {'extend_existing': True}

    subscritptionId = db.Column(db.Integer, autoincrement=True, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.userid'))
    tiers = db.Column(db.Integer, db.ForeignKey('tier.tierId'))
    startDate = db.Column(db.DATE,nullable=True )
    endDate = db.Column(db.DATE,nullable=False)
    billingInterval = db.Column(db.CHAR(8), nullable=True)
    price = db.Column(db.NUMERIC [ (10, 3) ], nullable=True)

class Content(db.Model):

    __tablename__ = "content"
    __table_args__ = {'extend_existing': True}

    contentId = db.Column(db.Integer, autoincrement=True, primary_key=True)
    ownerId = db.Column(db.Integer, db.ForeignKey('content_owner.ownerId'))
    categories = db.Column(db.Integer, db.ForeignKey('category.categoryId'))
    tierId = db.Column(db.Integer, db.ForeignKey('tier.tierId'), nullable=False)
    duration = db.Column(db.SMALLINT, nullable=True)
    author = db.Column(db.String(32),nullable=True )
    title = db.Column(db.String(64),nullable=False)
    description = db.Column(db.Text, nullable=True)
    imageUrl = db.Column(db.String(64), nullable=True)
    audioUrl = db.Column(db.String(80), nullable=True)

    @classmethod
    def get_content(cls, _id: int) -> "Content":
        result=cls.query\
                        .join(Category, Content.categories==Category.categoryId)\
                        .join(Tier, Content.tierId==Tier.tierId)\
                        .join(ContentOwner, Content.ownerId==ContentOwner.ownerId)\
                        .add_columns(Category.name,
                                    Category.imageUrl,
                                    ContentOwner.name,
                                    ContentOwner.description,
                                    ContentOwner.imageUrl,
                                    Tier.tierId
                                    ).all()
        return result
    #.join(Subscription, db.and_(Content.ownerId== Subscription.userId,
    #                    Tier.tierId==Subscription.tiers))\

    @classmethod
    def find_by_id(cls, _id: int) -> "Content":
        return cls.query.filter_by(ownerId=_id).first()

    def json_fmt(self):
        return {
            "contentId": self.contentId,
            "ownerId": self.ownerId,
            "categories": self.categories,
            "tierId": self.tierId,
            "duration": self.duration,
            "author": self.author,
            "title": self.title,
            "description": self.description,
            "imageUrl": self.imageUrl,
            "audioUrl": self.audioUrl
        }

class Host(db.Model):

    __tablename__ = 'host'
    __table_args__ = {'extend_existing': True}

    hostId = db.Column(db.Integer, autoincrement=True, primary_key=True)
    ownerId = db.Column(db.Integer, db.ForeignKey('content_owner.ownerId'))
    imageId = db.Column(db.Integer, db.ForeignKey('img.id'))
    companyName = db.Column(db.String(32),nullable=True )
    address1 = db.Column(db.String(64),nullable=False)
    address2 = db.Column(db.String(64), nullable=True)
    city = db.Column(db.String(32), nullable=True)
    state = db.Column(db.String(32),  nullable=False)
    zip = db.Column(db.String(16), nullable=True)
    pricingModel = db.Column(db.SMALLINT, nullable=True)
    priceVariance = db.Column(db.NUMERIC [ (10, 3) ], default=1.0,nullable=True)


class Dome(db.Model):

    __tablename__ = 'dome'
    __table_args__ = {'extend_existing': True}

    domeId = db.Column(db.Integer, autoincrement=True, primary_key=True)
    hostId = db.Column(db.Integer, db.ForeignKey('host.hostId'))
    timeZone = db.Column(db.SMALLINT,nullable=True )
    geoLocation = db.Column(db.FLOAT,nullable=False)
    locationAddress = db.Column(db.String(128), nullable=True)
    locationDescription = db.Column(db.Text, nullable=True)
    imageUrl = db.Column(db.String(64),  nullable=False)
    model = db.Column(db.String(32), nullable=True)
    publicUse = db.Column(db.BOOLEAN, default="$",nullable=True)

    @classmethod
    def find_domes(cls) -> "Dome":
        return cls.query.all()

    def json_fmt(self):
        return {
            "domeId": self.domeId,
            "hostId":self.startTime,
            "timeZone":self.endTime,
            "geoLocation":self.completed,
            "locationAddress":self.interrupts,
            "locationDescription":self.domeRating,
            "imageUrl":self.domeFeedback,
            "model":self.contentRating,
            "publicUse":self.contentFeedback,
        }

class Availability(db.Model):

    __tablename__ = 'availability'
    __table_args__ = {'extend_existing': True}

    availabilityId = db.Column(db.Integer, autoincrement=True, primary_key=True)
    domeId = db.Column(db.Integer, db.ForeignKey('dome.domeId'))
    isAvailable = db.Column(db.BOOLEAN,nullable=True )
    dayOfWeek = db.Column(db.CHAR(3),nullable=False)
    date = db.Column(db.DATE, nullable=True)
    startTime = db.Column(db.TIME, nullable=True)
    endTime = db.Column(db.TIME,  nullable=False)

    @classmethod
    #get all domes by date
    def find_dome_availability(cls,_dome_id,_date,_time) -> "Availability":
        query_result= cls.query.with_entities(Availability.date,
                                       Availability.startTime,
                                       Availability.endTime).filter((Availability.domeId==_dome_id),
                                                                    (Availability.date==_date),
                                                                    (Availability.startTime>=_time)).all()
        
        return query_result
    @classmethod
    def get_public_domes(cls):
        pass

    

    
class Reservation(db.Model):

    __tablename__ = 'reservation'
    __table_args__ = {'extend_existing': True}
    
    reservationId = db.Column(db.Integer, autoincrement=True, primary_key=True)
    domeId = db.Column(db.Integer, db.ForeignKey('dome.domeId'))
    userId = db.Column(db.Integer, db.ForeignKey('user.userid'))
    contentId = db.Column(db.Integer, db.ForeignKey('content.contentId'))
    resDate = db.Column(db.DATE, nullable=True)
    startTime = db.Column(db.TIME, nullable=True)
    duration = db.Column(db.SMALLINT,  nullable=False)
    pricePaid = db.Column(db.NUMERIC [ (10, 3) ], nullable=True)
    currency = db.Column(db.String(8),nullable=True)
    #currency = db.Column(db.String(8), default "USD",nullable=True)
    isCancelled = db.Column(db.BOOLEAN, nullable=True)
    dateCancelled = db.Column(db.DATE, nullable=True)
    refundApplied = db.Column(db.BOOLEAN, nullable=True)
    
    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()
        
class Session(db.Model):
    
    __tablename__ = 'session'
    __table_args__ = {'extend_existing': True}

    sessionId = db.Column(db.Integer, autoincrement=True, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.userid'))
    reservationId = db.Column(db.Integer, db.ForeignKey('reservation.reservationId'))
    contentId = db.Column(db.Integer, db.ForeignKey('content.contentId'))
    domeId = db.Column(db.Integer, db.ForeignKey('dome.domeId'))
    startTime = db.Column(db.TIMESTAMP, nullable=True)
    endTime = db.Column(db.TIMESTAMP,nullable=True )
    completed = db.Column(db.BOOLEAN,nullable=False)
    interrupts = db.Column(db.SMALLINT, nullable=True)
    domeRating = db.Column(db.SMALLINT, nullable=True)
    domeFeedback = db.Column(db.Text, nullable=True)
    contentRating = db.Column(db.SMALLINT, nullable=True)
    contentFeedback = db.Column(db.Text, nullable=True)

    @classmethod
    def find_by_id(cls, _id: int) -> "Session":
        return cls.query.filter_by(userId=_id).all()

    @classmethod
    def find_session_in_pastdays(cls, _id: int,past_days: int) -> "Session":
        start_range = date.today() + timedelta(days=-past_days)
        end_range = date.today()
        result={
        "sessionsInPastDays":cls.query.filter((Session.userId==_id),(Session.startTime.between(start_range,end_range))).count()
        ,"totalSessions":cls.query.filter_by(userId=_id).count()
        ,"consecutiveSessions":0
        ,"maxConsecutiveSessions":0
        }
        return result



    def json_fmt(self):
        return {
            "sessionId": self.sessionId,
            "userId": self.userId,
            "contentId": self.contentId,
            "domeId": self.domeId,
            "startTime":self.startTime,
            "endTime":self.endTime,
            "completed":self.completed,
            "interrupts":self.interrupts,
            "domeRating":self.domeRating,
            "domeFeedback":self.domeFeedback,
            "contentRating":self.contentRating,
            "contentFeedback":self.contentFeedback,
        }