__author__ = "andrey_m"

from numpy import average
import numpy
import pydot


class MyClassifier():
    """ Classifier : contains chosen parameters for fitting
    """
    def __init__(self,
                 min_delta_imp=0,
                 split_stop_min_list_size=10,
                 max_tree_node_amount=100,
                 ):
        self.min_list_size = split_stop_min_list_size
        self.min_delta_imp = min_delta_imp
        self.max_tree_node_amount = max_tree_node_amount
        self.tree = None

    def fit(self, x, y):
        """ Builds decision tree, using Classifier parameters

        :param x: input correct, no-None np.array(n x m) - array of features
        :param y: input correct, no-None np.array(n x 1) - array of targets
        :return: BinaryTree (see BinaryTree.__doc__)
        """
        print "Lets build tree"
        self.tree = BinaryTree()
        self.tree.add_node(x, y)


        tn = self.tree.get_undef_element()
        while tn != '':
            b = tn.check_for_leaf(self.min_list_size)
            if b or len(self.tree.storage) >= self.max_tree_node_amount:
                tn.set_type_leaf()
            else:
                col, border = get_best_separation(tn.data_x, tn.data_y, self.min_delta_imp)

                if col == -1:
                    # Min delta impurity criteria
                    tn.set_type_leaf()
                else:
                    x_lt, y_lt = select_data_less(tn.data_x, tn.data_y, col, border)
                    x_rt, y_rt = select_data_bigger(tn.data_x, tn.data_y, col, border)

                    lt = self.tree.add_node(x_lt, y_lt)
                    rt = self.tree.add_node(x_rt, y_rt)
                    tn.set_condition(col, border)
                    tn.add_leaves(lt, rt)
                    tn.data_x = ''
            tn = self.tree.get_undef_element()
        return self.tree

    def predict(self, X):
        if self.tree is None:
            print "Classifier did not built decision tree yet"
            return None
        targets = []
        for i in range(len(X)):
            node_index = 0
            curr_node = self.tree.storage[node_index]
            while curr_node.type == "node":
                if X[i, curr_node.column] <= curr_node.border:
                    node_index = curr_node.left
                else:
                    node_index = curr_node.right
                curr_node = self.tree.storage[node_index]
            targets.append(curr_node.answer)
        return numpy.array(targets)

    # Calculates absolute error on trained classifier
    def calc_error(self, x, y):
        predicted = self.predict(x)
        err_arr = [abs(y[i]-predicted[i]) for i in range(len(predicted))]
        return sum(err_arr)

    def find_weakest_node(self):
        i = -1
        min_count = 150000
        for k in range(len(self.tree.storage)):
            if self.tree.storage[k].type == "node":
                aov = self.tree.storage[k].amount_of_vectors
                if aov < min_count:
                    min_count = aov
                    i = k
        return i

    def pruning(self, x, y, alpha):
        print "pruning starts with " + str(len(self.tree.storage)) + " nodes"
        r = self.calc_error(x, y) + alpha*len(self.tree.storage)
        r_new = r
        # While we are falling or slowly growing
        while r_new - r < 1 and len(self.tree.storage) > 3:
            r = r_new
            weakest_index = self.find_weakest_node()
            el = self.tree.storage[weakest_index]
            left = el.left
            el.left = -1
            el.right = -1
            # Delete both neighbours-children
            del self.tree.storage[left]
            del self.tree.storage[left]
            el.column = -1
            el.border = -1
            el.set_type_leaf()
            for j in range(weakest_index+1, len(self.tree.storage), 1):
                if self.tree.storage[j].type == "node":
                    self.tree.storage[j].left -= 2
                    self.tree.storage[j].right -= 2
            r_new = self.calc_error(x, y) + alpha*len(self.tree.storage)
        print "pruning ends with " + str(len(self.tree.storage)) + " nodes"
        return self.tree


# Select elements from X[], Y[]: X[k, i]<j
def select_data_less(x, y, i, j):
    good_indexes = [k for k in range(len(x)) if x[k, i] <= j]
    x = x[good_indexes]
    y = y[good_indexes]
    return x, y


def select_data_bigger(x, y, i, j):
    good_indexes = [k for k in range(len(x)) if x[k, i] > j]
    x = x[good_indexes]
    y = y[good_indexes]
    return x, y


