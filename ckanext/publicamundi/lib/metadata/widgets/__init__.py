import re
import zope.interface
import zope.interface.verify
import zope.schema
import logging

from ckanext.publicamundi.lib.memoizer import memoize
from ckanext.publicamundi.lib.metadata.fields import *
from ckanext.publicamundi.lib.metadata.fields import (
    build_adaptee, check_multiadapter_ifaces)
from ckanext.publicamundi.lib.metadata import (
    adapter_registry, factory_for, IObject, Object, FieldContext)

from .ibase import (
    IQualAction, ILookupContext, 
    IWidget, IFieldWidget, IObjectWidget)

logger = logging.getLogger(__name__)

class QualAction(object):
    '''A qualified action that we need to perform and search a widget for.
    '''

    zope.interface.implements(IQualAction)
    
    __slots__ = ('action', 'qualifier')

    def __init__(self, action=None, qualifier=None):
        IQualAction.get('action').validate(action)
        self.action = action
        IQualAction.get('qualifier').validate(qualifier)
        self.qualifier = qualifier

    def to_string(self):
        '''Stringify as <action>:<qualifier>'''
        return self.action + \
            (':' + self.qualifier if self.qualifier else '')
   
    __str__ = to_string

    __repr__ = to_string

    def parents(self):
        p = []
        qualifier_parts = self.qualifier.split('.') if self.qualifier else []
        p.append(QualAction(self.action))
        for i in range(1, len(qualifier_parts)):
            p.append(QualAction(
                self.action, qualifier='.'.join(qualifier_parts[:i])))
        return p

    def make_child(self, child_qualifier):
        assert re.match('[a-z][_a-z0-9]+$', child_qualifier), \
            'Not a valid path component for a dotted name'
        q = self.qualifier + '.' + child_qualifier if self.qualifier else child_qualifier
        return QualAction(self.action, q)

    @classmethod
    def from_string(cls, q):
        ''' Parse <action>:<qualifier> '''
        try:
            action, qualifier = q.split(':')
        except:
            action, qualifier = q, None
        return cls(action, qualifier)
 
class LookupContext(object):
    '''Provide a context for widget adaptation.
    
    Essentially, this context is the part of adaptation that does not contain the
    adaptee vector (which is anyway available to the adapter as an init argument). 
    
    It will be available to (successfully adapted) widgets, under their `context`
    attribute.
    '''
    
    zope.interface.implements(ILookupContext)

    __slots__ = ('requested_action', 'provided_action')
    
    def __init__(self, requested=None, provided=None):
        self.requested_action = requested
        self.provided_action = provided

class WidgetNotFound(LookupError):
    '''An exception that represents a widget lookup (adaptation) failure.
    '''

    def __init__(self, qualified_action, r):
        self.qualified_action = qualified_action
        self.r = r

    def __str__(self):
        return 'Cannot find a widget for %s for action "%s"' % (
            type(self.r).__name__, self.qualified_action)

# Decorators for widget adapters

def decorator_for_widget_multiadapter(required_ifaces, provided_iface, qualifiers, is_fallback):
    def decorate(widget_cls):
        assert provided_iface.implementedBy(widget_cls) 
        names = set()
        action = widget_cls.action
        if is_fallback or not qualifiers:
            names.add(action)
        for qualifier in qualifiers:
            q = QualAction(action=action, qualifier=qualifier)
            names.add(q.to_string())
        for name in names:
            adapter_registry.register(
                required_ifaces, provided_iface, name, widget_cls)
        return widget_cls
    return decorate
   
def field_widget_adapter(field_iface, qualifiers=[], is_fallback=False):
    assert field_iface.extends(IField)
    decorator = decorator_for_widget_multiadapter(
        [field_iface], IFieldWidget, qualifiers, is_fallback)
    return decorator

def field_widget_multiadapter(required_ifaces, qualifiers=[], is_fallback=False):
    check_multiadapter_ifaces(required_ifaces) 
    decorator = decorator_for_widget_multiadapter(
        required_ifaces, IFieldWidget, qualifiers, is_fallback)
    return decorator
      
def object_widget_adapter(object_iface, qualifiers=[], is_fallback=False):
    assert object_iface.isOrExtends(IObject)
    decorator = decorator_for_widget_multiadapter(
        [object_iface], IObjectWidget, qualifiers, is_fallback)
    return decorator

# Utilities

def widget_for_object(qualified_action, obj, errors={}):
    '''Find and instantiate a widget to adapt an object to a widget interface.
    '''
    
    # Build an array with all candidate names
    
    q = qualified_action
    if isinstance(q, basestring):
        q = QualAction.from_string(q)
    candidates = list(reversed(q.parents() + [q]))

    # Lookup registry
    
    widget = None
    for candidate in candidates:
        name = candidate.to_string()
        widget = adapter_registry.queryMultiAdapter([obj], IObjectWidget, name)
        logger.debug('Trying to adapt [%s] to widget for action %s: %r',
            type(obj).__name__, name, 
            widget if widget else None)
        if widget:
            break
    
    if widget:
        widget.context = LookupContext(requested=q, provided=candidate)
        widget.errors = errors
    else:
        raise WidgetNotFound(qualified_action, obj)
    
    # Found a widget to adapt to obj
    
    assert zope.interface.verify.verifyObject(IObjectWidget, widget)
    return widget

def widget_for_field(qualified_action, field, errors={}):
    '''Find and instantiate a widget to adapt a field to a widget interface.
    The given field should be a bound instance of zope.schema.Field.
    '''
    
    # Build a list with candidate names
    
    q = qualified_action
    if isinstance(q, basestring):
        q = QualAction.from_string(q)
    candidates = list(reversed(q.parents() + [q]))

    # Build adaptee vector
    
    adaptee = build_adaptee(field, expand_collection=True)

    # Lookup registry
    
    widget = None
    while len(adaptee):
        for candidate in candidates:
            name = candidate.to_string()
            widget = adapter_registry.queryMultiAdapter(adaptee, IFieldWidget, name)
            logger.debug('Trying to adapt [%s] to widget for action %s: %r',
                ', '.join([type(x).__name__ for x in adaptee]), name, 
                widget if widget else None)
            if widget:
                break
        if widget:
            break
        # Fall back to a more general version of this adaptee    
        adaptee.pop()
    
    if widget:
        widget.context = LookupContext(requested=q, provided=candidate)
        widget.errors = errors
    else:
        raise WidgetNotFound(qualified_action, field)
    
    # Found
    
    assert zope.interface.verify.verifyObject(IFieldWidget, widget)
    return widget

def markup_for_field(qualified_action, field, errors={}, name_prefix='', data={}):
    assert isinstance(field, zope.schema.Field)
    widget = widget_for_field(qualified_action, field, errors)
    return widget.render(name_prefix, data)

def markup_for_object(qualified_action, obj, errors={}, name_prefix='', data={}):
    assert isinstance(obj, Object)
    widget = widget_for_object(qualified_action, obj, errors)
    return widget.render(name_prefix, data)

markup_for = markup_for_object

# Import actual widgets

from . import base
from . import fields
from . import objects

# Import markup formatters (bridge with IFormatter)

from . import markup_formatters

