from marshmallow import pre_load
from flask import json

from src import BaseSchema, ma
from src.admin_panel.models import Log


class LogSchema(BaseSchema):

    class Meta:
        model = Log

    id = ma.Integer(load=True)

    @pre_load
    def save_data(self, in_data):
        if 'updated_data' in in_data:
            try:
                in_data['updated_data'] = json.dumps(in_data['updated_data'])
            except (ValueError, TypeError) as e:
                print(e)
        return in_data
