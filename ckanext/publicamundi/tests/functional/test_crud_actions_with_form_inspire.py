# -*- encoding: utf-8 -*-

import json
import webtest
import nose.tools
from nose.plugins.skip import SkipTest
import inflection
import datadiff
import logging
from datadiff.tools import assert_equal

from ckan.tests import CreateTestData
from ckan.tests import TestController as BaseTestController

from ckanext.publicamundi.lib import dictization

log1 = logging.getLogger(__name__)

## Tests ##

class TestController(BaseTestController):

    basic_fields = set([
        'name', 'title', 'notes', 
        'maintainer', 'maintainer_email', 'author', 'author_email', 
        'version', 'license_id',
    ])
 
    request_headers = {}

    request_environ = {
        'REMOTE_USER': 'tester',
    }

    def __init__(self):
        BaseTestController.__init__(self)
        self.app.extra_environ.update(self.request_environ)
    
    @classmethod
    def setup_class(cls):
        CreateTestData.create_user('tester', about='A tester', password='tester')
        return

    @classmethod
    def teardown_class(cls):
        pass
    
    # Note: webtest 1.4.3 (pulled from CKAN requirments) will fail to parse a 
    # form with <select multiple> fields. So, following tests are disabled.
    _skip_message = u'webtest fails to parse form with <select multiple/>'

    @nose.tools.istest
    def test_1_create_package(self):
        raise SkipTest(self._skip_message)    
        
        yield self._create_package, 'hello-inspire-1'
    
    @nose.tools.istest
    def test_2_update_package(self):
        raise SkipTest(self._skip_message)    
    
        yield self._update_package, 'hello-inspire-1', '0..1'
        #yield self._update_package, 'hello-foo-1', '1..2'
     
    @nose.tools.istest
    def test_3_create_resource(self):
        raise SkipTest(self._skip_message)    
    
        yield self._create_resource, 'hello-inspire-1', 'resource-1'
        #yield self._create_resource, 'hello-foo-1', 'resource-2'
     
    @nose.tools.istest
    def test_4_update_resource(self):
        raise SkipTest(self._skip_message)    
    
        yield self._update_resource, 'hello-inspire-1', 'resource-1', '0..1'
        #yield self._update_resource, 'hello-foo-1', 'resource-2', '0..1'

    @nose.tools.istest
    def test_5_delete_resource(self):
        raise SkipTest(self._skip_message)    
    
        yield self._delete_resource, 'hello-inspire-1', 'resource-1'
        pass

    @nose.tools.istest
    def test_6_delete_package(self):
        raise SkipTest(self._skip_message)    
    
        #yield self._delete_package, 'hello-inspire-1'
        pass

    def _create_package(self, fixture_name):
        
        pkg_dict = package_fixtures[fixture_name]['0'] 
        pkg_name = pkg_dict['name']

        res1 = self.app.get('/dataset/new', status='*')
        assert res1.status == 200
        
        key_prefix = dt = pkg_dict['dataset_type']

        # 1st stage
    
        form1 = res1.forms['package-form'] 
        for k in ['title', 'name', 'dataset_type', 'notes', 'license_id']:
            v = pkg_dict.get(k)
            v = v.encode('utf-8') if isinstance(v, unicode) else v
            form1.set(k, v)
        form1.set('tag_string', ','.join(map(lambda t: t['name'], pkg_dict.get('tags', []))))
        
        res1s = form1.submit('save')
        assert res1s.status in [301, 302] 
        
        # 2nd stage

        res2 = res1s.follow()
        
        resource_dict = next(iter(pkg_dict['resources'])) # 1st resource
        form2 = res2.forms['resource-form']
        for k in ['description', 'url', 'name', 'format']:
            v = resource_dict.get(k)
            v = v.encode('utf-8') if isinstance(v, unicode) else v
            form2.set(k, v)
        
        btns = form2.fields.get('save')
        i2 = next(j for j, b in enumerate(btns) if b.id == 'btn-save-go-metadata')
        res2s = form2.submit('save', index=i2, status='*')
        assert res2s.status in [301, 302]

        # 3rd stage - core metadata
        
        res3 = res2s.follow()
        
        form3 = res3.forms['package-form']
        for k in ['version', 'author', 'author_email', 'maintainer', 'maintainer_email']:
            v = pkg_dict.get(k)
            v = v.encode('utf-8') if isinstance(v, unicode) else v
            form3.set(k, v)

        # 3rd stage - dataset_type-related metadata
        
        for t, v in dictization.flatten(pkg_dict.get(dt)).items():

            k = '.'.join((key_prefix,) + tuple(map(str,t)))
            v = v.encode('utf-8') if isinstance(v, unicode) else v
            form3.set(k, v)

        btns = form3.fields.get('save')
        i3 =  next(j for j, b in enumerate(btns) if b.id == 'btn-save-finish')
        res3s = form3.submit('save', index=i3, status='*')
        assert res3s.status in [301, 302]

        # Finished, return to "view" page
        res4 = res3s.follow()
        assert res4.status in [200]
        assert res4.request.url == '/dataset/%s' %(pkg_name)

        # Compare to package_show result
        
        res_dict = self._get_package(pkg_name)

        assert res_dict['dataset_type'] == dt
        
        for k in (self.basic_fields & set(res_dict.keys())):
            assert (not k in pkg_dict) or res_dict[k] == pkg_dict[k]
        
        pkg_dt_dict = dictization.flatten(pkg_dict.get(dt))
        res_dt_dict = dictization.flatten(res_dict.get(dt))
        for k in pkg_dt_dict.keys():
            assert res_dt_dict[k] == pkg_dt_dict[k]

        return

    def _update_package(self, fixture_name, changeset):
 
        assert fixture_name in package_fixtures
        pkg_dict = package_fixtures[fixture_name][changeset]
        pkg_name = package_fixtures[fixture_name]['0']['name']
        
        res1 = self.app.get('/dataset/edit/%s' % pkg_name)
        assert res1.status == 200
        
        key_prefix = dt = package_fixtures[fixture_name]['0']['dataset_type']

        # Edit core metadata
        
        form1 = res1.forms['package-form']
        for k in self.basic_fields :
            v = pkg_dict.get(k)
            if v is not None:
                v = v.encode('utf-8') if isinstance(v, unicode) else v
                form1.set(k, v)
        if 'tags' in pkg_dict:
            form1.set('tag_string', ','.join(map(lambda t: t['name'], pkg_dict.get('tags', []))))
        
        # Edit dataset_type-related metadata

        for t, v in dictization.flatten(pkg_dict.get(dt)).items():
            k = '.'.join((key_prefix,) + tuple(map(str,t)))
            v = v.encode('utf-8') if isinstance(v, unicode) else v
            form1.set(k, v)
        
        # Submit

        res1s = form1.submit('save', status='*')
        assert res1s.status in [301, 302]
        
        res2 = res1s.follow()
        assert res2.status in [200]      
        assert res2.request.url == '/dataset/%s' %(pkg_name)

    def _delete_package(self, fixture_name):
 
        assert fixture_name in package_fixtures
        pkg_dict = package_fixtures[fixture_name]
        pkg_name = package_fixtures[fixture_name]['0']['name']
        
        res_pkg_dict = self._get_package(pkg_name)
        res1 = self.app.get('/dataset/delete/%s' % pkg_name)
        assert res1.status == 200

        key_prefix = dt = package_fixtures[fixture_name]['0']['dataset_type']

        form1 = res1.forms[1]
        
        # Confirm
        res1s = form1.submit('delete', status='*')
        assert res1s.status in [301, 302]

        res2 = res1s.follow()
        assert res2.status in [200]
        assert res2.request.url == '/dataset'

        res = self.app.get('/api/action/package_list')
        assert res.json.get('success')
        assert pkg_name not in res.json.get('result')

    def _create_resource(self, pkg_fixture_name, fixture_name):
        
        assert pkg_fixture_name in package_fixtures
        assert fixture_name in resource_fixtures
        pkg_name = package_fixtures[pkg_fixture_name]['0']['name']
        resource_dict = resource_fixtures[fixture_name]['0']
        resource_name = resource_dict['name']
        
        # Fetch initial package dict
        
        pkg_dict = self._get_package(pkg_name)
        
        dt = pkg_dict['dataset_type']

        # Create resource

        res1 = self.app.get('/dataset/new_resource/%s' % pkg_name)
        assert res1.status == 200

        form1 = res1.forms['resource-form']
        for k in ['description', 'url', 'name', 'format']:
            v = resource_dict.get(k)
            v = v.encode('utf-8') if isinstance(v, unicode) else v
            form1.set(k, v)
        
        res1s = form1.submit('save', status='*')
        assert res1s.status in [301, 302]
        
        res2 = res1s.follow()
        assert res2.status in [200]      
        assert res2.request.url == '/dataset/%s' %(pkg_name)

        # Fetch result package dict
        
        res_pkg_dict = self._get_package(pkg_name)
        res_pkg_resources = res_pkg_dict['resources']

        # Verify resource metadata (changed)
        res_resource_dict = next(r for r in res_pkg_resources if r['name'] == resource_name)
        for k in ['url', 'description', 'name']:
            assert resource_dict[k] == res_resource_dict[k]
        assert resource_dict['format'] == res_resource_dict['format'].lower()

        # Verify package metadata (not changed)

        for k in self.basic_fields:
            assert pkg_dict[k] == res_pkg_dict[k] 
        
        assert_equal(pkg_dict.get(dt), res_pkg_dict.get(dt))

    def _update_resource(self, pkg_fixture_name, fixture_name, changeset):
        
        assert pkg_fixture_name in package_fixtures
        assert fixture_name in resource_fixtures
        pkg_name = package_fixtures[pkg_fixture_name]['0']['name']
        resource_name = resource_fixtures[fixture_name]['0']['name']
        resource_dict = resource_fixtures[fixture_name][changeset]
        
        # Fetch initial package dict
        
        pkg_dict = self._get_package(pkg_name)
        
        pkg_resources = pkg_dict['resources']
        dt = pkg_dict['dataset_type']
        
        resource_id = next(r for r in pkg_resources if r['name'] == resource_name).get('id')
        
        # Update resource
        
        res1 = self.app.get('/dataset/%s/resource_edit/%s' % (pkg_name, resource_id))
        assert res1.status == 200
        
        form1 = res1.forms['resource-form']
        for k in ['description', 'url', 'name', 'format']:
            v = resource_dict.get(k)
            if v is not None:
                v = v.encode('utf-8') if isinstance(v, unicode) else v
                form1.set(k, v)
        
        res1s = form1.submit('save', status='*')
        assert res1s.status in [301, 302]
        
        res2 = res1s.follow()
        assert res2.status in [200]      
        assert res2.request.url == '/dataset/%s/resource/%s' %(pkg_name, resource_id)

        # Fetch result package dict
       
        res_pkg_dict = self._get_package(pkg_name)
        res_pkg_resources = res_pkg_dict['resources']
        
        # Verify resource metadata (changed)
        
        resource_name = resource_dict.get('name', resource_name)
        res_resource_dict = next(r for r in res_pkg_resources if r['name'] == resource_name)
        for k in ['url', 'description', 'name']:
            assert not(k in resource_dict) or (resource_dict[k] == res_resource_dict[k])
        if 'format' in resource_dict:
            assert resource_dict['format'] == res_resource_dict['format'].lower()
    
        # Verify package metadata (not changed)

        for k in self.basic_fields:
            assert pkg_dict[k] == res_pkg_dict[k] 
        
        assert_equal(pkg_dict.get(dt), res_pkg_dict.get(dt))

    def _delete_resource(self, pkg_fixture_name, fixture_name):
        
        assert pkg_fixture_name in package_fixtures
        assert fixture_name in resource_fixtures

        pkg_name = package_fixtures[pkg_fixture_name]['0']['name']
        resource_name = resource_fixtures[fixture_name]['0']['name']
        resource_dict = resource_fixtures[fixture_name]
        
        # Fetch initial package dict
        
        pkg_dict = self._get_package(pkg_name)
        
        pkg_resources = pkg_dict['resources']
        dt = pkg_dict['dataset_type']

        resource_id = next(r for r in pkg_resources if r['name'] == resource_name).get('id')
        
        # Delete resource
        
        res1 = self.app.get('/dataset/%s/resource_delete/%s' % (pkg_name, resource_id))
        assert res1.status == 200

        # Note forms[1] is the delete confirmation form
        form1 = res1.forms[1]

        res1s = form1.submit('delete', status='*')
        assert res1s.status in [301, 302]

        res12 = self.app.get('/dataset/%s/resource_delete/%s' % (pkg_name, resource_id))
        assert res12.status == 200

        res2 = res1s.follow()
        assert res2.status in [200]
        assert res2.request.url == '/dataset/%s' %(pkg_name)

        # Fetch result package dict
       
        res_pkg_dict = self._get_package(pkg_name)
        res_pkg_resources = res_pkg_dict['resources']

        # Verify resource metadata deleted
        for res in res_pkg_resources:
            assert res.get('name') != resource_name
            

        # Verify package metadata (not changed)

        for k in self.basic_fields:
            assert pkg_dict[k] == res_pkg_dict[k] 
        
        assert_equal(pkg_dict.get(dt), res_pkg_dict.get(dt))
    def _get_package(self, pkg_name):
        
        res = self.app.get('/api/action/package_show?id=%s' %(pkg_name))
        assert res.json.get('success')
        return res.json.get('result')

