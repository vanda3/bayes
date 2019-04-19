from parser import parser, debug, queryParser
from copy import deepcopy
from ast import literal_eval


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


def process_query(var, perm, nodes):
    """
    Gets the probability for the permutation
    :param var:     The variable we query
    :param perm:    The permutation in question
    :param nodes:   The network
    :return:        A tuple (query / permutation, probability)
    """

    # The variable has no parents. Just return the probability it has set for that evidence value.
    if len(nodes[var].parent) == 0:
        query_values = (literal_eval(nodes[var].probs[0]), nodes[var].probs[1][0])
    # The variable has parents. Query its probability
    else:
        prob = nodes[var].getProbability(perm)      # Get the probability
        query_values = (str(perm), prob)

    # print(query_values)
    return query_values


def make_factor(nodes, var, e):
    """
    Create a factor
    :param nodes:           The network
    :param var:             The selected variable's name.
    :param e:               Dictionary of the evidence
    :return:                A list of the probabilities for the possible permutations
    """

    all_vars = []
    for parent in nodes[var].parent:
        all_vars.append(parent)
    # all_vars.append(var)               # All variables involved in the factor, including the evidence

    # Generate the permutations (Need all the possible values of the variables)
    perms = gen_perms(all_vars)

    # Filter out permutations not in accord with the evidence
    old_perms = deepcopy(perms)
    for perm in old_perms:
        for key, value in e.items():
            if key in perm.keys():
                if perm[key] != value:
                    # Remove the permutations that don't match the evidence
                    perms.remove(perm)
                else:
                    # Remove the evidence from the permutations that match it
                    # perms[perms.index(perm)].pop(key)
                    continue

    # Calculate probability for each permutation
    probabilities = {}
    for perm in perms:
        prob = process_query(var, perm, nodes)
        if var in probabilities:
            probabilities[var].append(prob)
        else:
            probabilities[var] = [prob]

    return probabilities


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
        variables = filter(lambda var: all(child in elimd for child in nodes[var].child), variables)

        # list, containing the unknown variables of the factor to be created
        factor_vars = [parent for parent in nodes[order[i]].parent if parent not in e.keys()]

        print("Factor vars of " + order[i] + ": " + str(factor_vars))

        # make the factor
        if len(factor_vars) > 0:
            factors.append(make_factor(nodes, order[i], e))

        print()
        i += 1      # This is just so that the loop stops. It isn't a part of the code
        # To be continued...

    print(factors)

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
