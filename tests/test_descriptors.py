#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010, Nicolas Clairon
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the University of California, Berkeley nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE REGENTS AND CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import unittest

from mongokit import *

class DescriptorsTestCase(unittest.TestCase):
        
    def test_duplicate_required(self):
        class MyDoc(Document):
            structure = {"foo":unicode}
            required_fields = ["foo", "foo"]
        self.assertRaises(DuplicateRequiredError, MyDoc)
    
    def test_flat_required(self):
        class MyDoc(Document):
            structure = {
                "foo":unicode,
            }
            required_fields = ["foo"]
        mydoc = MyDoc()
        self.assertRaises(RequireFieldError, mydoc.validate )
             
    def test_nested_required(self):
        class MyDoc(Document):
            structure = {
                "bla":{
                    "foo":unicode,
                },
            }
            required_fields = ["bla.foo"]
        mydoc = MyDoc()
        self.assertRaises(RequireFieldError, mydoc.validate )

    def test_list_required(self):
        class MyDoc(Document):
            structure = {
                "foo":[]
            }
            required_fields = ["foo"]
        mydoc = MyDoc()
        self.assertRaises(RequireFieldError, mydoc.validate )

    def test_list_required2(self):
        class MyDoc(Document):
            structure = {
                "foo":{int:[]}
            }
            required_fields = ["foo.$int"]
        mydoc = MyDoc()
        self.assertRaises(RequireFieldError, mydoc.validate )


    def test_dict_required(self):
        class MyDoc(Document):
            structure = {
                "foo":{}
            }
            required_fields = ["foo"]
        mydoc = MyDoc()
        self.assertRaises(RequireFieldError, mydoc.validate )

    def test_dict_nested_required(self):
        class MyDoc(Document):
            structure = {
                "foo":{unicode:{"bar":int}}
            }
            required_fields = ["foo.$unicode.bar"]
        mydoc = MyDoc()
        self.assertRaises(RequireFieldError, mydoc.validate )

    def test_default_values(self):
        class MyDoc(Document):
            structure = {
                "foo":int,
                "bla":unicode,
            }
            default_values = {"foo":42}
        mydoc = MyDoc()
        assert mydoc["foo"] == 42
        assert mydoc == {'foo':42, 'bla':None}, mydoc

    def test_default_values_nested(self):
        class MyDoc(Document):
            structure = {
                "bar":{
                    "foo":int,
                    "bla":unicode,
                }
            }
            default_values = {"bar.foo":42}
        mydoc = MyDoc()
        assert mydoc['bar']["foo"] == 42
        assert mydoc == {'bar':{'foo':42, 'bla':None}}, mydoc

    def test_default_values_nested_inheritance(self):
        import datetime
        class Core(Document):
            structure = {
                "core":{
                    "creation_date":datetime.datetime,
                }
            }
            default_values = {
                "core.creation_date": datetime.datetime(2010, 1, 1),
            }

        class MyDoc(Core):
            structure = {
                "bar":{
                    "foo":int,
                    "bla":unicode,
                }
            }
            default_values = {"bar.foo":42}

        class MyDoc2(MyDoc):
            structure = {
                "mydoc2":{
                    "toto":int
                }
            }
        mydoc = MyDoc2()
        assert mydoc['bar']["foo"] == 42
        assert mydoc == {'mydoc2': {'toto': None}, 'core': {'creation_date': datetime.datetime(2010, 1, 1, 0, 0)}, 'bar': {'foo': 42, 'bla': None}}

    def test_default_values_from_function(self):
        import time
        class MyDoc(Document):
            structure = {
                "foo":float
            }
            default_values = {"foo":time.time}
        mydoc = MyDoc()
        mydoc.validate()

    def test_default_values_from_function2(self):
        import time
        class Doc( Document ):
            structure = {
                "doc":{
                    "creation_date":float,
                    "updated_date": float,
                }
            }
            default_values = {
                "doc.creation_date": time.time,
                "doc.updated_date": time.time
            }
        doc = Doc()
        assert isinstance(doc['doc']['creation_date'], float), doc['doc']['creation_date']
        assert isinstance(doc['doc']['updated_date'], float)

    def test_default_values_from_function_nested(self):
        import time
        class MyDoc(Document):
            structure = {
                "foo":{"bar":float}
            }
            default_values = {"foo.bar":time.time}
        mydoc = MyDoc()
        mydoc.validate()
        assert mydoc['foo']['bar'] > 0

    def _test_default_values_from_function_througt_types(self):
        # XXX TODO
