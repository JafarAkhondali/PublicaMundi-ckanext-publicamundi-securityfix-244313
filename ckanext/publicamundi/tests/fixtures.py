# -*- encoding: utf-8 -*-

import datetime
import copy

from ckan.lib import create_test_data as _test_data
from ckanext.publicamundi.lib.metadata.types import *

## Basic CKAN packages ##

packages = {
    'ckan': {},
    'foo': {}
}

for pkg in _test_data.gov_items:
    pkg1 = copy.deepcopy(pkg)
    pkg1.update({
        'dataset_type': 'ckan',
        'tags': [{'name': 'gov-data', 'display_name': 'Government Data'}],
        'extras': [],
        'language': 'en',
    })
    packages['ckan'][pkg1['name']] = pkg1 

packages['foo']['hello-foo-1'] = {
    'title': u'Καλημέρα Foo (1)',
    'name': 'hello-foo-1',
    'notes': u'Τρα λαλα λαλλαλαλαλα!',
    'author': u'Κανένας',
    'license_id': 'notspecified',
    'version': '1.0.1b',
    'maintainer': u'Nowhere Man',
    'author_email': 'nowhere-man@example.com',
    'maintainer_email': 'nowhere-man@example.com',
    'tags': [ 
        { 'name': 'hello-world', 'display_name': 'Hello World', }, 
        { 'name': u'test', 'display_name': 'Test' }, 
        { 'name': 'foo', 'display_name': 'Foo' }, 
    ],
    'dataset_type': 'foo',
    'language': 'el',
    'foo': {
        'baz': u'BaoBab',
        'description': u'Τριαλαριλαρο',
        'rating': 9,
        'grade': 5.12,
        'reviewed': False,
        'created': u'2014-09-13T17:00:00',
        'temporal_extent': { 
            'start': '2012-01-01',
            'end': '2013-01-01',
        },
        'thematic_category': 'health',
    },
    'resources': []
}

## Auxiliary objects ##

pt1 = Point(x=0.76, y=0.23)

contact1 = ContactInfo(
    email = u'nowhere-man@example.com', 
    address = PostalAddress(address=u'Nowhere Land', postalcode=u'12321'))

contact2 = ContactInfo(
    email = u'somebody@example.com', 
    address = PostalAddress(address=u'Ακακίας 22', postalcode=u'54321'))

contact3 = ContactInfo(
    email = u'penguin@example.com', 
    address = PostalAddress(address=u'North Pole', postalcode=u'91911'))

poly1 = Polygon(name = u'Poly1', points=[
    Point(x=0.6, y=0.5), Point(x=0.7, y=0.1),
    Point(x=1.6, y=0.2), Point(x=0.6, y=0.5),])

poly2 = Polygon(name = u'Poly2', points=[
    Point(x=7.9, y=0.8), Point(x=1.3, y=0.2),
    Point(x=1.6, y=0.2), Point(x=7.9, y=0.8),])

poly3 = Polygon(name = u'Poly3', points=[
    Point(x=3.6, y=1.8), Point(x=1.5, y=5.2),
    Point(x=1.2, y=7.2), Point(x=3.6, y=1.8),])

dt1 = TemporalExtent(
    start = datetime.date(2014, 5, 27),
    end = datetime.date(2014, 5, 29))

dt2 = TemporalExtent(
    start = datetime.date(1999, 5, 1),
    end = datetime.date.today())

freekeyword1 = FreeKeyword(
    value = u"atmosphere",
    originating_vocabulary = u"Foo-1",
    reference_date = datetime.date.today(),
    date_type = 'creation')

party1 = ResponsibleParty(
    organization = u"Acme Org", 
    email = u"someone@acme.org", 
    role = "resourceProvider")

bbox1 = GeographicBoundingBox(nblat=50.0, sblat=-20.12, wblng=15.0, eblng=20.0)

textent1 = TemporalExtent(start=datetime.date.today(), end=datetime.date(2015,01,01))

conformity1 = Conformity(
    title = u"lala",
    date = datetime.date.today(), 
    date_type = "creation", 
    degree = "conformant")

spatialres1 = SpatialResolution(distance=5, uom=u"m")

spatialres2 = SpatialResolution(denominator=1000)

# Foo

foo1 = FooMetadata(
    identifier = '71adc2bf-b8fd-481e-bd52-2ca86e93df35',
    baz = u'Bazzz',
    title = u'Αβαβούα',
    tags = [ u'alpha', u'beta', u'gamma'],
    url = 'http://example.com/res/1',
    contact_info = ContactInfo(email=u'nomad@somewhere.com', address=None),
    contacts = {
        'personal': ContactInfo(
            publish=False,
            email=u'nobody@example.com', 
            address=PostalAddress(address=u'North Pole', postalcode=u'54321')),
        'office': ContactInfo(
            publish=True,
            email=None, 
            address=PostalAddress(address=u'South Pole', postalcode=u'12345')),
    },
    geometry = [[ poly1, poly2 ]],
    reviewed = False,
    created = datetime.datetime(2014, 06, 11),
    wakeup_time = datetime.time(8, 0, 0),
    description = u'Hello World',
    thematic_category = 'economy',
    temporal_extent = dt1,
    rating = 0,
    grade = 13.7,
    password = u'secret',
)

