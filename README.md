# Ansible callback plugin for playbook logging
This is a simple implementation of ansible callback plugin for extended playbook logging.
Works with ansible versions **2.8+**.
The idea behind this is getting all the interesting information from ansible's **context.CLIARGS** dictionary and sending it to a remote log collector.

When a playbook is executed three strings are formed:

_ANS_HOSTS:_ contains all inventory hosts that returned **ok** or **changed** in a task.
_ANS_EXTRAVARS:_ contains all extra variables that were passed to **ansible-playbook**.
_ANS_PLAYBOOK:_ contains all executed tasks that were started with their additional variables.

## Usage:
Insert your log collector's IP address or FQDN in **dest_addr** variable.
Insert your log collector's port in **dest_port** variable.
You can activate a custom callback by either dropping it into a _callback_plugins_ directory adjacent to your play, inside a role, or by putting it in one of the callback directory sources configured in _ansible.cfg_.
