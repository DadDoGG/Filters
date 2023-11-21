from flask import redirect, url_for
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.fields import QuerySelectField
from flask_login import login_required, current_user

from filters import app
from filters.models import *
from filters.routes import logout


class BaseModelView(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated:
            return True
        return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        if current_user.is_authenticated:
            return True
        return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))


class ProductShopView(BaseModelView):
    column_display_pk = True
    column_hide_backrefs = False
    column_list = ('shop_id', 'product_id')


class ShopView(BaseModelView):
    column_display_pk = True
    column_hide_backrefs = False
    column_list = ('shop_type', 'name', 'contact', 'workers', 'debt', 'date_created', 'provider_id', 'id')

    form_extra_fields = {
        'provider': QuerySelectField('Provider', query_factory=lambda: Shop.query.all(), allow_blank=True),
    }

    def on_model_change(self, form, model, is_created):
        model.provider_id = form.provider.data.id if form.provider.data else None


class BackHomeView(BaseView):
    @expose('/')
    def back_home(self):
        return self.render('main.html')


class LogoutView(BaseView):
    @expose('/')
    def back_home(self):
        return logout()


class ShopAdminView(BaseView):
    @expose('/')
    def any_shop(self, *args, **kwargs):
        city = args
        if city:
            shops = Shop.query.all()
            for shop in shops:
                for key, value in shop.contact.items():
                    if key == "city" and value == city:
                        shops = Shop.query.get(id=shop.id)
        else:
            shops = Shop.query.all()

        return self.render('shop.html', shops=shops)

    @expose("/<int:shop_id>/")
    def current_shop(self, shop_id):
        shop = Shop.query.get_or_404(shop_id)
        return self.render('current_shop.html', shop=shop)

    @expose("/<int:shop_id>/del")
    @login_required
    def del_debt(self, shop_id):
        shop = Shop.query.get_or_404(shop_id)
        shop.debt = 0
        db.session.commit()

        return self.render('current_shop.html', shop=shop)

    def is_accessible(self):
        if current_user.is_authenticated:
            return True
        return False


class UserView(BaseModelView):
    column_display_pk = True
    column_hide_backrefs = False
    column_list = ('login', 'email', 'permission', 'is_active')


admin = Admin(app, name="Главная", template_mode='bootstrap3', index_view=MyAdminIndexView())

admin.add_view(ShopView(Shop, db.session, name='Магазины'))
admin.add_view(UserView(User, db.session, name='Пользователи'))
admin.add_view(BaseModelView(Product, db.session, name='Товары'))
admin.add_view(ProductShopView(ProductShop, db.session, name='Продаваемые продукты'))
admin.add_view(ShopAdminView(name='Магазины'))
admin.add_view(BackHomeView(name='На главную'))
admin.add_view(LogoutView(name='Выйти'))

