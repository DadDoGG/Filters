from sqlalchemy.dialects.postgresql import JSONB
from flask_login import UserMixin

from filters import db, manager


class BaseIdModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)


class Shop(BaseIdModel):
    __tablename__ = "shop"

    shop_type = db.Column(db.String(128))
    name = db.Column(db.String(128), nullable=False)
    contact = db.Column(JSONB)
    workers = db.Column(db.Integer)
    debt = db.Column(db.Float(15))
    date_created = db.Column(db.DateTime, server_default=db.text('now()'))
    provider_id = db.Column(db.Integer, db.ForeignKey('shop.id'))

    product = db.relationship("Product", secondary='product_shop', back_populates="shop", overlaps="product,shop")
    provider = db.relationship('Shop', remote_side='Shop.id', primaryjoin='Shop.provider_id==Shop.id',
                               backref='provided_shops', overlaps="product,shop")


class Product(BaseIdModel):
    __tablename__ = "product"

    name = db.Column(db.String(128), nullable=False)
    model = db.Column(db.String(128), nullable=False)
    date_release = db.Column(db.Date)

    shop = db.relationship("Shop", secondary='product_shop', back_populates="product", overlaps="product,shop")


class ProductShop(db.Model):
    __tablename__ = 'product_shop'

    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), primary_key=True)

    shop = db.relationship('Shop', backref='shop', overlaps="product,shop")
    product = db.relationship('Product', backref='product', overlaps="product,shop")


class User(BaseIdModel, UserMixin):
    __tablename__ = 'user'

    email = db.Column(db.String(120), unique=True)
    login = db.Column(db.String(32), nullable=False, unique=True)
    password = db.Column(db.String(320), nullable=False)
    permission = db.Column(db.String(10), index=True)
    is_active = db.Column(db.Boolean)

    @manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    @property
    def is_admin(self):
        return self.permission == 'admin'

