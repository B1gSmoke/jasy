#
# Jasy - JavaScript Tooling Refined
# Copyright 2010 Sebastian Werner
#

import logging, re, copy
from jasy.parser.Node import Node

class TranslationError(Exception):
    pass

class Translation:
    def __init__(self, table=None):
        self.__table = table
        

    def patch(self, node):
        self.__recurser(node)
    
    
    
    __methods = ("tr", "trc", "trn")
    __params = {
      "tr" : ["text"],
      "trn" : ["textSingular", "textPlural"],
      "trc" : ["textHint", "text"]
    }
    
    
    replacer = re.compile("({[a-zA-Z0-9_\.]+})")
    number = re.compile("[0-9]+")
    

    def __rebuildAsSplitted(self, value, mapper):
        """ The real splitter engine. Creates plus Node instances and cascade them automatically """
        
        result = []
        splits = self.replacer.split(value)
        if len(splits) == 1:
            return None
        
        pair = Node(None, "plus")

        for entry in splits:
            if entry == "":
                continue
                
            if len(pair) == 2:
                newPair = Node(None, "plus")
                newPair.append(pair)
                pair = newPair

            if self.replacer.match(entry):
                pos = int(entry[1:-1])
                
                # Items might be added multiple times. Copy to protect original.
                try:
                    repl = mapper[pos]
                except KeyError:
                    raise TranslationError("Invalid positional value: %s in %s" % (entry, value))
                
                copied = copy.deepcopy(mapper[pos])
                copied.parenthesized = True
                pair.append(copied)
                
            else:
                child = Node(None, "string")
                child.value = entry
                pair.append(child)
                
        return pair

    
    def __splitTemplate(self, replaceNode, patchParam, valueParams):
        """ Split string into plus-expression(s) """
        
        mapper = { pos: value for pos, value in enumerate(valueParams) }
        
        try:
            pair = self.__rebuildAsSplitted(patchParam.value, mapper)
        except TranslationError as ex:
            raise TranslationError("Invalid translation usage in line %s. %s" % (replaceNode.line, ex))
            
        if pair:
            replaceNode.parent.replace(replaceNode, pair)
    
    
    def __recurser(self, node):
        if node.type == "call":
            funcName = None
            
            if node[0].type == "identifier":
                funcName = node[0].value
            elif node[0].type == "dot" and node[0][1].type == "identifier":
                funcName = node[0][1].value
            
            if funcName in self.__methods:
                params = node[1]
                table = self.__table

                # Verify param types
                if params[0].type != "string":
                    logging.warn("Expecting translation string to be type string: %s at line %s" % (params[0].type, params[0].line))
                    
                if (funcName == "trn" or funcName == "trc") and params[1].type != "string":
                    logging.warn("Expecting translation string to be type string: %s at line %s" % (params[1].type, params[1].line))


                # Signature tr(msg, arg1, arg2, ...)
                if funcName == "tr":
                    key = params[0].value
                    if key in table:
                        params[0].value = table[key]
                        
                    if len(params) == 1:
                        node.parent.replace(node, params[0])
                    else:
                        self.__splitTemplate(node, params[0], params[1:])
                        
                        
                # Signature trc(hint, msg, arg1, arg2, ...)
                elif funcName == "trc":
                    key = params[0].value
                    if key in table:
                        params[1].value = table[key]

                    if len(params) == 2:
                        node.parent.replace(node, params[1])
                    else:
                        self.__splitTemplate(node, params[1], params[2:])
                        
                        
                # Signature trn(msg, msg2, [...], int, arg1, arg2, ...)
                elif funcName == "trn":
                    keySingular = params[0].value
                    if keySingular in table:
                        params[0].value = table[keySingular]

                    keyPlural = params[1].value
                    if keyPlural in table:
                        params[1].value = table[keyPlural]
                        
                    # TODO: Multi plural support

                        
                    if len(params) >= 3:
                        # Patch strings
                        
                        self.__splitTemplate(params[0], params[0], params[3:])
                        self.__splitTemplate(params[1], params[1], params[3:])
                        
                        

                    
                    


                    #    # Replace the whole call with: int < 2 ? singularMessage : pluralMessage
                    #    
                    #    hook = Node(node.tokenizer, "hook")
                    #    hook.parenthesized = True
                    #    condition = Node(node.tokenizer, "le")
                    #    condition.append(params[2])
                    #    number = Node(node.tokenizer, "number")
                    #    number.value = 1
                    #    condition.append(number)
                    #    
                    #    hook.append(condition, "condition")
                    #    hook.append(params[1], "elsePart")
                    #    hook.append(params[0], "thenPart")
                    #    
                    #    node.parent.replace(node, hook)
                    #    





                    
                    
    
    
        for child in node:
            if child != None:
                self.__recurser(child)
                
                
                

        
       