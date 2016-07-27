import elasticsearch
from elasticsearch.exceptions import TransportError

from src import elastic_store
from src.products.schemas import Product, ProductSchema
from .mapping import elastic_mapping


class ElasticSearchManager(object):

    mapping = elastic_mapping
    index_name = 'shop'
    indices_es = elasticsearch.client.IndicesClient(elastic_store)

    def create_mapping(self):
        try:
            self.indices_es.delete(index=self.index_name)
        except TransportError as e:
            print(e)
            pass
        try:
            self.indices_es.create(index=self.index_name, body=self.mapping)
        except TransportError as e:
            print(e)
            pass
        try:
            self.indices_es.put_mapping(index=self.index_name, doc_type='products', body=self.mapping['mappings']['products'])
        except TransportError as e:
            print(e)
            pass

    def index_products(self):

        products = Product.query.all()
        for product in products:
            elastic_store.index(index=self.index_name, doc_type='products', id=product.id,
                                body=ProductSchema(exclude=('similar_products', 'product_stocks', 'local_price', 'local_mrp'))
                                .dump(product).data)
            print(product.id)

        return True

    def index_product(self, product_id):

        product = Product.query.get(product_id)
        elastic_store.index(index=self.index_name, doc_type='products', id=product.id,
                            body=ProductSchema(exclude=('similar_products', 'product_stocks', 'local_price', 'local_mrp'))
                            .dump(product).data)
        print(product.id)

        return True
