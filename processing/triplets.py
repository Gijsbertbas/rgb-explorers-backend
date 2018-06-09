# Processing file for generating the triplets to simulate.
# No flask here


def generate_triplets():
    """
    Generates the list of triplets that we would like to simulate.
    :return: The list of triplets, like ((20, 40, 60), (30, 50, 70), ...).
    """
    return ((20, 40, 60),
            (25, 40, 550),
            (30, 50, 70))
