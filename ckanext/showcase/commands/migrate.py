from __future__ import print_function
import logging

from ckan.lib.cli import CkanCommand

import ckanext.showcase.utils as utils
from ckan.lib.helpers import render_markdown
from ckan.plugins import toolkit



log = logging.getLogger(__name__)


class MigrationCommand(CkanCommand):
    '''
    CKAN 'Related Items' to 'Showcase' migration command.

    Usage::

        paster showcase migrate -c <path to config file>
            - Migrate Related Items to Showcases

        paster showcase migrate -c <path to config file> [--allow-duplicates]
            - Migrate Related Items to Showcases and allow duplicates

        paster showcase markdown-to-html -c <path to config file>
            - Migrate the notes of all showcases from markdown to html.

    Must be run from the ckanext-showcase directory.
    '''
    summary = __doc__.split('\n')[0]
    usage = __doc__

    def __init__(self, name):
        super(CkanCommand, self).__init__(name)

        self.parser.add_option('--allow-duplicates',
                               dest='allow_duplicates',
                               default=False,
                               help='''Use this option to allow
                            related items with duplicate titles to be migrated.
                            Duplicate showcases will be created as
                            'duplicate_<related-name>_<related-id>'.''',
                               action='store_true')

    def command(self):
        '''
        Parse command line arguments and call appropriate method.
        '''
        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print(self.__doc__)
            return

        cmd = self.args[0]
        self._load_config()

        if cmd == 'migrate':
            self.migrate()
        elif cmd == 'markdown-to-html':
            self.markdown_to_html()
        else:
            print('Command "{0}" not recognized'.format(cmd))

    def migrate(self):
        utils.migrate(self.options.allow_duplicates)

    def markdown_to_html(self):
        ''' Migrates the notes of all showcases from markdown to html.

        When using CKEditor, notes on showcases are stored in html instead of
        markdown, this command will migrate all nothes using CKAN's
        render_markdown core helper.
        '''
        showcases = toolkit.get_action('ckanext_showcase_list')(data_dict={})

        site_user = toolkit.get_action('get_site_user')({
            'model': model,
            'ignore_auth': True},
            {}
        )
        context = {
            'model': model,
            'session': model.Session,
            'ignore_auth': True,
            'user': site_user['name'],
        }

        for showcase in showcases:
            toolkit.get_action('package_patch')(
                context,
                {
                    'id': showcase['id'],
                    'notes': render_markdown(showcase['notes'])
                }
            )
        print('All notes were migrated successfully.')
