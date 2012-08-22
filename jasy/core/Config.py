import os, json
from jasy.core.Error import JasyError

try:
    import yaml
except ImportError:
    yaml = None


def findConfig(fileName):
    fileExt = os.path.splitext(fileName)[1]

    # Auto discovery
    if not fileExt:
        for tryExt in (".json", ".yaml"):
            if os.path.exists(fileName + tryExt):
                return fileName + tryExt

        return None  

    if os.path.exists(fileName) and fileExt in (".json", ".yaml"):
        return fileName  
    else:
        return None


def loadConfig(fileName, encoding="utf-8"):
    configName = findConfig(fileName)
    if configName is None:
        raise JasyError("Unsupported config file: %s" % fileName)

    fileHandle = open(configName, mode="r", encoding=encoding)    

    fileExt = os.path.splitext(configName)[1]
    if fileExt == ".json":
        return json.load(fileHandle)

    elif fileExt == ".yaml":
        if yaml is None:
            raise JasyError("Unable to safe YAML. Python module is missing!")

        return yaml.load(fileHandle)
        


def writeConfig(data, fileName, indent=2, encoding="utf-8"):
    fileHandle = open(fileName, mode="w", encoding=encoding)

    fileExt = os.path.splitext(fileName)[1]
    if fileExt == ".json":
        json.dump(data, fileHandle, indent=indent, ensure_ascii=False)
    
    elif fileExt == ".yaml":
        if yaml is None:
            raise JasyError("Unable to safe YAML. Python module is missing!")

        yaml.dump(data, fileHandle, default_flow_style=False, indent=indent, allow_unicode=True)

    else:
        raise JasyError("Unsupported config type: %s" % fileExt)

