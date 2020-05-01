# Lots of module path stuff

def module_path_root(module_path):
    #! should return nothing on fail?
    idx = module_path.find('.') 
    if (idx >= 0):
        return module_path[:idx]
    return module_path
    
def module_path_leaf(module_path):
    idx = module_path.rfind('.') 
    if (idx >= 0 and (len(module_path) > idx + 1)):
        return module_path[idx + 1:]
    return module_path 

def module_path_branch(module_path):
    idx = module_path.rfind('.') 
    if (idx >= 0):
        return module_path[:idx]
    return module_path 

def module_path_append(module_path, leaf):
    return "{}.{}".format(module_path, leaf)
