from parser import parser, debug, queryParser


# Core Algorithm
def core(nodes, names, q, e, flag, debug):
    for key, value in nodes[q].probs.items():
        print(key, nodes[q].classes, value)

    order = elimOrder(nodes, names)
    for var in order:
        for f in nodes[var].factor:
            pass


# Determines variable topological elimination order
def elimOrder(nodes, names):
    order = []
    nxt = []
    # parents of a node go before node
    for n in names:
        if len(order) == 0:
            order = nodes[n].parent + [n]
        else:
            for p in nodes[n].parent:
                if p not in order:
                    order += [p]
            order += [n]
    return order


if __name__ == "__main__":
    es = {}
    print("Input BIF file name w/o extension")
    file = str(input())
    nodes, names = parser(file)
    debug(nodes)
    print("Available Variables: ", names)
    print("Pr? ", end='')
    query = str(input())
    q, e, flag, f = queryParser(query)
    while True:
        if q not in names:
            print("Error, ", q, " not available.")
            f = -1
        else:
            for ev in e:
                if ev not in names:
                    print("Error, ", ev, " not available.")
                    f = -1
        if f == -1:
            print("Available variables: ", names)
            print("Try again. Pr? ", end='')
            query = str(input())
            q, e, flag, f = queryParser(query)
        else:
            break

    core(nodes, names, q, e, flag, True)
