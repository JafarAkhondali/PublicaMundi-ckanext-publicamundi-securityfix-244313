import re
import zope.interface
import zope.interface.verify
import zope.schema
from zope.schema.interfaces import IVocabularyTokenized
from zope.interface.verify import verifyObject

from ckanext.publicamundi.lib.metadata.ibase import IObject
from ckanext.publicamundi.lib.metadata import vocabularies

_ = lambda t:t

class IThesaurus(IObject):

    name = zope.schema.NativeString(title=_(u'Name'), required=True)
    
    title = zope.schema.TextLine(title=_(u'Title'), required=True)

    reference_date = zope.schema.Date(title=_(u'Date'), required=True)

    date_type = zope.schema.Choice(
        title = _(u'Date Type'),
        vocabulary = vocabularies.get_by_name('date-types').get('vocabulary'),
        required = True)

    version = zope.schema.NativeString(
        title = _(u'Version'),
        constraint = re.compile('^\d+\.\d+(\.[a-z0-9]+)*$').match,
        required = False)

    vocabulary = zope.schema.Object(IVocabularyTokenized, 
        title = _(u'Vocabulary'),
        required = True)

    @zope.interface.invariant
    def check_vocabulary(obj):
        ''' Check that vocabulary provides an IVocabularyTokenized interface.
        Note that, this cannot be done via IObject's field-wise validators because
        target interface is not based on IObject.
        '''
        try:
            verifyObject(IVocabularyTokenized, obj.vocabulary)
        except Exception as ex:
            raise zope.interface.Invalid('Not a vocabulary: %s' %(str(ex)))

class IThesaurusTerms(IObject):

    thesaurus = zope.schema.Object(IThesaurus, 
        title = _(u'Thesaurus'),
        required = True)

    terms = zope.schema.List(
        title = _(u'Terms'),
        value_type = zope.schema.NativeString(title=_(u'Term')),
        required = True,
        min_length = 1,
        max_length = 8)

    def iter_terms():
        '''Provide an iterator on terms.
        '''

    @zope.interface.invariant
    def check_terms(obj):
        unexpected_terms = []
        vocabulary = obj.thesaurus.vocabulary
        for term in obj.terms:
            try:
                vocabulary.getTerm(term)
            except:
                unexpected_terms.append(term)
        if unexpected_terms:
            msg = 'The following terms do not belong to named Thesaurus %r: %s' % (
                obj.thesaurus.title, ','.join(unexpected_terms))
            raise zope.interface.Invalid(msg)

