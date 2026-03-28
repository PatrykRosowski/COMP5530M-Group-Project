import pickle


# Accept input as list of strings, save this list to a JSON file.
def save_path(path: list[str], loc: str):

    # Saving path to a file using pickle, to the desired location
    with open(loc, "wb") as fp:
        pickle.dump(path, fp)


# Accept input as location, and retrieve path
def load_path(loc: str):

    # Loading from a file using pickle, from the desired location
    with open(loc, "rb") as fp:
        path = pickle.load(fp)

    return path