# Depending on i - select best separation with maximal DELTA_IMPURITY
def get_best_separation_on_column(x, y, i):

    imp_root = compute_impurity(y)
    root_len = len(x)
    xi = [x[row, i] for row in range(len(x))]
    uq = numpy.unique(xi)

    delta_imp = -100500
    best_border = -1

    for border in uq[0: len(uq)-1]:
        print "Check for " + str(border) + " from X[~, " + str(i) + "]"
        x_left, y_left = select_data_less(x, y, i, border)
        x_right, y_right = select_data_bigger(x, y, i, border)
        imp_left = compute_impurity(y_left)
        imp_right = compute_impurity(y_right)
        new_delta_impurity = imp_root - (len(y_left)*imp_left + len(y_right)*imp_right)/(root_len*1.0)
        if new_delta_impurity > delta_imp:
            delta_imp = new_delta_impurity
            best_border = border
        print ">>Delta impurity = " + str(new_delta_impurity)
    return best_border, delta_imp


def get_best_separation(x, y, mdi):
    delta_imp = -100500
    column = -1
    border = ""

    for i in range(x.shape[1]):
        new_border, new_delta_imp = get_best_separation_on_column(x, y, i)
        if new_delta_imp > delta_imp:
            delta_imp = new_delta_imp
            column = i
            border = new_border
    if delta_imp < mdi:
        return -1, ''
    return column, border


def compute_impurity(ans_vector):
    method = "quad"
    #                                                               Update this with new methods, add into Classifier
    avg = numpy.average(ans_vector)
    imps_on_positions = [(el-avg)**2 for el in ans_vector]
    return numpy.sum(imps_on_positions)


#===================================================================================================Tree implementation

class TreeNode:
    def __init__(self, x, y):
        self.data_x = x
        self.data_y = y
        self.column = -1
        self.border = -1
        self.left = -1
        self.right = -1
        self.type = "undef"
        self.answer = -1
        self.amount_of_vectors = len(y)

    # Add links to subtrees, define type as node
    def add_leaves(self, left, right):
        self.left = left
        self.right = right
        self.type = "node"

    def set_type_leaf(self):
        self.type = "leaf"
        self.answer = average(self.data_y)

    def set_condition(self, col, border):
        self.column = col
        self.border = border

    # Checks current node for chosen criteria of leaf
    def check_for_leaf(self, mls):
        if len(self.data_y) < mls:
            b = True
        else:
            b = False
        return b

    def print_node(self):
        print "node: " + str(self.column) + " " + str(self.border) + " Avg = " + str(self.answer) + " L " + \
            str(self.left) + " R " + str(self.right)


class BinaryTree:
    # Creation of simple array of nodes
    def __init__(self):
        self.storage = []
        self.node_amount = 0

    # Adds new node into array of nodes, returns index
    def add_node(self, x, y):
        node = TreeNode(x, y)
        self.storage.insert(self.node_amount, node)
        self.node_amount += 1
        return self.node_amount-1

    def print_tree(self):
        for i in self.storage:
            i.print_node()

    # Search for some undef-type element - in case of absence - we treated all tree
    def get_undef_element(self):
        for i in self.storage:
            if i.type == "undef":
                return i
        return ''

    def name_of_the_node(self, index, feature_names):
        if self.storage[index].type == "leaf":
            return str(index) + ". avg = " + str(self.storage[index].answer) + \
                ", am = " + str(self.storage[index].amount_of_vectors)
        return str(index) + ". " + feature_names[self.storage[index].column] + " <= " + str(self.storage[index].border)

    def draw_me(self, feature_names, fl='gr.dotfile'):
        print "Drawing starts >>> " + fl
        graph = pydot.Dot(graph_type='graph', graph_name='decision tree')

        for el in range(len(self.storage)):
            n = self.storage[el]
            if (n.type == "node"):
                edge1 = pydot.Edge(self.name_of_the_node(el, feature_names), self.name_of_the_node(n.left, feature_names))
                edge2 = pydot.Edge(self.name_of_the_node(el, feature_names), self.name_of_the_node(n.right, feature_names))
                graph.add_edge(edge1)
                graph.add_edge(edge2)

        graph.write(fl, format='raw', prog='dot')
        print "Drawing complete"