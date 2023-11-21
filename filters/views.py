from flask_login import login_required, current_user
from flask_restful import Resource, reqparse, abort

from filters import api, db
from filters.models import Shop, ProductShop, Product


product_post_args = reqparse.RequestParser()
product_post_args.add_argument('name')
product_post_args.add_argument('model')
product_post_args.add_argument('date_release')

shop_post_args = reqparse.RequestParser()
shop_post_args.add_argument('shop_type')
shop_post_args.add_argument('name')
shop_post_args.add_argument('contact', type=dict)
shop_post_args.add_argument('workers')
shop_post_args.add_argument('debt')
shop_post_args.add_argument('date_created')
shop_post_args.add_argument('provider_id')


def shop_to_result(shop):
    return {
        'id': shop.id,
        'shop_type': shop.shop_type,
        'name': shop.name,
        'contact': shop.contact,
        'workers': shop.workers,
        'debt': shop.debt,
        'date_created': shop.date_created.isoformat(),
    }


class ShopApi(Resource):

    def get(self):
        shops = Shop.query.all()
        result = [shop_to_result(obj) for obj in shops]
        return {'shop': result}


class ShopCityApi(Resource):
    @login_required
    def get(self, city):
        shops = Shop.query.all()
        result = []
        for shop in shops:
            for key, value in shop.contact.items():
                if key == "city" and value == city:
                    result.append(shop_to_result(shop))
        return {'shop': result}


class ShopDebtApi(Resource):
    @login_required
    def get(self):
        shops = Shop.query.all()
        avg_debt = sum(shop.debt for shop in shops) / len(shops)
        result = [shop_to_result(shop) for shop in shops if shop.debt > avg_debt]
        return {'shop': result}


class ShopItemApi(Resource):
    @login_required
    def get(self, item_id):
        shops = Shop.query.all()
        result = []
        for shop in shops:
            for prod in shop.product:
                if prod.id == item_id:
                    result.append(shop_to_result(shop))
        return {'shop': result}


class ShopEditApi(Resource):
    @login_required
    def post(self, shop_id):
        args = shop_post_args.parse_args()
        shops = Shop.query.filter_by(id=shop_id).first()
        if shops:
            abort(409, message="task id taken")

        shop = Shop(id=shop_id, shop_type=args['shop_type'], name=args['name'], contact=args['contact'],
                    workers=args['workers'], debt=args['debt'], date_created=args['date_created'],
                    provider_id=args['provider_id'])
        db.session.add(shop)
        db.session.commit()
        return {'message': 'Shop created successfully'}, 201

    @login_required
    def delete(self, shop_id):
        shop = Shop.query.filter_by(id=shop_id).first()
        pr_sh = ProductShop.query.filter_by(shop_id=shop_id).all()
        for sh in pr_sh:
            db.session.delete(sh)
        db.session.delete(shop)
        db.session.commit()
        return {'message': 'Shop deleted successfully'}

    @login_required
    def put(self, shop_id):
        args = shop_post_args.parse_args()
        shop = Shop.query.filter_by(id=shop_id).first()
        if not shop:
            abort(404, message="shop doesn't exist")
        if args['debt']:
            abort(404, message="you cannot update debt")
        if args['shop_type']:
            shop.shop_type = args['shop_type']
        if args['name']:
            shop.name = args['name']
        if args['contact']:
            shop.contact = args['contact']
        if args['workers']:
            shop.workers = args['workers']
        if args['date_created']:
            shop.date_created = args['date_created']
        if args['provider_id']:
            shop.provider_id = args['provider_id']
        db.session.commit()
        return {'message': 'Shop edited successfully'}


class ProductEditApi(Resource):

    @login_required
    def post(self, product_id):
        args = product_post_args.parse_args()
        products = Product.query.filter_by(id=product_id).first()
        if products:
            abort(409, message="task id taken")

        product = Product(id=product_id, name=args['name'], model=args['model'], date_release=args['date_release'])
        db.session.add(product)
        db.session.commit()
        return {'message': 'Product created successfully'}, 201

    @login_required
    def delete(self, product_id):
        product = Product.query.filter_by(id=product_id).first()
        pr_sh = ProductShop.query.filter_by(shop_id=product_id).all()
        for sh in pr_sh:
            db.session.delete(sh)
        db.session.delete(product)
        db.session.commit()
        return {'message': 'Product deleted successfully'}

    @login_required
    def put(self, product_id):
        args = product_post_args.parse_args()
        products = Product.query.filter_by(id=product_id).first()
        if not products:
            abort(404, message="product doesn't exist")
        if args['name']:
            products.name = args['name']
        if args['model']:
            products.model = args['model']
        if args['date_release']:
            products.date_release = args['date_release']
        db.session.commit()
        return {'message': 'Product eddited successfully'}


api.add_resource(ShopApi, '/api/shop')
api.add_resource(ShopCityApi, '/api/shop/<string:city>')
api.add_resource(ShopDebtApi, '/api/dept')
api.add_resource(ShopItemApi, '/api/shop/<int:item_id>')
api.add_resource(ShopEditApi, '/api/upd-shop/<int:shop_id>')
api.add_resource(ProductEditApi, '/api/upd-product/<int:product_id>')