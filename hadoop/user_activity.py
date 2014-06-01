"""
Count the number of hits for each user_id
"""

__author__ = 'Nikolay Anokhin'


class Mapper:

    def __init__(self):
        self.ids = {}
        with open("tv_train.txt", "rU") as ids_file:
            for line in ids_file:
                items = line.strip().split("\t")
                if len(items) == 2:
                    self.ids[items[0]] = items[1]
                if len(self.ids) > 100000:
                    break


    def __call__(self, key, value):
        items = value.split("\t")
        user_id = items[0]
        gender_str = items[2]
        age_str = items[3]
        # if user_id in self.ids:
        if True:
            if gender_str != "None":
                gender = int(gender_str)
                if gender:
                    yield user_id, ("female", 1)
                else:
                    yield user_id, ("male", 1)
            if age_str != "None":
                age = int(age_str)
                if 10 < age < 80:
                    yield user_id, ("age", age)


def reducer(key, values):
    ages = []
    male_count = 0
    female_count = 0
    for feature, value in values:
        if feature == "female":
            female_count += value
        elif feature == "male":
            male_count += value
        elif feature == "age":
            ages.append(value)
    if ages:
        yield key, ("age", float(sum(ages)) / len(ages))
    yield key, ("female", female_count)
    yield key, ("male", male_count)


if __name__ == "__main__":
    import dumbo
    dumbo.run(Mapper, reducer, combiner=reducer)
