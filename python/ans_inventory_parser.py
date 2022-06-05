from operator import attrgetter

from ansible.cli import CLI
from ansible.cli.inventory import InventoryCLI
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager

file = '/tmp/k.ini'

INTERNAL_VARS = frozenset(['ansible_diff_mode',
                           'ansible_config_file',
                           'ansible_facts',
                           'ansible_forks',
                           'ansible_inventory_sources',
                           'ansible_limit',
                           'ansible_playbook_python',
                           'ansible_run_tags',
                           'ansible_skip_tags',
                           'ansible_verbosity',
                           'ansible_version',
                           'inventory_dir',
                           'inventory_file',
                           'inventory_hostname',
                           'inventory_hostname_short',
                           'groups',
                           'group_names',
                           'omit',
                           'playbook_dir', ])


class MyInventoryParser(InventoryCLI):
    def __init__(self):
        pass

    def handler_vars(self, top):

        seen = set()

        def format_group(group):
            results = {}
            results[group.name] = {}
            if group.name != 'all':
                results[group.name]['hosts'] = [h.name for h in sorted(group.hosts, key=attrgetter('name'))]
            results[group.name]['children'] = []
            for subgroup in sorted(group.child_groups, key=attrgetter('name')):
                results[group.name]['children'].append(subgroup.name)
                if subgroup.name not in seen:
                    results.update(format_group(subgroup))
                    seen.add(subgroup.name)

            self._remove_empty(results[group.name])
            if not results[group.name]:
                del results[group.name]

            return results

        results = format_group(top)

        # populate meta
        results['_meta'] = {'hostvars': {}}
        hosts = self.inventory.get_hosts()
        for host in hosts:
            # 调用里面有context,不会处理,只能自己重写
            # hvars = self._get_host_variables(host)
            hvars = self.vm.get_vars(host=host, include_hostvars=False, stage='all')
            # _remove_internal
            for internal in INTERNAL_VARS:
                if internal in hvars:
                    del hvars[internal]

            if hvars:
                results['_meta']['hostvars'][host.name] = hvars

        return results

    def format_ini(self, fname) -> dict:
        msg = open(fname).read()
        self.loader = DataLoader()
        self.inventory = InventoryManager(loader=self.loader, sources=(file,))
        # self.inventory = InventoryManager(loader=self.loader, sources=msg)
        self.vm = VariableManager(loader=self.loader, inventory=self.inventory, version_info=CLI.version_info())

        group = self.inventory.groups.get('all')
        results = self.handler_vars(group)
        return results


d = MyInventoryParser()
ret = d.format_ini(file)
print(ret)
