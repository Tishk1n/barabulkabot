from peewee import *

db = SqliteDatabase('database.db')


class Users(Model):
    id = BigIntegerField(primary_key=True, unique=True)

    class Meta:
        database = db


class Products(Model):
    id = IntegerField(default=0)
    photo = TextField()
    name = TextField()
    description = TextField()
    price = FloatField(default=0)

    class Meta:
        database = db


class Orders(Model):
    user_id = BigIntegerField(default=0)
    product_id = IntegerField(default=0)
    count = IntegerField(default=0)

    class Meta:
        database = db


db.create_tables([Users, Products, Orders])
