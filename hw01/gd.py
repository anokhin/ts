import numpy
import sklearn.datasets
import pylab
from GDAlgorithm import GDAlgorithm
def select_objects(x, y, species, axis1, axis2):
    selected_items = [i for i, t in enumerate(y) if t in species]
    return x[selected_items][:, [axis1, axis2]], y[selected_items]


def plot_data_set(x, y, clf=None, description=''):
    x = x.transpose()
    print "Plotting data"
    pylab.figure(figsize=(10, 10))

    colors = numpy.array(['r', 'g', 'b'])[y]
    pylab.title(description, fontsize='small')
    pylab.scatter(x[:, 0], x[:, 1], marker='^', c=colors, s=100)

    if clf:
        add_decision_function_to_plot(x[:, 0].min(), x[:, 0].max(), x[:, 1].min(), x[:, 1].max(), clf)

    #pylab.show()

def add_decision_function_to_plot(x_1_min, x_1_max, x_2_min, x_2_max, clf):
    x1s = numpy.linspace(x_1_min, x_1_max, 10)
    x2s = numpy.linspace(x_2_min, x_2_max, 10)

    x1, x2 = numpy.meshgrid(x1s, x2s)
    z = numpy.ones(x1.shape)

    for (i, j), v1 in numpy.ndenumerate(x1):
        v2 = x2[i, j]
        p = clf.decision_function([v1, v2])
        z[i, j] = p[0]

    pylab.contour(x1, x2, z, [0.0], colors='k', linestyles='dashed', linewidths=2.5)

def main():
    # Load Iris data set
    data = sklearn.datasets.load_iris()
    # Axes used for classification/visualization
    axis1 = 0
    axis2 = 1
    # Select objects of the specified class and axis
    x, y = select_objects(data['data'], data['target'], [0, 1], axis1, axis2)
    x = x.transpose()
    y[(y < 1)] = -1
    #plot_data_set(x, y)

    gd = GDAlgorithm()
    gd.fit(x, y)
    plot_data_set(x, y, clf = gd)

    pylab.show()


if __name__ == "__main__":
    main()


