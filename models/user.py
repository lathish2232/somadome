from datetime import datetime
from db import db


class UserModel(db.Model):
    __tablename__ = "user"

    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False, unique=True)
    pwResetRequired = db.Column(db.Boolean, default=False, nullable=False)
    displayName = db.Column(db.String(80), nullable=True)
    headline = db.Column(db.String(80), nullable=True)
    firstName = db.Column(db.String(80), nullable=True)
    middleInitial = db.Column(db.String(80), nullable=True)
    lastName = db.Column(db.String(80), nullable=True)
    suffix = db.Column(db.String(80), nullable=True)
    phone = db.Column(db.String(80), nullable=True)
    address1 = db.Column(db.String(80), nullable=True)
    address2 = db.Column(db.String(80), nullable=True)
    city = db.Column(db.String(80), nullable=True)
    state = db.Column(db.String(80), nullable=True)
    zip = db.Column(db.String(80), nullable=True)
    joinDate = db.Column(db.Date, default=datetime.utcnow(), nullable=True)
    birthDate = db.Column(db.Date, nullable=True)

    @classmethod
    def find_by_username(cls, _username: str) -> "UserModel":
        return cls.query.filter_by(username=_username).first()

    @classmethod
    def find_by_email(cls, email: str) -> "UserModel":
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_id(cls, _id: int) -> "UserModel":
        return cls.query.filter_by(userid=_id).first()

    def json_data(self):
        return {
            "userId": self.userid,
        }

    def loginData(self, access_token, refresh_token):
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "userId": self.userid,
            "displayName": self.displayName,
            "pwResetRequired": self.pwResetRequired
        }

    def json(self):
        return {
            "userId": self.userid,
            "email": self.email,
            "displayName": self.displayName,
            "headline": self.headline,
            "firstName": self.firstName,
            "middleInitial": self.middleInitial,
            "lastName": self.lastName,
            "suffix": self.suffix,
            "phone": self.phone,
            "address1": self.address1,
            "address2": self.address2,
            "city": self.city,
            "state": self.state,
            "zip": self.zip,
            "joinDate": str(self.joinDate),
            "birthDate": str(self.birthDate),
        }

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
    
    @classmethod
    def update_user_data(cls,new_user_data:dict):
        _id =new_user_data['userid']
        user_data=cls.query.filter_by(userid=_id).first()
        user_data.email=new_user_data.get('email',None)
        user_data.displayName=new_user_data.get('displayName',None)
        user_data.headline=new_user_data.get('headline',None)
        user_data.firstName=new_user_data.get('firstName',None)
        user_data.middleInitial=new_user_data.get('middleInitial',None)
        user_data.lastName=new_user_data.get('lastName',None)
        user_data.suffix=new_user_data.get('suffix',None)
        user_data.phone=new_user_data.get('phone',None)
        user_data.address1=new_user_data.get('address1',None)
        user_data.address2=new_user_data.get('address2',None)
        user_data.city=new_user_data.get('city',None)
        user_data.state=new_user_data.get('state',None)
        user_data.zip=new_user_data.get('zip',None)
        user_data.birthDate=new_user_data.get('birthDate',None)
        db.session.commit()
        return user_data
        
