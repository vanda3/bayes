import re
from ast import literal_eval
from copy import deepcopy

class Node:
    def __init__(self, name):
        self.name = name
        self.classes = []
        self.parent = []
        self.child = []
        self.probs = {}
        self.values = {}
        self.factor = [name]
    def addProb(self, values, prob):
        self.probs[repr(values)] = prob
        self.values = values
    def isRoot(self):
        return len(self.parent) == 0
    def addParent(self, parent):
        self.parent.append(parent)
        self.factor.append(parent)
    def addChild(self, child):
        self.child.append(child)
    def classPos(self, value):
        pos = 0
        for c in self.classes:
            if c == value:
                return pos
            pos += 1
    def getProbability(self, perm):
        # Discard the var's value
        # Utilize only the parent's values
        # print("PERM: " + str(perm))
        # print("VAR: " + self.name)
        # print(self.probs)
        perm_to_compare = deepcopy(perm)
        perm_to_compare.pop(self.name)
        for prob in self.probs.items():
            if literal_eval(prob[0]) == perm_to_compare:
                for i, clas in enumerate(self.classes):
                    if perm[self.name] == clas:
                        return prob[1][i]       # Return the probability of the var, given the permutation

        return -1


def debug(nodes):
    print()
    for _, n in nodes.items():
        print("Name: ", n.name)
        print("Classes: ", n.classes)
        print("Parents: ", n.parent)
        print("Children: ", n.child)
        print("Probabilities: ")
        for key, value in n.probs.items():
            print("\t", key, " ", value)


def parser(name):
    char_list = '[(),;]'
    nodes = {}
    names = []
    bif = []
    name = str(name) + ".bif"
    file = open(name, mode='r+')
    for line in file:
        bif.append(line)
    for i in range(0, len(bif)):
        line = [x for x in bif[i].split(' ') if x != '']
        fst = line[0].strip()
        if fst == "variable":
            name = line[1].strip()
            names.append(name)
            nodes[name] = Node(name)
            i += 1
            line = [x for x in bif[i].split(' ') if x != '']
            fst = line[0].strip()
            while fst != "}":
                if fst == "type":
                    n = int(line[3].strip())
                    k = 0
                    while n > 0:
                        nodes[name].classes.append(re.sub(char_list, '', line[6 + k].strip()))
                        k += 1
                        n -= 1
                elif fst == "property":
                    # DEPOIS
                    pass
                else:
                    pass
                i += 1
                line = [x for x in bif[i].split(' ') if x != '']
                fst = line[0].strip()
        elif fst == "probability":
            name = line[2].strip()
            # tem parents
            if line[3].strip() == '|':
                occur = bif[i].count(',')
                k = 0
                while k <= occur:
                    parent = re.sub(char_list, '', line[4 + k].strip())
                    nodes[name].addParent(parent)
                    nodes[parent].addChild(name)
                    k += 1
                k = 0
                i += 1
                line = [x for x in bif[i].split(' ') if x != '']
                fst = line[0].strip()
                while fst != "}":
                    values = {}
                    probs = []
                    n_parents = len(nodes[name].parent)
                    n_classes = len(nodes[name].classes)
                    for m in range(0, n_parents):
                        values[nodes[name].parent[m]] = re.sub(char_list, '', line[m].strip())
                    for j in range(n_parents, n_parents + n_classes):
                        probs.append(float(re.sub(char_list, '', line[j].strip())))
                    nodes[name].addProb(values, probs)
                    i += 1
                    line = [x for x in bif[i].split(' ') if x != '']
                    fst = line[0].strip()
            else:
                i += 1
                line = [x for x in bif[i].split(' ') if x != '']
                fst = line[0].strip()
                probs = []
                n_classes = len(nodes[name].classes)
                for j in range(1, n_classes + 1):
                    probs.append(float(re.sub(char_list, "", line[j].strip())))
                nodes[name].addProb({}, probs)
        else:  # network
            pass
    return nodes, names


def queryParser(q):
    e = {}
    occur = q.count('|')
    flag = 0
    if occur == 0:
        flag = 1
    else:
        tmp = [x for x in q.split('|') if x != '']
        q = tmp[0].strip()
        occur = tmp[1].count(',')
        if occur == 0:
            try:
                # To remove all whitespaces and split the key, value
                attrib = "".join(tmp[1].split()).split('=')
                e[attrib[0]] = attrib[1]
            except IndexError:
                print("You have to attribute a value to the evidence")
                return q, e, flag, -1
            finally:
                flag = 2
        else:
            tmp1 = [x for x in tmp[1].split(',') if x != '']
            for ev in tmp1:
                try:
                    # To remove all whitespaces and split the key, value
                    attrib = "".join(ev.split()).split('=')
                    e[attrib[0]] = attrib[1]
                except IndexError:
                    print("You have to attribute a value to the evidence")
                    return q, e, flag, -1
                finally:
                    flag = 2

    print("Query:", q, " Evidence:", e, "Flag:", flag)

    # Execution went OK
    return q, e, flag, 0
