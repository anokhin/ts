"""
Count the number of hits for each user_id
"""

__author__ = 'Nikolay Anokhin'


class Mapper:

    def __init__(self):
        with open("ids.txt", "rU") as ids_file:
            self.ids = dict(line.strip().lower().split() for line in ids_file)

    def __call__(self, key, value):
        items = value.split("\t")
        user_id = items[0]
        if user_id in self.ids:
            yield user_id, 1


def reducer(key, values):
    yield key, sum(values)


if __name__ == "__main__":
    import dumbo
    dumbo.run(Mapper, reducer, combiner=reducer)
