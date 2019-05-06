import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

engine = create_engine('sqlite:///:memory:', echo=True)
print(sqlalchemy.__version__ )
Base = declarative_base()
# class User(Base):
#     __tablename__ = 'users'
#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#     fullname = Column(String)
#     nickname = Column(String)
#     def __repr__(self):
#         return "<User(name='%s', fullname='%s', nickname='%s')>" % (
#                self.name, self.fullname, self.nickname)
# print(repr(User.__table__ ))
# print(Base.metadata.create_all(engine))

from sqlalchemy import Sequence
Column(Integer, Sequence('user_id_seq'), primary_key=True)
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column(String(50))
    fullname = Column(String(50))
    nickname = Column(String(50))

    def __repr__(self):
        return "<User(name='%s', fullname='%s', nickname='%s')>" % (
                                self.name, self.fullname, self.nickname)
print(repr(User.__table__ ))
print(Base.metadata.create_all(engine))

ed_user = User(name='ed', fullname='Ed Jones', nickname='edsnickname')
print(ed_user.name)
print(ed_user.nickname)
print(str(ed_user.id))

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
Session = sessionmaker()
Session.configure(bind=engine)  
session = Session()
ed_user = User(name='ed', fullname='Ed Jones', nickname='edsnickname')
session.add(ed_user)
our_user = session.query(User).filter_by(name='ed').first() 
print(our_user)
print(ed_user is our_user)
session.add_all([
                 User(name='wendy', fullname='Wendy Williams', nickname='windy'),
                 User(name='mary', fullname='Mary Contrary', nickname='mary'),
                 User(name='fred', fullname='Fred Flintstone', nickname='freddy')])
ed_user.nickname = 'eddie'
print(session.dirty)
print(session.new)
session.commit()
print(ed_user.id)

ed_user.name = 'Edwardo'
fake_user = User(name='fakeuser', fullname='Invalid', nickname='12345')
session.add(fake_user)
users = session.query(User).filter(User.name.in_(['Edwardo', 'fakeuser'])).all()
print(users)
session.rollback()
print(ed_user.name)
print(fake_user in session) 
print(session.query(User).filter(User.name.in_(['ed', 'fakeuser'])).all())

for instance in session.query(User).order_by(User.id):
    print(instance.name, instance.fullname)

for name, fullname in session.query(User.name, User.fullname):
    print(name, fullname)

for row in session.query(User, User.name).all():
    print(row.User, row.name)

for row in session.query(User.name.label('name_label')).all():
    print(row.name_label)

from sqlalchemy.orm import aliased
user_alias = aliased(User, name='user_alias')

for row in session.query(user_alias, user_alias.name).all():
    print(row.user_alias, row.user_alias.name)

for u in session.query(User).order_by(User.id)[1:3]:
    print(u)

for name, in session.query(User.name).filter_by(fullname='Ed Jones'):
    print(name)

for name, in session.query(User.name).filter(User.fullname=='Ed Jones'):
    print(name)

for user in session.query(User).\
         filter(User.name=='ed').\
         filter(User.fullname=='Ed Jones'):
    print(user)

#query = session.query(User).filter(User.name.like('%ed')).order_by(User.id)
#print(query.all())
#print(query.first())
#print(query.one())
#print(query.filter(User.id == 99).one())

#query = session.query(User.id).filter(User.name == 'ed').order_by(User.id)
#print(query.scalar())

from sqlalchemy import text
for user in session.query(User).\
             filter(text("id<224")).\
             order_by(text("id")).all():
    print(user.name)

print(session.query(User).filter(text("id<:value and name=:name")).\
      params(value=224, name='fred').order_by(User.id).one())

print(session.query(User).from_statement(
                     text("SELECT * FROM users where name=:name")).\
                     params(name='ed').all())

#stmt = text("SELECT name, id, fullname, nickname "
#            "FROM users where name=:name")
#stmt = stmt.columns(User.name, User.id, User.fullname, User.nickname)
#print(session.query(User).from_statement(stmt).params(name='ed').all())

stmt = text("SELECT name, id FROM users where name=:name")
stmt = stmt.columns(User.name, User.id)
print(session.query(User.id, User.name).\
          from_statement(stmt).params(name='ed').all())
print(session.query(User).filter(User.name.like('%ed')).count())

from sqlalchemy import func
print(session.query(func.count(User.name), User.name).group_by(User.name).all())
print(session.query(func.count('*')).select_from(User).scalar())
print(session.query(func.count(User.id)).scalar())

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
class Address(Base):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="addresses")

    def __repr__(self):
        return "<Address(email_address='%s')>" % self.email_address

User.addresses = relationship(
     "Address", order_by=Address.id, back_populates="user")
#print(repr(User.__table__ ))
print(Base.metadata.create_all(engine))

jack = User(name='jack', fullname='Jack Bean', nickname='gjffdd')
jack.addresses = [
                 Address(email_address='jack@google.com'),
                 Address(email_address='j25@yahoo.com')]
print(jack.addresses[1])
print(jack.addresses[1].user)

session.add(jack)
session.commit()
jack = session.query(User).\
 filter_by(name='jack').one()
print(jack)
print(jack.addresses)

for u, a in session.query(User, Address).\
                     filter(User.id==Address.user_id).\
                     filter(Address.email_address=='jack@google.com').\
                     all():
    print(u)
    print(a)

print(session.query(User).join(Address).\
        filter(Address.email_address=='jack@google.com').\
        all())
print(session.query(User, Address).select_from(Address).join(User))

from sqlalchemy.orm import aliased
adalias1 = aliased(Address)
adalias2 = aliased(Address)

for username, email1, email2 in \
     session.query(User.name, adalias1.email_address, adalias2.email_address).\
     join(adalias1, User.addresses).\
     join(adalias2, User.addresses).\
     filter(adalias1.email_address=='jack@google.com').\
     filter(adalias2.email_address=='j25@yahoo.com'):
     print(username, email1, email2)

from sqlalchemy.sql import func
stmt = session.query(Address.user_id, func.count('*').\
         label('address_count')).\
         group_by(Address.user_id).subquery()

for u, count in session.query(User, stmt.c.address_count).\
     outerjoin(stmt, User.id==stmt.c.user_id).order_by(User.id):
     print(u, count)