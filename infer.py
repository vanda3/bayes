from parser import parser, debug, queryParser
from copy import deepcopy


# Core Algorithm
def core(nodes, names, q, e, flag, debug):
    for key, value in nodes[q].probs.items():
        print(key, nodes[q].classes, value)

    order = elimOrder(nodes, names)
    factors = init_factors(nodes, order, q, e)
    for var in order:
        for f in nodes[var].factor:
            pass


def gen_perms(vars):
    """
    Generate the permutations
    :param vars: A list of the variables we want to permutate
    :return: A list of the possible permutations
    """

    # For all possible values of all vars, create a permutation and add it to the list
    perms = []
    for var in vars:
        if len(perms) == 0:
            for value in nodes[var].classes:
                perms.append({var: value})
        else:
            classes = nodes[var].classes
            old_perms = perms
            for i in range(1, len(classes)):
                perms = perms + deepcopy(old_perms)

            for i in range(0, int(len(perms) / len(classes))):
                for j in range(0, len(classes)):
                    perms[i + j * int(len(perms) / len(classes))][var] = classes[j]

    return perms


def make_factor(nodes, var, factor_vars, e):
    """
    Create a factor
    :param nodes:           The network
    :param var:             The selected variable's name.
    :param factor_vars:     List of factor vars for the selected var.
    :param e:               Dictionary of the evidence
    :return:
    """

    all_vars = []
    for parent in nodes[var].parent:
        all_vars.append(parent)
    all_vars.append(var)               # All variables involved in the factor, including the evidence

    # Generate the permutations (Need all the possible values of the variables)
    perms = gen_perms(all_vars)
    print("Permutations for " + var + "\n" + str(perms))

    # To be continued...

    return


def init_factors(nodes, order, q, e):
    elimd = []
    factors = []
    i = 0
    print()
    while len(elimd) != len(order):
        if i == len(order):
            break

        # filter vars that were eliminated
        variables = filter(lambda var: var not in elimd, list(nodes.keys()))

        # filter vars that have children yet not eliminated
        # variables = filter(lambda var: all(child in elimd for child in nodes[var].child), variables)

        # list, containing the unknown variables of the factor to be created
        factor_vars = [parent for parent in nodes[order[i]].parent if parent not in e]

        print("Factor vars of " + order[i] + ": " + str(factor_vars))

        # make the factor
        if len(factor_vars) > 0:  # Is this really needed?
            factors.append(make_factor(nodes, order[i], factor_vars, e))

        print()
        i += 1      # This is just so that the loop stops. It isn't a part of the code
        # To be continued...

    return factors

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