## Fixtures ##

resource_fixtures = {}

resource_fixtures['resource-1'] = {
    '0': {
        'url': 'http://example.com/res/1',
        'name': u'Example 1',
        'format': 'html',
        'description': u'A very important HTML document',
    },
    '0..1': {
        'name': u'Example webpage (1)',
        'description': u'A quite important HTML document',
    }
}

resource_fixtures['resource-2'] = {
    '0': {
        'url': 'http://localhost:5001/samples/1.csv',
        'name': u'Example 2',
        'format': 'csv',
        'description': u'A sample CSV file',
    },
    '0..1': {
        'name': 'Example CSV (2)',
    },
}

resource_fixtures['resource-3'] = {
    '0': {
        'url': 'http://localhost:5001/api/action',
        'name': u'Example API',
        'format': 'api',
        'description': u'An example API endpoint',
    },
}

package_fixtures = {}

package_fixtures['hello-inspire-1'] = {
    '0': {
        'title': u'Hello Inspire',
        'name': 'hello-inspire-1',
        'notes': u'I am the first _Inspire_ dataset!',
        'author': u'Λαλάκης',
        'license_id': 'CC-BY-3.0',
        'version': '1.0.0',
        'maintainer': u'Nowhere Man',
        'author_email': 'lalakis.1999@example.com',
        'maintainer_email': 'nowhere-man@example.com',
        'tags': [
            { 'name': 'hello-world', 'display_name': 'Hello World', }, 
            { 'name': u'test', 'display_name': 'Test' }, 
            { 'name': 'inspire', 'display_name': 'INSPIRE' }, 
        ],
        'dataset_type': 'inspire',
        'inspire': {
            'contact': [{
                "organization": u"Ομάδα geodata.gov.gr",
                "role": "pointofcontact",
                "email": "info@geodata.gov.gr"
            }],
            'datestamp': u'2014-01-01',
            'languagecode': "el",
            'title': u"A great helloworld dataset",
            'abstract': u"This is really great",
            'bounding_box': {
                "sblat": 33.188516,
                "wblng": 16.76871,
                "nblat": 43.339883,
                "eblng": 30.655429
            },
            'locator': [],
            'resource_language': [],
            'topic_category':["biota", "economy"],
            'temporal_extent': {'start': '2012-01-01', 'end': '2013-01-01'},
            'lineage': u"A lineage description here ...",
            'access_constraints': [u"A constaint", u"Another strict constraint"],
            'creation_date': '2012-01-01',
            'publication_date': '2012-01-30',
            'revision_date': '2014-01-01',
            'limitations': [u"Nothin"],
         #   'keywords':[{
         #       'terms':["air", "agriculture", "climate"],
         #       'thesaurus':'TODO'
         #       },
         #       {
         #       'terms':["buildings", "addresses"],
         #       'thesaurus': 'TODO'
         #       }],
         #   'conformity':[{
         #       'title':u"specifications blabla",
         #       'date':'2014-09-19',
         #       'date_type':"creation",
         #       'degree': "conformant"
         #       }],
         #   'responsible_party':[{
         #       'organization': u"Org",
         #       'email':[u"email@asd.gr"],
         #       'role':"pointofcontact"
         #       }]
            },
        'resources': [
            resource_fixtures['resource-1']['0'],
        ],

        },

    '0..1': {
        'license_id': 'CC-BY-SA-4.0',
        'version': '1.0.1',
        'inspire': {
            'spatial_resolution': [
                {
                    'distance': 5,
                    'denominator': None,
                    'uom': "km",
                }
            ]
        },
    },
}
