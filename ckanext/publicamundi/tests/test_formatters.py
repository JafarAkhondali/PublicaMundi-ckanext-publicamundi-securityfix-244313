# -*- encoding: utf-8 -*-

import datetime
import random
import itertools
import zope.interface
import zope.schema
from zope.interface.verify import verifyObject
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from ckan.plugins import toolkit

# Mock translator before importing our modules!
toolkit._ = lambda s: s

from ckanext.publicamundi.lib.metadata import FieldContext, Object
from ckanext.publicamundi.lib.metadata import IFormatter, formatters
from ckanext.publicamundi.lib.metadata.formatters import formatter_for_field
from ckanext.publicamundi.lib.metadata import schemata
from ckanext.publicamundi.lib.metadata import types
from ckanext.publicamundi.lib.metadata import formatter_for_object
from ckanext.publicamundi.tests import fixtures

def test_objects():
    
    for name in [
            'contact1', 'dt1', 'bbox1', 'foo1', 'thesaurus_gemet_concepts']:
        yield _test_object, name
        yield _test_object_dictize_with_format, name

def _test_object(fixture_name):

    print
    
    x = getattr(fixtures, fixture_name)
    
    formatter = formatter_for_object(x, 'default')
    verifyObject(IFormatter, formatter)
    
    s = formatter.format(x)
    print ' -- format:default %s -- ' %(type(x))
    print s

    format_spec = 'default:precision=4,aa,bb'
    print ' -- format %s -- ' %(format_spec)
    s = format(x, format_spec)
    print s

    format_spec = ''
    print ' -- format <empty-string> -- '
    s = format(x, format_spec)
    print s

    print ' -- format <missing> -- '
    s = format(x)
    print s

def _test_object_dictize_with_format(fixture_name):

    print
   
    x = getattr(fixtures, fixture_name)

    bad_opts = { 'serialize-values': True, 'format-values': 'default',}
    try:
        d = x.to_dict(flat=1, opts=bad_opts)
    except ValueError as ex:
        assert ex.message.find('incompatible') >= 0
    else:
        assert False, 'Method to_dict() should fail: incompatible opts'
    
    opts = { 'format-values': True, }
    d = x.to_dict(flat=1, opts=opts)

    opts = { 'format-values': 'default', }
    d = x.to_dict(flat=1, opts=opts)
    
    opts = { 'format-values': 'default:quote,aa=1,baz,boo', }
    d = x.to_dict(flat=1, opts=opts)
    
    opts = { 'format-values': 'default:precision=3,aa=1,bb', }
    d = x.to_dict(flat=1, opts=opts)
     
    opts = { 'serialize-keys': True, 'key-prefix': 'test1', 'format-values': 'default', }
    d = x.to_dict(flat=1, opts=opts)

    for n in range(1,4):
        opts = { 'format-values': 'default:precision=3,aa=1,bb', 'max-depth': n }
        d = x.to_dict(flat=1, opts=opts)
        opts = { 'format-values': 'default:precision=3,aa=1,bb', 'max-depth': n, 'serialize-keys': 1 }
        d = x.to_dict(flat=1, opts=opts)

def test_field_float():

    print 

    f = zope.schema.Float(title=u'Grade')

    v = random.random() 
    v1 = random.random() 
    
    f = f.bind(FieldContext(key='f', value=v))

    formatter = formatter_for_field(f, 'default')
    verifyObject(IFormatter, formatter)
    
    s = formatter.format(v)
    print ' -- format:default %s -- ' %(type(f))
    print s

def test_field_datetime():

    f = schemata.IFooMetadata.get('created')
    
    v = datetime.datetime.now()
    
    f.validate(v)
    f = f.bind(FieldContext(key='f', value=v))
 
    formatter = formatter_for_field(f, 'default')
    verifyObject(IFormatter, formatter)
    
    s = formatter.format(v)
    print ' -- format:default %s -- ' %(type(f))
    print s
  
    assert formatter.format(v) == v.isoformat()
    assert formatter.format() == v.isoformat()
 
