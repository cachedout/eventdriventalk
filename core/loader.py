'''
A basic loader to pull some modules off of disk
for normalized access.
'''

import os
import imp
import inspect

def load_actions(opts, reactions_dir):
    reaction_mods = os.listdir(reactions_dir)
    return _load_mods(opts, reaction_mods, reactions_dir, 'reactions')

def load_rules(opts, rules_dir):
    rules_mods = os.listdir(rules_dir)
    return _load_mods(opts, rules_mods, rules_dir, 'rules')

def _load_mods(opts, mods, search_dir, prefix):
    '''
    opts: The seralized config file
    reaction_dir: A directory to search for reaction modules
    '''
    loaded = dict()
    
    for mod_to_load in mods:
        mod = imp.load_source(mod_to_load, os.path.join(search_dir, mod_to_load))

        for func_def in inspect.getmembers(mod, inspect.isfunction):
            func_mod_delimited = '{0}.{1}.{2}'.format(prefix, mod_to_load.rstrip('.py'), func_def[0])
            loaded[func_mod_delimited] = func_def[1]
    return loaded


