from unittest import TestCase

import jsonschema
import seep.core
import collections


class TestInstantiate(TestCase):
    def test_it_sets_defaults(self):
        data = {}
        schema = {"properties" : {"foo" : {"default" : 12}}}
        seep.core.instantiate(data, schema)
        self.assertEqual(data, {"foo" : 12})

    def test_it_sets_nested_defaults(self):
        data = {}
        schema = {
            "properties" : {
                "foo" : {
                    "default" : {},
                    "properties" : {"bar" : {"default" : []}},
                }
            }
        }
        seep.core.instantiate(data, schema)
        self.assertEqual(data, {"foo" : {"bar" : []}})

    def test_it_sets_multiple_nested_defaults(self):
        data = {}
        schema = {
            "properties" : {
                "bar" : {"default" : 123},
                "foo" : {
                    "default" : {},
                    "properties" : {
                        "bar" : {
                            "properties": {"baz" : {"default" : []}},
                        },
                    },
                },
            }
        }
        seep.core.instantiate(data, schema)
        self.assertEqual(data, {"bar": 123, "foo" : {"bar" : {"baz" : []}}})

    def test_identity_instantiate(self):
        data = {"foo" : 12}
        schema = {"properties" : {"foo" : {}}}
        seep.core.instantiate(data, schema)
        self.assertEqual(data, {"foo" : 12})

    def test_validation_errors_are_still_errors(self):
        with self.assertRaises(jsonschema.ValidationError):
            seep.core.instantiate("foo", {"type" : "integer"})

    def test_validation_default_and_required_before_properties(self):
        data = {}
        schema = collections.OrderedDict()
        schema['required'] = ["foo"]
        schema['properties'] = {
            "foo": {
                "default": 14,
                "type": "integer"}
        }

        seep.core.instantiate(data, schema)
        self.assertEqual(data, {"foo": 14})

    def test_validation_default_and_required_after_properties(self):
        data = {}
        schema = collections.OrderedDict()
        schema['properties'] = {
            "foo": {
                "default": 14,
                "type": "integer"}
        }
        schema['required'] = ["foo"]

        seep.core.instantiate(data, schema)
        self.assertEqual(data, {"foo": 14})

    def test_validation_error_required_no_default_after_properties(self):
        data = {}
        schema = collections.OrderedDict()
        schema['properties'] = {
            "foo": {
                "type": "integer"}
        }
        schema['required'] = ["foo"]
        with self.assertRaises(jsonschema.exceptions.ValidationError):
            seep.core.instantiate(data, schema)

    def test_validation_error_required_no_default_before_properties(self):
        data = {}
        schema = collections.OrderedDict()
        schema['required'] = ["foo"]
        schema['properties'] = {
            "foo": {
                "type": "integer"}
        }
        with self.assertRaises(jsonschema.exceptions.ValidationError):
            seep.core.instantiate(data, schema)

    def test_validation_nested_required_with_default(self):
        data_1 = {}
        data_2 = {"foo": {}}
        schema = collections.OrderedDict()
        schema['required'] = ['foo']
        schema['properties'] = {
            "foo": {
                "default": {},
                "required": ["bar"],
                "properties": {
                    "bar": {
                        "type": "integer",
                        "default": 12
                    }
                }}
        }

        seep.core.instantiate(data_1, schema)
        self.assertEqual(data_1, {"foo": {"bar": 12}})

        seep.core.instantiate(data_2, schema)
        self.assertEqual(data_2, {"foo": {"bar": 12}})

    def test_validation_nested_required_without_default(self):
        data_1 = {}
        data_2 = {"foo": {}}
        data_3 = {"foo": {"bar": 12}}
        schema = collections.OrderedDict()
        schema['required'] = ['foo']
        schema['properties'] = {
            "foo": {
                "required": ["bar"],
                "properties": {
                    "bar": {
                        "type": "integer",
                    }
                }}
        }
        with self.assertRaises(jsonschema.exceptions.ValidationError):
            seep.core.instantiate(data_1, schema)

        with self.assertRaises(jsonschema.exceptions.ValidationError):
            seep.core.instantiate(data_2, schema)

        seep.core.instantiate(data_3, schema)
        self.assertEqual(data_3, {"foo": {"bar": 12}})

    def test_validation_top_level_not_required(self):
        data_1 = {}
        data_2 = {"foo": {}}
        schema = collections.OrderedDict()
        schema['properties'] = {
            "foo": {
                "required": ["bar"],
                "properties": {
                    "bar": {
                        "type": "integer",
                    },
                }}
        }

        seep.core.instantiate(data_1, schema)
        self.assertEqual(data_1, {})

        with self.assertRaises(jsonschema.exceptions.ValidationError):
            seep.core.instantiate(data_2, schema)

    def test_validation_nested_mix_required_and_default(self):
        data_1 = {"foo": {}}
        data_2 = {"foo": {"bar": 12}}
        schema = collections.OrderedDict()
        schema['properties'] = {
            "foo": {
                "required": ["bar"],
                "properties": {
                    "bar": {
                        "type": "integer",
                    },
                    "baz": {
                        "type": "integer",
                        "default": 12
                    }
                }}
        }

        with self.assertRaises(jsonschema.exceptions.ValidationError):
            seep.core.instantiate(data_1, schema)

        seep.core.instantiate(data_2, schema)
        self.assertEqual(data_2, {"foo": {"bar": 12, "baz": 12}})