def test_field_choice():

    f = schemata.IFooMetadata.get('thematic_category')
    
    v = 'health'
    f.validate(v)
    f = f.bind(FieldContext(key='f', value=v))
    
    formatter = formatter_for_field(f, 'default')
    verifyObject(IFormatter, formatter)
    
    s = formatter.format(v)
    print ' -- format:default %s -- ' %(type(f))
    print s

    assert formatter.format(v) == u'Health'
    assert formatter.format() == u'Health'

    try:
        formatter.format('not-a-term')
    except ValueError:
        pass
    else:
        assert False, 'The formatter should fail'

def test_field_dicts():

    print 
    
    # [Dict, TextLine]

    f = zope.schema.Dict(
        title = u'A map of keywords',
        key_type = zope.schema.Choice(
            vocabulary = SimpleVocabulary.fromValues(('alpha', 'alpha-el', 'nonsence'))
        ),
        value_type = zope.schema.TextLine(title=u'Keyword')
    ) 
    v = { 
        'alpha': u'alpha', 
        'alpha-el': u'αλφα', 
        'nonsence': u'ειμαι "βράχος"',
    }
    f.validate(v)
    
    for name in ['default']:
        formatter = formatter_for_field(f, name)
        verifyObject(IFormatter, formatter)
        s = formatter.format(v)
        print ' -- format:%s %s -- ' %(name, type(f))
        print s 
   
    # [Dict, *]
    
    f = schemata.IFooMetadata.get('contacts') 
    v = {
        'personal': fixtures.contact1,
        'office': fixtures.contact2,
    }
    f.validate(v)

    for name in ['default']:
        formatter = formatter_for_field(f, name)
        verifyObject(IFormatter, formatter)
        s = formatter.format(v)
        print ' -- format:%s %s -- ' %(name, type(f))
        print s 

def test_field_lists():
    
    print 
    
    # [List, TextLine]

    for name in ['default']:
        f = zope.schema.List(
            title = u'A list of keywords',
            value_type = zope.schema.TextLine(title=u'Keyword')) 
        v = [ u'alpha', u'αλφα', u'ειμαι "βράχος"' ]
        f.validate(v)
        formatter = formatter_for_field(f, name)
        verifyObject(IFormatter, formatter)
        s = formatter.format(v)
        print ' -- format:%s %s -- ' %(name, type(f))
        print s 
    
    # [List, NativeStringLine]

    for name in ['default',]:
        f = zope.schema.List(
            title = u'A list of keywords',
            value_type = zope.schema.NativeStringLine(title=u'Keyword')) 
        v = [ 'alphA', 'beta', 'i am a "rock"' ]
        f.validate(v)
        formatter = formatter_for_field(f, name)
        verifyObject(IFormatter, formatter)    
        s = formatter.format(v)
        print ' -- format:%s %s -- ' %(name, type(f))
        print s 

    # [List, *]
    
    for name in ['default',]:
        f = schemata.IInspireMetadata.get('bounding_box') 
        v = [fixtures.bbox1]
        f.validate(v)
        formatter = formatter_for_field(f, name)
        verifyObject(IFormatter, formatter)
        s = formatter.format(v)
        print ' -- format:%s %s -- ' %(name, type(f))
        print s

    f = zope.schema.List(
        title=u'A list of spatial resolution objects',
        value_type=zope.schema.Object(schema=schemata.ISpatialResolution))
    v = [fixtures.spatialres2, fixtures.spatialres1]
    f = f.bind(FieldContext(key='f', value=v))
    formatter = formatter_for_field(f, 'booo')
    s = formatter.format(v)
    print ' -- format:booo %s -- ' %(type(f))
    print s
   
if __name__ == '__main__':
    
    #_test_object_dictize_with_format('thesaurus_gemet_concepts')
    _test_object_dictize_with_format('foo1')
    _test_object('foo1')
    test_field_lists()
    test_field_dicts()