#        class MyDoc(Document):
#            structure = {
#                "foo":{int:float}
#            }
#            default_values = {"foo.$int":time.time}
#        mydoc = MyDoc()
#        mydoc.validate()
#        # can't go througt types, because no values
#        assert mydoc['foo'] == {}

        # but
        import time
        class MyDoc(Document):
            structure = {
                "foo":{int:float}
            }
            default_values = {"foo":{3:time.time}}
        mydoc = MyDoc()
        mydoc.validate()
        assert mydoc['foo'][3] > 0
     
    def test_default_list_values(self):
        class MyDoc(Document):
            structure = {
                "foo":[int]
            }
            default_values = {"foo":[42,3]}
        mydoc = MyDoc()
        assert mydoc["foo"] == [42,3]
        mydoc.validate()

    def test_default_list_nested_values(self):
        class MyDoc(Document):
            structure = {
                "foo":{
                    "bar":[int]
                }
            }
            default_values = {"foo.bar":[42,3]}
        mydoc = MyDoc()
        assert mydoc["foo"]["bar"] == [42,3]

    def test_default_dict_values(self):
        class MyDoc(Document):
            structure = {
                "foo":{}
            }
            default_values = {"foo":{"bar":42}}
        mydoc = MyDoc()
        assert mydoc["foo"] == {"bar":42}, mydoc
         
    def test_default_dict_checked_values(self):
        class MyDoc(Document):
            structure = {
                "foo":{unicode:int}
            }
            default_values = {"foo":{u"bar":42}}
        mydoc = MyDoc()
        assert mydoc["foo"] == {"bar":42}, mydoc

    def test_default_dict_nested_checked_values(self):
        class MyDoc(Document):
            structure = {
                "foo":{unicode:{"bla":int, "ble":unicode}}
            }
            default_values = {"foo":{u"bar":{"bla":42, "ble":u"arf"}}}
        mydoc = MyDoc()
        assert mydoc["foo"] == {u"bar":{"bla":42, "ble":u"arf"}}, mydoc
           
    def test_validators(self):
        class MyDoc(Document):
            structure = {
                "foo":unicode,
                "bar":{
                    "bla":int
                }
            }
            validators = {
                "foo":lambda x: x.startswith("http://"),
                "bar.bla": lambda x: x > 5
            }
        mydoc = MyDoc()
        mydoc["foo"] = u"google.com"
        self.assertRaises(ValidationError, mydoc.validate)
        mydoc["foo"] = u"http://google.com"
        print mydoc
        mydoc.validate()
        mydoc['bar']['bla'] = 2
        self.assertRaises(ValidationError, mydoc.validate)
        mydoc['bar']['bla'] = 42
        mydoc.validate()

    def test_validators_througt_types(self):
        class MyDoc(Document):
            structure = {
                "bar":{
                    int:{"bla":int}
                }
            }
            validators = {
                "bar.$int.bla": lambda x: x > 5
            }
        mydoc = MyDoc()
        mydoc['bar'].update({3:{'bla': 15}})
        self.assertRaises(InvalidDocument, mydoc.validate)

    def test_multiple_validators(self):
        class MyDoc(Document):
            structure = {
                "foo":unicode,
            }
            validators = {
                "foo":[lambda x: x.startswith("http://"),lambda x: x.endswith(".com")],
            }
        mydoc = MyDoc()
        mydoc["foo"] = u"google.com"
        self.assertRaises(ValidationError, mydoc.validate)
        mydoc["foo"] = u"http://google.fr"
        self.assertRaises(ValidationError, mydoc.validate)
        mydoc["foo"] = u"http://google.com"
        mydoc.validate()

    def test_complexe_validation(self):
        class MyDoc(Document):
            structure = {
                "foo":unicode,
                "bar":{
                    "bla":int
                }
            }
            def validate(self):
                if self['bar']['bla']:
                    self['foo'] = unicode(self['bar']['bla'])
                else:
                    self['foo'] = None
                super(MyDoc, self).validate()

        mydoc = MyDoc()
        mydoc['bar']['bla'] = 4
        assert mydoc['foo'] is None
        mydoc.validate()
        assert mydoc['foo'] == "4", mydoc['foo']
        mydoc['bar']['bla'] = None
        mydoc.validate()
        assert mydoc['foo'] is None

    def test_complexe_validation2(self):
       
        class MyDoc(Document):
            structure = {
                "foo":unicode,
                "bar":{"bla":unicode}
            }
            default_values = {"bar.bla":3}
            def validate(self):
                self["bar"]["bla"] = unicode(self["bar"]["bla"])
                self["foo"] = unicode(self["foo"])
                super(MyDoc, self).validate()

        mydoc = MyDoc()
        mydoc['foo'] = 4
        mydoc.validate()
        assert mydoc['foo'] == "4", mydoc['foo']
        assert mydoc["bar"]["bla"] == "3", mydoc

    def test_complexe_validation3(self):
        class MyDoc(Document):
            structure = {
                "foo":unicode,
                "bar":{
                    "bla":int
                },
                "ble":unicode,
            }
            def validate(self):
                if self['bar']['bla'] is not None:
                    self['foo'] = unicode(self['bar']['bla'])
                else:
                    self['foo'] = None
                self["ble"] = self["foo"]
                super(MyDoc, self).validate()

        mydoc = MyDoc()
        mydoc['bar']['bla'] = 4
        assert mydoc['foo'] is None
        mydoc.validate()
        assert mydoc['foo'] == "4"
        assert mydoc["ble"] == "4"
        mydoc['bar']['bla'] = None
        mydoc.validate()
        assert mydoc['foo'] is None
        assert mydoc['ble'] is None

    def test_bad_default_values(self):
        class MyDoc(Document):
            structure = {
                "foo":{"bar":int},
            }
            default_values = {"foo.bla":2}
        self.assertRaises(ValueError, MyDoc)

    def test_bad_validators(self):
        class MyDoc(Document):
            structure = {
                "foo":{"bar":int},
            }
            validators = {"foo.bla":lambda x:x}
        self.assertRaises(ValueError, MyDoc)

    def test_bad_required(self):
        class MyDoc(Document):
            db_name = "test"
            collection_name = "mongokit"
            structure = {
                "profil":{
                    "screen_name":unicode,
                    "age":int
                }
            }
            required_fields = ['profil.screen_nam']

        self.assertRaises( ValueError, MyDoc )
        
    def test_nested_structure2(self):
        class MyDoc(Document):
            db_name = "test"
            collection_name = "mongokit"
            structure = {
                unicode:{int:int}
            }

        mydoc = MyDoc()
        assert mydoc._namespaces == ['$unicode', '$unicode.$int']
  
