import math 
import re
import numpy as np


class Node:
    def __init__(self, name):
        self.name=name
        self.classes=[]
        self.parent=[]
        self.child=[]
        self.probs={}
        self.dic={}
    def addProb(self, values, prob):
        self.probs[repr(values)]=prob
    def findProb(self, evidence):
        pass
    def findClass(self, value):
        pos=0
        for c in self.classes:
            if c==value:
                return pos
            pos+=1


def debug(nodes):
    for key, n in nodes.items():
        print("Name: ",n.name)
        print("Classes: ",n.classes)
        print("Parents: ",n.parent)
        print("Children: ",n.child)
        print("Probabilities: ")
        for key, value in n.probs.items():
            print("\t",key," ", value)


def parser(name):
    char_list = '[(),;]'
    nodes = {}
    bif = []
    name=str(name)+".bif"
    file = open(name,mode='r+')
    for line in file:
        bif.append(line)
    for i in range(0, len(bif)):
        line = [x for x in bif[i].split(' ') if x!= '']
        fst=line[0].strip()
        if fst=="variable":
            name=line[1].strip()
            nodes[name]=Node(name)
            i+=1
            line = [x for x in bif[i].split(' ') if x!= '']
            fst=line[0].strip()
            while fst!="}":
                if fst=="type":
                    n=int(line[3].strip())
                    k=0
                    while n>0:
                        nodes[name].classes.append(re.sub(char_list, '',line[6+k].strip()))
                        k+=1
                        n-=1
                elif fst=="property":
                    # DEPOIS
                    pass
                else:
                    pass 
                i+=1
                line = [x for x in bif[i].split(' ') if x!= '']
                fst=line[0].strip()
        elif fst=="probability":
            name = line[2].strip()
            # tem parents
            if (line[3].strip()=='|'):
                occur=bif[i].count(',')
                k=0
                while k<=occur:
                    parent=re.sub(char_list, '', line[4+k].strip())
                    nodes[name].parent.append(parent)
                    nodes[parent].child.append(name)
                    k+=1
                k=0
                i+=1
                line = [x for x in bif[i].split(' ') if x!= '']
                fst=line[0].strip()
                while fst!="}":
                    values={}
                    probs=[]
                    n_parents=len(nodes[name].parent)
                    n_classes=len(nodes[name].classes)
                    for m in range(0,n_parents):
                        values[nodes[name].parent[m]]=re.sub(char_list, '', line[m].strip())
                    for j in range(n_parents,n_parents+n_classes):
                        probs.append(float(re.sub(char_list, '', line[j].strip())))
                    nodes[name].addProb(values,probs)
                    i+=1
                    line = [x for x in bif[i].split(' ') if x!= '']
                    fst=line[0].strip()
            else:
                i+=1
                line = [x for x in bif[i].split(' ') if x!= '']
                fst=line[0].strip()
                probs=[]
                n_classes=len(nodes[name].classes)
                for j in range(1,n_classes+1):
                    probs.append(float(re.sub(char_list, "", line[j].strip())))
                nodes[name].addProb([],probs)
        else: #network
            pass
    return nodes