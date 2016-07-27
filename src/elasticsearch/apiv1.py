from elasticsearch_dsl import Search, Q, A
from elasticsearch_dsl.query import Match
from flask import jsonify, request
from src import api, OpenResource
from .elastic_manager import ElasticSearchManager, elastic_store


class ElasticIndexResource(OpenResource):

    def get(self):

        esm = ElasticSearchManager()
        esm.create_mapping()
        esm.index_products()

        return jsonify({'success': 200, 'message': 'Indexed Data'})

api.add_resource(ElasticIndexResource, '/index/', endpoint='index')


class ElasticProductSearchResource(OpenResource):

    def post(self):

        s = Search(using=elastic_store, index='shop', doc_type='products')
        s.query = Match(name={"query": request.json['keyword'], "type": "phrase", "fuzziness": "AUTO"})
        s = s.suggest('simple_phrase', request.json['keyword'], term={'field': 'name'})
        if 'sort' in request.json and int(request.json['sort']) > 0:
            s = s.sort({'mrp': {"order": "desc", "mode": "max"}})
        if 'sort' in request.json and int(request.json['sort']) < 0:
            s = s.sort({'mrp': {"order": "asc", "mode": "min"}})

        if 'brand_name' in request.json and request.json['brand_name']:
            for brand in request.json['brand_name']:
                s = s.query('bool', should=[Q('match', brand_name=brand)])

        if 'brand_name' not in request.json:
            a = A('terms', field='brand_name.untouched', size=25)
            s.aggs.bucket('brand_names', a)
        if 'price_range' not in request.json:
            a = A('max', field='price')
            s.aggs.bucket('max_price', a)
            a = A('min', field='price')
            s.aggs.bucket('min_price', a)

        if 'price_range' in request.json:
            s = s.filter('range', price={"gte": request.json['price_range'][0], "lte": request.json['price_range'][1]})

        if 'category_name' in request.json and request.json['category_name']:
            for category in request.json['category_name']:
                s = s.query('bool', should=[Q('match', category_name=category)])

        if 'category_name' not in request.json:
            a = A('terms', field='category_name.untouched', size=25)
            s.aggs.bucket('category_name', a)

        size = request.json['size'] if 'size' in request.json else 25
        from_ = request.json['from'] if 'from' in request.json else 0
        s = s.extra(from_=from_, size=size)
        print(s.to_dict())

        return jsonify({'success': 200, 'data': s.execute().to_dict()})

api.add_resource(ElasticProductSearchResource, '/search/products/', endpoint='search_products')


class ElasticRecommendedProductSearchResource(OpenResource):

    def post(self):
        s = Search(using=elastic_store, index='shop', doc_type='products')
        q0 = Q('bool', should=[Q('match', category=request.json['category'])])
        q1 = Q("match", is_recommended=True)
        s.query = q0 & q1
        products = s.execute()
        return jsonify({'success': 200, 'data': products.to_dict()})
api.add_resource(ElasticRecommendedProductSearchResource, '/search/recommended_products/', endpoint='recommended_products')


class ElasticCategoryProductSearchResource(OpenResource):

    def post(self):
        s = Search(using=elastic_store, index='shop', doc_type='products')
        if 'all_category' in request.json:
            s.query = Match(all_categories={"query": request.json['all_category'], "type": "phrase", "fuzziness": "AUTO", 'operator':'AND'})

        size = request.json['size'] if 'size' in request.json else 25
        from_ = request.json['from'] if 'from' in request.json else 0
        s.to_dict()
        s = s.extra(from_=from_, size=size)
        s.extra(random_score={})            
        products = s.execute()
        return jsonify({'success': 200, 'data': products.to_dict()})

api.add_resource(ElasticCategoryProductSearchResource, '/search/category_products/', endpoint='search_category_products')
