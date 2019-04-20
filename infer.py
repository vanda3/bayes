from parser import parser, debug, queryParser
from copy import deepcopy
from ast import literal_eval


# Core Algorithm
def core(nodes, names, q, e, flag, debug):
    for key, value in nodes[q].probs.items():
        print(key, nodes[q].classes, value)

    order = elimOrder(nodes, names, q, e)
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
    if nodes[var].isRoot():
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
    all_vars.append(var)               # All variables involved in the factor, including the evidence

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


def check_var_in_value(var, value):
    """
    :param var:         The queried var
    :param value:       List of tuples (permutation, probability)
    :return:            True, if var is in the permutation; false, otherwise
    """
    for val in value:
        if var in literal_eval(val[0]).keys():
            return True
    return False


def product(nodes, var, factorA, factorB):
    return 0


def sum_out(nodes, var, factors):
    """
    Sum out factors, based on var
    :param nodes:       The network
    :param var:         The var to remove
    :param factors:     List of factors in form of ({'var': [entries]})
    :return:            List of new factors
    """

    print()
    factors_with_var = []
    indices_to_remove = []
    for i, factor in enumerate(factors):
        for _, value in factor.items():
            if check_var_in_value(var, value):
                factors_with_var.append(factor)
                indices_to_remove.append(i)

    if len(factors_with_var) > 1:
        for i in reversed(indices_to_remove):
            del factors[i]

        result = factors_with_var[0]
        for factor in factors_with_var[1:]:
            result = product(nodes, var, result, factor)
        factors.append(result)

    # SUM-OUT OPERATION
    # For each factor:
    # Calculate the table of the new factor

    # If the only value that changed in a permutation is the value of
    # the variable we are eliminating, sum the probabilities of those permutations
    # i.e:
    #   C   X   Prob            Eliminating X:      C   Prob
    #   T   p   0.9                                 T   1.0 (0.9 + 0.1)
    #   T   n   0.1                                 F   1.0 (0.2 + 0.8)
    #   F   p   0.2
    #   F   n   0.8                              (Only 2 permutations, not 4)

    #   C   D   Prob            Eliminating D:      C   Prob
    #   T   T   0.65                                T   1.0 (0.65 + 0.35)
    #   T   F   0.35                                F   1.0 (0.3 + 0.7)
    #   F   T   0.3
    #   F   F   0.7                              (Only 2 permutations, not 4)

    final_probabilities = []
    # We need to normalize the probabilities (divide each by the total of the sum)
    for i, factor in enumerate(factors):
        # Get the tuple (permutation, probability)
        for _, lst in factor.items():
            for tup in lst:
                perm = literal_eval(tup[0])
                for v in perm.keys():
                    if v == var:
                        # Calculate the probabilities
                        var_probabilities = []  # List of tuples [(remaining_perm, probability)]

                        # The "remaining perm" is the perm without the var we are summing out
                        remaining_perm = deepcopy(perm)
                        remaining_perm.pop(var)

                        # Search for the "remaining perm" in the tuples of the list
                        # Sum the values of the probabilities on the cases
                        # where the "remaining perm" matches
                        for tup2 in lst:
                            check_perm = literal_eval(tup2[0])
                            if all(check_perm[key_perm] == val_perm for key_perm, val_perm in remaining_perm.items()):
                                if len(var_probabilities) == 0:
                                    var_probabilities = [(str(remaining_perm), tup2[1])]
                                else:
                                    old_var_prob = deepcopy(var_probabilities)
                                    for tup3 in old_var_prob:
                                        if str(remaining_perm) == tup3[0]:
                                            prob = tup3[1] + tup2[1]
                                            var_probabilities.remove(tup3)
                                            var_probabilities.append((str(remaining_perm), prob))
                                        else:
                                            var_probabilities.append((str(remaining_perm), tup2[1]))

                        # Check if the tuple has already been calculated
                        for tup in var_probabilities:
                            if tup not in final_probabilities:
                                final_probabilities.append(tup)

    # TODO: We still need to normalize the probabilities
    # Swap the list of the factor by the list final_probabilities
    for item in factors:
        # print(item)
        if var in item.keys():
            item[var] = final_probabilities

    print(factors)

    return factors


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

        # make the factor
        if len(factor_vars) > 0:
            factors.append(make_factor(nodes, order[i], e))

        factors = sum_out(nodes, order[i], factors)

        i += 1      # This is just so that the loop stops. It isn't a part of the code
        # To be continued...

    # print(factors)

    return factors


# Determines variable topological elimination order
def elimOrder(nodes, names, q, e):
    order = []
    nxt = []
    unav = [q]
    for k in e.keys():
        unav.append(k)
    # parents of a node go before node
    for n in names:
        if n not in unav:
            if len(order) == 0:
                order = nodes[n].parent + [n]
            else:
                for p in nodes[n].parent:
                    if p not in order and p not in unav:
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
    q, e, flag, f = queryParser(query, nodes)
    while True:
        if q not in names:
            print("Error. ", q, " not available.")
            print("Available variables: ", names)
            f = -1
        else:
            for ev in e:
                if ev not in names:
                    print("Error. ", ev, " not available.")
                    print("Available variables: ", names)
                    f = -1
                if e[ev] not in nodes[ev].classes:
                    print("Error. ", e[ev], " isn't a valid value.")
                    print("Available values for variable ",ev,": ",nodes[ev].classes,".")
                    f= -1
        if f == -1:
            print("Try again. Pr? ", end='')
            query = str(input())
            q, e, flag, f = queryParser(query, nodes)
        else:
            break

    core(nodes, names, q, e, flag, True)