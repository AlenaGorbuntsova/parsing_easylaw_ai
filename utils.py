import pickle


def chunks(xs, n):
    n = max(1, n)
    return [xs[i:i + n] for i in range(0, len(xs), n)]


def read_or_new_pickle(path, default_value = []):
    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except Exception:
        with open(path, "wb") as f:
            pickle.dump(default_value, f)
        print('New file has been created.')
        return []


def pop_elements(full_list, elements):
    for element in elements:
        full_list.remove(element)
