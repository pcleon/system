import json
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.cli.inventory import InventoryCLI
inifd = '/tmp/x.ini'
jsonfd = '/tmp/dd'
ini_data = None

ll = ['-i', inifd, '--list']
loader = DataLoader()
inventory = InventoryManager(loader=loader, sources='/tmp/x.ini')
variable_manager = VariableManager(loader=loader, inventory=inventory)
top = inventory.groups.get('all')
xx = InventoryCLI(ll)
xx.loader = loader
xx.inventory = inventory
xx.vm = variable_manager
super(InventoryCLI,xx).run()
t=xx.json_inventory(top)
# print(t)
print(json.dumps(t, indent=4, sort_keys=True))
