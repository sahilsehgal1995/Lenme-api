from sqlalchemy import select, func
from sqlalchemy.ext.hybrid import hybrid_property
from src import db, BaseMixin, ReprMixin

tax_to_product = db.Table('tax_to_product', db.metadata,
                          db.Column('id', db.Integer, primary_key=True),
                          db.Column('tax_id', db.Integer, db.ForeignKey('taxes.id')),
                          db.Column('product_id', db.Integer, db.ForeignKey('product.id'))
                          )


class SimilarProductMapping(db.Model, BaseMixin):

    id = db.Column( db.Integer, primary_key=True)
    similar_product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    similar_product = db.relationship('Product', foreign_keys=[similar_product_id])


class ProductQuantityMapping(db.Model, BaseMixin):

    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity_product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.relationship('Product', foreign_keys=[quantity_product_id])
    # product = db.relationship('Product', foreign_keys=[self_product_id], backref='quantities')


class ProductStockPinCode(db.Model, BaseMixin):

    product_stock_id = db.Column(db.Integer, db.ForeignKey('product_stock.id'))
    pin_code_id = db.Column(db.Integer, db.ForeignKey('pin_code.id'))
    stocks = db.relationship('ProductStock')
    pin_codes = db.relationship('PinCode')


class Shop(db.Model, ReprMixin, BaseMixin):
    name = db.Column(db.String(127))
    address = db.Column(db.Text())
    locality = db.Column(db.Text())
    city = db.Column(db.Text())
    pin_code = db.Column(db.Text())

    owner = db.relationship('User', backref='shop', uselist=False)

    @hybrid_property
    def owner_name(self):
        return self.owner.first_name + self.owner.last_name

    @hybrid_property
    def total_stock(self):
        return str(ProductStock.query.with_entities(func.sum(ProductStock.stock)).filter(ProductStock.shop_id == self.id).all()[0][0])

    @hybrid_property
    def total_products(self):

        products = ProductStock.query.with_entities(func.count(ProductStock.product_id))\
            .filter(ProductStock.shop_id == self.id).distinct(ProductStock.product_id).all()[0][0]
        return str(products)


class Category(db.Model, ReprMixin, BaseMixin):

    name = db.Column(db.String(127))
    parent_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    parent = db.relationship('Category', remote_side='Category.id')
    children = db.relationship('Category', remote_side='Category.parent_id')
    products = db.relationship('Product', uselist=True, backref='category', lazy='dynamic')


class ProductRate(db.Model, BaseMixin):

    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    min_quantity = db.Column(db.Integer)
    max_quantity = db.Column(db.Integer)
    rate = db.Column(db.Float(precision=2))

    product = db.relationship('Product', backref='rates', cascade='delete')


class Product(db.Model, ReprMixin, BaseMixin):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'))
    picture = db.Column(db.String(512), nullable=True)
    price = db.Column(db.Integer, nullable=False)
    local_price = db.Column(db.Integer, nullable=False)
    market_price = db.Column(db.Integer, nullable=True)
    quantity = db.Column(db.String(255), nullable=True)
    in_stock = db.Column(db.Boolean(True))
    is_bulk_discounted = db.Column(db.Boolean(False))
    is_new = db.Column(db.Boolean(False))
    review_count = db.Column(db.Integer, nullable=True, default=0)
    rating = db.Column(db.Integer, nullable=True, default=0)
    color = db.Column(db.String(80), nullable=True)
    is_recommended = db.Column(db.Boolean(False))
    discount = db.Column(db.Float(precision=2), nullable=True, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    description = db.relationship('Description', uselist=False, backref='product')
    taxes = db.relationship('Taxes', secondary=tax_to_product, backref='products')

    similar_quantity_products = db.relationship('ProductQuantityMapping', foreign_keys=[ProductQuantityMapping.product_id])
    product_stocks = db.relationship('ProductStock', backref='product_available', lazy='dynamic')

    @hybrid_property
    def brand_name(self):
        return self.brand.name

    @hybrid_property
    def is_bulk_discounted(self):
        return bool(self.rates)

    @hybrid_property
    def mrp(self):
        return self.local_price + sum([float(i.tax_percentage/100 * self.local_price) for i in self.taxes])

    @hybrid_property
    def local_mrp(self):
        return self.price + sum([float(i.tax_percentage / 100 * self.price) for i in self.taxes])

    @hybrid_property
    def category_name(self):
        return self.category.name

    @hybrid_property
    def parent_category(self):
        return self.category.parent.name

    @hybrid_property
    def grand_parent_category(self):
        if self.category.parent:
            if self.category.parent.parent:
                return self.category.parent.parent.name
            return self.category.parent.name
        return ''

    @hybrid_property
    def all_categories(self):
        categories = [self.category.name]
        parent = self.category
        while parent.parent:
            parent = parent.parent
            categories.append(parent.name)
        return categories

    @hybrid_property
    def base_category(self):
        parent = self.category
        while parent.parent:
            parent = parent.parent
        return parent.name


class Taxes(db.Model, BaseMixin):

    tax_type = db.Column(db.String(55))
    tax_percentage = db.Column(db.Float(precision=2))
    is_cascading = db.Column(db.Boolean(False))


class Rating(db.Model, BaseMixin):

    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    rating = db.Column(db.Enum('1', '2', '3', '4', '5'), default='1')


class Brand(db.Model, BaseMixin, ReprMixin):

    name = db.Column(db.String(255))
    products = db.relationship('Product', uselist=True, lazy='dynamic', backref='brand')


class Description(db.Model, BaseMixin):

    description = db.Column(db.Text())
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))


class ProductImage(db.Model, BaseMixin):

    image = db.Column(db.String(512), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    product = db.relationship('Product', backref='images', uselist=False, cascade='all')


class SpecificDetails(db.Model, BaseMixin):

    details = db.Column(db.Text())
    documentation = db.Column(db.String(255))
    warranty = db.Column(db.String(255))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))


class CustomerQuestion(db.Model, BaseMixin):

    question = db.Column(db.String(255))
    votes = db.Column(db.Integer)
    answer_count = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class CustomerAnswer(db.Model, BaseMixin):

    answer = db.Column(db.Text())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('customer_question.id'))


class CustomerAnswerImages(db.Model, BaseMixin):

    customer_answer_images = db.Column(db.String(512), nullable=True)
    customer_answer_id = db.Column(db.Integer, db.ForeignKey('customer_answer.id'))


class PinCode(db.Model, BaseMixin):

    pin_code = db.Column(db.Integer)
    stocks = db.relationship('ProductStockPinCode', back_populates='pin_codes')


class ProductStock(db.Model, BaseMixin):

    delivery_charge = db.Column(db.Float(precision=2))
    delivery_time = db.Column(db.Integer)
    stock = db.Column(db.Integer)

    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'))

    shop = db.relationship('Shop', backref='shop_stocks')
    product = db.relationship('Product', backref='product_availability')
    pin_codes = db.relationship('ProductStockPinCode', back_populates='stocks')

    @hybrid_property
    def pin_code_list(self):
        return [pin_code.pin_code for pin_code in self.pin_codes]

    @pin_code_list.expression
    def pin_code_list(self):
        return select([PinCode.pin_code]).where(PinCode.pin_code.in_(self.pin_code_list)).as_scalar()


class OfferImage(db.Model, BaseMixin, ReprMixin):

    name = db.Column(db.String(127), nullable=True)
    image = db.Column(db.String(127), nullable=True)
    expiry = db.Column(db.DateTime())