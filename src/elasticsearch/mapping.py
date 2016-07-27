elastic_mapping = {
    "mappings": {
        "products": {
            "properties": {
                "base_category": {
                    "type": "string"
                },
                "brand_name": {
                    "type": "string",
                    "fields": {
                        "untouched": {
                            "type": "string",
                            "index": "not_analyzed"
                        }
                    }
                },
                "category_name": {
                    "type": "string",
                    "fields": {
                        "untouched": {
                            "type": "string",
                            "index": "not_analyzed"
                        }
                    }
                },
                "category": {
                    "type": "nested",
                    "properties": {
                        "id": {
                            "type": "long"
                        },
                        "name": {
                            "type": "string"
                        },
                        "parent": {
                            "properties": {
                                "id": {
                                    "type": "long"
                                },
                                "name": {
                                    "type": "string"
                                },
                                "parent": {
                                    "properties": {
                                        "id": {
                                            "type": "long"
                                        },
                                        "name": {
                                            "type": "string"
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "description": {
                    "type": "nested",
                    "properties": {
                        "description": {
                            "type": "string"
                        },
                        "id": {
                            "type": "long"
                        },
                        "product": {
                            "type": "long"
                        },
                        "product_id": {
                            "type": "object"
                        }
                    }
                },
                "grand_parent_category": {
                    "type": "string"
                },
                "id": {
                    "type": "long"
                },
                "name": {
                    "type": "string"
                },
                "parent_category": {
                    "type": "string"
                },
                "price": {
                    "type": "long"
                },
                "taxes": {
                    "properties": {
                        "id": {
                            "type": "long"
                        },
                        "tax_percentage": {
                            "type": "double"
                        },
                        "tax_type": {
                            "type": "string"
                        }
                    }
                }
            }
        }
    }
}