foo2 = FooMetadata(
    identifier = '71adc2bf-b8fd-481e-bd52-2ca86e93df35',
    baz = u'Baobab',
    title = u'Αβαβούα',
    tags = [ u'alpha', u'beta', u'gamma',],
    url = 'ftp://example.com/res/2',
    description = u'Καλημέρα κόσμος',
    contact_info = ContactInfo(
        email=u'nomad@somewhere.com', 
        address=PostalAddress(address=u'Sahara', postalcode=u'12329')),
    geometry = [[ poly1 ]],
    reviewed = True,
    created = datetime.datetime(2014, 6, 11),
    wakeup_time = datetime.time(8, 30, 0),
    thematic_category = 'health',
    temporal_extent = None,
    rating = 3,
    grade = -2.79,
    password = u'another-secret',
)

foo3 = copy.deepcopy(foo1)
foo3.rating = None
foo3.grade = None

foo4 = copy.deepcopy(foo1)
foo4.geometry = None

foo5 = copy.deepcopy(foo1)
foo5.contacts = None

foo6 = copy.deepcopy(foo1)
foo6.contacts['personal'] = None

foo7 = copy.deepcopy(foo1)
foo7.tags = None

foo8 = copy.deepcopy(foo1)
foo8.contacts.pop('personal')

# Thesaurus

thesaurus_gemet_concepts = Thesaurus(
    title = u'GEMET Concepts',
    name = 'keywords-gemet-concepts',
    reference_date = datetime.date(2014, 1, 1),
    version = '1.0',
    date_type = 'creation'
)

thesaurus_gemet_themes = Thesaurus.lookup('keywords-gemet-themes')

thesaurus_gemet_inspire_data_themes = Thesaurus.lookup('keywords-gemet-inspire-themes')

# BazMetadata 

baz1 = BazMetadata(
    url = 'http://baz.example.com',
    contacts = [contact1, contact2, contact3],
    keywords = ThesaurusTerms(
        terms = ["energy", "agriculture", "climate", "human-health"],
        thesaurus = thesaurus_gemet_themes),
    bbox = bbox1,
    resolution = SpatialResolution(distance=5, uom='km'),
)

baz2 = copy.deepcopy(baz1)
baz2.keywords = None #ThesaurusTerms(thesaurus=Thesaurus(name='keywords-gemet-inspire-themes'))
baz2.resolution = SpatialResolution(denominator=5000) 

# INSPIRE metadata

inspire1 = InspireMetadata(
    contact = [party1],
    datestamp = datetime.date.today(),
    languagecode = "gre",
    title = u"Title",
    identifier = "91b54070-5adb-11e4-8ed6-0800200c9a66",
    abstract = u"This is an abstract description",
    locator = [
        "http://publicamundi.eu",
        "http://www.ipsyp.gr",
        "http://www.example.com"
    ],
    resource_language = ["gre"],
    topic_category = ["biota", "farming", "economy"],
    keywords = {
        'keywords-gemet-themes': ThesaurusTerms(
            terms=["air", "agriculture", "climate"],
            thesaurus=thesaurus_gemet_themes
        ),
        'keywords-gemet-inspire-themes': ThesaurusTerms(
            terms=["buildings", "addresses"],
            thesaurus=thesaurus_gemet_inspire_data_themes,
        ),
    },
    bounding_box = [
        GeographicBoundingBox(nblat=30.0, sblat=0.0, wblng=0.0, eblng=0.0)],
    temporal_extent = [
        TemporalExtent(start=datetime.date(2009,1,1), end=datetime.date(2010,1,1))],
    creation_date = datetime.date(2011,1,1),
    publication_date = datetime.date(2012,1,1),
    revision_date = datetime.date(2013,1,1),
    lineage = u"lineaage",
    spatial_resolution = [
        SpatialResolution(distance=5, uom=u"meters")],
    conformity = [
        Conformity(
            title = u"specifications blabla", 
            date = datetime.date.today(), 
            date_type = 'creation', 
            degree = "not-conformant")
    ],
    access_constraints = [u"lalala1", u"lalala2"],
    limitations = [u"limit1", u"limit2"],
    responsible_party = [
        ResponsibleParty(
            organization=u"Acme Org", email=u"a@acme.example.com", role="originator"), 
        ResponsibleParty(
            organization=u"Coyote Org", email=u"b@coyote.example.com", role="pointOfContact")]
)

inspire2 = copy.deepcopy(inspire1)
inspire2.keywords = None

inspire3 = copy.deepcopy(inspire1)
inspire3.spatial_resolution.append(SpatialResolution(denominator=51000))

inspire4 = copy.deepcopy(inspire1)
inspire4.spatial_resolution = [SpatialResolution(denominator=3),
        SpatialResolution(distance=5, uom=u"meters"), SpatialResolution(denominator=50, distance=2, uom=u"meters")]
#inspire4.spatial_resolution = None
inspire4.conformity = [
        Conformity(
            title = u"specifications blabla", 
            date = datetime.date.today(), 
            date_type = 'creation', 
            degree = "not-evaluated"
            ),
        Conformity(
            title = u"specifications blabla2", 
            date = datetime.date.today(), 
            date_type = 'creation', 
            degree = "conformant"
            )

    ]

