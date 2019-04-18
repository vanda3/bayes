from parser import parser, debug, queryParser


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

    perms = []

    # For all possible values of all vars, create a permutation and add it to the list
    # i.e:
    #
    # perm = [{'Pollution': 'high', 'Smoker': 'True'}, {'Pollution': 'high', 'Smoker': 'False'},
    #         {'Pollution': 'low', 'Smoker': 'True}, {'Pollution': 'low', 'Smoker': 'False'}]
    # perms.append(perm)
    #
    # Problem: Not all vars have the same possible values (Not all vars are 'True' and 'False'.
    #          How do we create permutations of that?

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
    perms = gen_perms(factor_vars)

    # To be continued...

    return


def init_factors(nodes, order, q, e):
    elimd = []
    factors = []
    i = 0
    while len(elimd) != len(order):
        # filter vars that were eliminated
        variables = filter(lambda var: var not in elimd, list(nodes.keys()))

        # filter vars that have children yet not eliminated
        variables = filter(lambda var: all(child in elimd for child in nodes[var].child), variables)

        # list, containing the unknown variables of the factor to be created
        factor_vars = [parent for parent in nodes[order[i]].parent if parent not in e]

        # make the factor
        if len(factor_vars) > 0:  # Is this really needed?
            factors.append(make_factor(nodes, order[i], factor_vars, e))

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
