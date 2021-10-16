import sqlalchemy as sq
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

DSN = 'postgresql://login:pass@localhost:5432/database'
engine = sq.create_engine(DSN)
Session = sessionmaker(bind=engine)


class User_vk(Base):
    __tablename__ = 'user_vk'
    id = sq.Column(sq.Integer, primary_key=True)
    user_vk_id = sq.Column(sq.Integer, nullable=False, unique=True)
    all_shown = relationship('Shown_person', secondary='user_shown')
    all_requests = relationship('Request', secondary='user_request')


class User_Request(Base):
    __tablename__ = 'user_request'
    __table_args__ = (sq.PrimaryKeyConstraint('user_id', 'request_id'),)
    user_id = sq.Column(sq.Integer(), sq.ForeignKey("user_vk.id"))
    request_id = sq.Column(sq.Integer(), sq.ForeignKey("request.id"))


class Request(Base):
    __tablename__ = 'request'
    id = sq.Column(sq.Integer, primary_key=True)
    city = sq.Column(sq.Integer, nullable=False)
    sex = sq.Column(sq.Integer, nullable=False)
    status = sq.Column(sq.Integer, nullable=False)
    age = sq.Column(sq.Integer, nullable=False)
    users = relationship("User_vk", secondary='user_request')


class User_Shown(Base):
    __tablename__ = 'user_shown'
    __table_args__ = (sq.PrimaryKeyConstraint('user_id', 'shown_id'),)
    user_id = sq.Column(sq.Integer(), sq.ForeignKey("user_vk.id"))
    shown_id = sq.Column(sq.Integer(), sq.ForeignKey("shown_person.id"))


class Shown_person(Base):
    __tablename__ = 'shown_person'
    id = sq.Column(sq.Integer, primary_key=True)
    person_vk_id = sq.Column(sq.Integer, nullable=False, unique=True)
    name = sq.Column(sq.String(30), nullable=False)
    users = relationship('User_vk', secondary='user_shown')
    phi = relationship('Photo_id')
    request_id = sq.Column(sq.Integer(), sq.ForeignKey('request.id'), nullable=False)


class Photo_id(Base):
    __tablename__ = 'photo_id'
    id = sq.Column(sq.Integer, primary_key=True)
    photo_id = sq.Column(sq.String(30), nullable=False, unique=True)
    shown_id = sq.Column(sq.Integer(), sq.ForeignKey('shown_person.id'), nullable=False)


Base.metadata.create_all(engine)
# Base.metadata.drop_all(engine)

session = Session()


def write_db(u_id, params_dict, age, db_list):
    user1 = session.query(User_vk).filter(User_vk.user_vk_id == u_id).first()
    if user1:
        for request in user1.all_requests:
            if age == request.age \
                    and params_dict['status'] == request.status \
                    and params_dict['sex'] == request.sex \
                    and params_dict['city'] == request.city:
                write_new_people_db(db_list, user1, request)
                return

    else:
        user1 = User_vk(user_vk_id=u_id)
        session.add(user1)

    request = Request(city=params_dict['city'], status=params_dict['status'], sex=params_dict['sex'], age=age)
    session.add(request)
    session.commit()
    user_request = User_Request(user_id=user1.id, request_id=request.id)
    session.add(user_request)
    session.commit()

    write_new_people_db(db_list, user1, request)


def write_new_people_db(db_list, user1, request):
    for person in db_list:
        shown1 = Shown_person(person_vk_id=person['people_id'], name=person['name'], request_id=request.id)
        session.add(shown1)
        session.commit()
        user_shown = User_Shown(user_id=user1.id, shown_id=shown1.id)
        session.add(user_shown)
        if person['photo']:
            for photo in person['photo']:
                photo1 = Photo_id(photo_id=photo, shown_id=shown1.id)
                session.add(photo1)
        session.commit()


def check_db(u_id, params, age):
    user = session.query(User_vk).filter(User_vk.user_vk_id == u_id).first()
    if user:  # если юзер уже есть в базе
        for request in user.all_requests:
            if age == request.age \
                    and params['status'] == request.status \
                    and params['sex'] == request.sex \
                    and params['city'] == request.city:
                # проверка set
                old_people = [i.person_vk_id for i in user.all_shown]
                # offset
                count = session.query(Shown_person).filter(User_Request.request_id == request.id).count()
                return old_people, count
    return 0, 0
