import logging

import ckan.plugins as plugins
import ckan.model as model
import resource_actions
import pylons.config as global_config

log = logging.getLogger(__name__)


class RasterStorer(plugins.SingletonPlugin):
    """
    Implementation of the raster import functionality in ckan
    This class implements the notify method that determines if a dataset was modified and takes appropiate action
    by either registering the raster data or removing it through WCST
    """
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.IConfigurable, inherit=True)
    plugins.implements(plugins.IDomainObjectModification, inherit=True)
    plugins.implements(plugins.IResourceUrlChange)

    SUPPORTED_FROMATS = "geotiff png jpeg zip raster"

    def before_map(self, map):
        """
        Adds the url mappings to the raster import controller
        """
        map.connect("raster-publish", "/api/raster/publish/{resource_id}",
                    controller='ckanext.publicamundi.storers.raster.controllers.import:RasterImportController', action='publish',
                    resource_id='{resource_id}')
        map.connect("raster-delete", "/api/raster/delete/{resource_id}",
                    controller='ckanext.publicamundi.storers.raster.controllers.import:RasterImportController', action='delete',
                    resource_id='{resource_id}')
        map.connect("raster-finalize", "/api/raster/finalize/{resource_id}",
                    controller='ckanext.publicamundi.storers.raster.controllers.import:RasterImportController', action='finalize',
                    resource_id='{resource_id}')
        return map

    def update_config(self, config):
        """
        Exposes the public folder of this extension. The intermediary gml files will be stored here.
        """
        plugins.toolkit.add_public_directory(config, global_config.get("ckanext.publicamundi.rasterstorer.temp_dir", ""))
        plugins.toolkit.add_public_directory(config, 'public')
        plugins.toolkit.add_template_directory(config, 'templates')
        plugins.toolkit.add_resource('public', 'ckanext-publicamundi-raster')

    def notify(self, entity, operation=None):
        """
        Notifies the plugin when a change is done to a resource
        :param entity: the entity that was modified
        :param operation: the operation that was applied on it
        """
        if isinstance(entity, model.resource.Resource):
            if entity.format != "":
                if entity.format.lower() in self.SUPPORTED_FROMATS:
                    if operation == model.domain_object.DomainObjectOperation.new:
                        # A new raster resource has been created
                        resource_actions.create_identify_resource_task(entity)
                    elif operation == model.domain_object.DomainObjectOperation.deleted:
                        # A raster resource has been deleted
                        # resource_actions.create_delete_resource_task(entity)
                        pass
                    elif operation is None:
                        # The URL of a raster resource has been updated
                        pass
        elif isinstance(entity, model.Package):
            log.info('Notified on modification %r of dataset %r (state=%r)' % (
                operation, entity.id, entity.state))
            if entity.state == 'deleted':
                for resource in entity.as_dict()['resources']:
                    if resource['format'] in self.SUPPORTED_FROMATS:
                        resource_actions.create_delete_resource_task(resource)