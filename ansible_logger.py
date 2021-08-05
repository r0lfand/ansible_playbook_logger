__metaclass__ = type

from ansible.plugins.callback import CallbackBase
from ansible import constants as C
from ansible import context
import os
import re
import socket
import datetime
import pwd


username = pwd.getpwuid(os.getuid())[0]
hostname = socket.gethostname()
ppid = os.getppid()
tmp = datetime.datetime.now()
time = tmp.strftime('%Y-%m-%dT%H:%M:%S')
dest_addr = '127.0.0.1'
dest_port = 4444
res_hosts = []

class CallbackModule(CallbackBase):
    
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'scs_log_callback'


    def __init__(self, display=None):
        super(CallbackModule, self).__init__()


    def form_inventory(self, executi, inven):
        res_hosts.append('play arguments: ')
        if len(executi) != 0 and type(executi) == tuple:
            for ex in executi:
                res_hosts.append(ex + ' ')
        elif len(executi) != 0 and type(executi) != tuple:
            res_hosts.append(executi + ' ')
        if len(inven) != 0:
            inv_flag = 0
            for inv in inven:
                if inv_flag == 0:
                    res_hosts.append('inventory: ')
                    inv_flag = 1
                res_hosts.append(inv + ' ')


    def form_extra_vars(self, extras, executi):
        res_list = []
        res_list.append('play arguments: ')
        if len(executi) != 0 and type(executi) == tuple:
            for ex in executi:
                res_list.append(ex + ' ')
        elif len(executi) != 0 and type(executi) != tuple:
            res_list.append(executi + ' ')
        if len(extras) != 0:
            res_list.append('extra vars: ')
            for ex in extras:
                res_list.append(ex + ' ')
        res = ''.join(res_list)
        return res


    def send_to_scs(self, mess):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(mess.encode('utf-8'), (dest_addr, dest_port))	
        sock.close()


    def v2_runner_on_ok(self, result):
        if str(result._host) not in res_hosts:
            res_hosts.append(str(result._host))
            res_hosts.append(' ')
    

    def v2_playbook_on_stats(self, stats):
        res = ''.join(res_hosts).replace('\n', ' ')
        inv = '{0} {1} ANS_HOSTS: {2}[{3}]: {4}'.format(time, hostname, username, ppid, res)
        CallbackModule.send_to_scs(self, mess=inv)
    

    def v2_playbook_on_start(self, playbook):
        hostfilepath = context.CLIARGS['inventory']
        extravars = context.CLIARGS['extra_vars']
        execution = context.CLIARGS['args']
        
        CallbackModule.form_inventory(self, executi=execution, inven=hostfilepath)
        check_ex = CallbackModule.form_extra_vars(self, extras=extravars, executi=execution)

        extras = '{0} {1} ANS_EXTRAVARS: {2}[{3}]: {4}'.format(time, hostname, username, ppid, check_ex)
        CallbackModule.send_to_scs(self, mess=extras)

    
    def v2_playbook_on_task_start(self, task, is_conditional):
        execution = context.CLIARGS['args']
        module_name = task.action
        task_name = task.get_name()
        loops = str(task.loop)

        args = ''
        args = u', '.join(u'%s: %s' % a for a in task.args.items())
        args = u' %s' % args
        for_logs =  CallbackModule.form_extra_vars(self, extras='', executi=execution) + ' task name: ' + task_name + ' module name: ' + module_name + ' '  + args + ' loops: ' + loops
        ex_tasks = '{0} {1} ANS_PLAYBOOK: {2}[{3}]: {4}'.format(time, hostname, username, ppid, for_logs)
        CallbackModule.send_to_scs(self, mess=ex_tasks)
 
