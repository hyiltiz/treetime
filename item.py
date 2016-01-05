#
# Tis file is part of TreeTime, a tree editor and data analyser
#
# Copyright (C) GPLv3, 2015, Jacob Kanev
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA

# -*- coding:utf-8 -*-

import copy
import json



"""The list/forest item containing the actual data"""
class Item:

    def __init__(self, name, fieldstring='{}', treestring='[]'):
        self.name = name
        self.parentNames = []
        self.fields = json.loads(fieldstring)
        self.trees = json.loads(treestring)
        self.viewNodes = []
        self.nameChangeCallbacks = []
        self.fieldChangeCallbacks = []
        self.deletionCallbacks = []
        self.clearCallbacks()
        
        
    def clearCallbacks(self):
        self.viewNodes = []
        self.nameChangeCallbacks = []
        self.fieldChangeCallbacks = []
        self.deletionCallbacks = []
        for t in self.trees:
            self.viewNodes += [None]
            self.nameChangeCallbacks += [None]
            self.fieldChangeCallbacks += [None]
            self.deletionCallbacks += [None]
        

    def addField(self, name, content):
        self.fields[name] = content


    def removeField(self, name, content):
        del self.fields[name]


    def writeToString(self):
        string = self.name + "\n"
        string += "   fields " + json.dumps(self.fields) + "\n"
        string += "   trees " + json.dumps(self.trees) + "\n"
        return string


    def readFromString(self, string):
        s = string.split("\n   fields ")
        self.name = s[0]
        s = s[1].split("\n   trees ")
        self.fields = json.loads(s[0])
        self.trees = json.loads(s[1])
        self.clearCallbacks()

    def printitem(self):
        print(self.name)
        for key in self.fields:
            print("    ", key)
            for subkey in self.fields[key]:
                print("        ", subkey, ":", self.fields[key][subkey])


    def registerViewNode(self, tree, node):
        self.viewNodes[tree] = node
        

    def registerNameChangeCallback(self, tree, callback):
        self.nameChangeCallbacks[tree] = callback
            

    def registerFieldChangeCallback(self, tree, callback):
        self.fieldChangeCallbacks[tree] = callback


    def registerDeletionCallback(self, tree, callback):
        self.deletionCallbacks[tree] = callback


    def changeName(self, newName):
        self.name = newName
        for c in self.nameChangeCallbacks:
            if c is not None:
                c(newName)


    ''' Edit the content of a field. The content is expected to be a string and will be converted accourding to the field type. '''
    def changeFieldContent(self, fieldName, fieldContent):
        
        if fieldName not in self.fields:
            return "A field with name " + fieldName + " does not exist in node " + self.name + "."
        else:
            # update field content
            field = self.fields[fieldName]
            type = field["type"]
            if type == "string":
                field["content"] = fieldContent
            elif type == "integer":
                field["content"] = json.loads(fieldContent)
            else:
                return "A field of type " + type + " cannot be edited."
            
            self.notifyFieldChange(fieldName)
        
        return True


    def notifyFieldChange(self, fieldName):
        # notify GUI of field change
        for f in self.fieldChangeCallbacks:
            if f is not None:
                f(fieldName)


    ''' Remove this item from the tree, and have it call all removal callbacks. '''
    def removeFromTree(self, treeIndex):
        
        self.trees[treeIndex] = [];
        if self.deletionCallbacks[treeIndex] is not None:
            self.deletionCallbacks[treeIndex]();
    

class ItemPool:
    def __init__(self):
        self.items = []
        self.defaultItem = None
        
    def writeToString(self):
        string = ""
        for it in self.items:
            string += "item " + it.writeToString() + "\n"
        return string
        
    def readFromString(self, string):
        string = string.split("\n\nitem ") # items are separated by empty lines and the keyword "item"
        for s in string:
            if s != "":
                it = Item("")
                it.readFromString(s)
                self.items += [it]
                if self.defaultItem is None:
                    self.defaultItem = it

    def printpool(self):
        for it in self.items:
            it.printitem()
            

    """Adds a copy of the default item to the list and returns a reference to it"""
    def addNewItem(self):
        return self.copyItem(self.defaultItem)


    """Adds a copy of the default item to the list and returns a reference to it"""
    def copyItem(self, item):
        newitem = copy.deepcopy(item)
        newitem.viewNodes = []
        newitem.clearCallbacks()
        self.items += [newitem]
        return newitem
