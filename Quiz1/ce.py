import pandas as pd

class Samples(object):
    attributes = ()
    factors = {}

    def __init__(self, filename):
        self.data = pd.read_csv(filename)
        self.attributes = self.data.columns.values.tolist()[:-1]
        for i in self.attributes:
            self.factors[i] = []
            temp = list(self.data[i].drop_duplicates())
            self.factors[i] = temp
        self.data = tuple(self.data.values)


class CandidateElimination(object):
    def __init__(self, samples):
        self.num_attr = len(samples.attributes)
        self.factors = samples.factors
        self.attr = samples.attributes
        self.data_set = samples.data

    def run(self):
        s = self.initial_s()
        g = self.initial_g()
        times = 0
        for sample in self.data_set:
            print('S' + str(times), s)
            print('G' + str(times), g)
            times += 1
            print('First' + str(times) + 'Sample', sample)
            if g == [] or s == [None]:
                raise ArithmeticError
            if self.is_positive(sample):
                g = self.remove_inconsistent_g(g, sample[:-1])
                s_new = s[:]
                for each_s in s:
                    if not self.consistent(each_s, sample):
                        s_new.remove(each_s)
                        s_mini_paradigm = self.minimalist_paradigm(each_s, sample, g)
                        s_new.append(s_mini_paradigm)
                        s_new = self.remove_more_general(s_new)
                s = s_new[:]
            elif self.is_negative(sample):
                s = self.remove_inconsistent_s(s, sample[:-1])
                g_new = g[:]
                for each_g in g:
                    if self.consistent(each_g, sample):
                        g_new.remove(each_g)
                        g_mini_special = self.minimal_specialization(each_g, sample, s)
                        g_new += g_mini_special
                        g_new = self.remove_more_special(g_new)
                g = g_new[:]
        print("S:", s)
        print("G:", g)
        self.get_concept(s, g)

    def initial_s(self):
        return [tuple(['/' for factor in range(self.num_attr)])]

    def initial_g(self):
        return [tuple(['?' for factor in range(self.num_attr)])]

    @staticmethod
    def is_positive(sample):
        if sample[-1] == 'Y':
            return True
        elif sample[-1] == 'N':
            return False
        else:
            raise TypeError("invalid target value")

    @staticmethod
    def is_negative(sample):
        if sample[-1] == 'N':
            return True
        elif sample[-1] == 'Y':
            return False
        else:
            raise TypeError("invalid target value")

    def remove_inconsistent_g(self, g, sample):
        set_new = g[:]
        for each_set in set_new:
            if not self.consistent(each_set, sample):
                g.remove(each_set)
        return g

    def remove_inconsistent_s(self, s, sample):
        set_new = s
        for each_set in set_new:
            if self.consistent(each_set, sample):
                set_new.remove(each_set)
        return set_new

    def consistent(self, a, b):
        for i in range(self.num_attr):
            if not self.match_factor(a[i], b[i]):
                return False
        return True

    @staticmethod
    def match_factor(i, j):
        if i == '?' or j == '?':
            return True
        elif i == j:
            return True
        return False

    def minimalist_paradigm(self, concept, sample, g):
        hypo = list(concept)
        for i, factor in enumerate(hypo):
            if factor == '/':
                hypo[i] = sample[i]
            elif not self.match_factor(factor, sample[i]):
                hypo[i] = '?'
        h = tuple(hypo)
        for each_g in g:
            if self.more_general(each_g, h):
                return h
        return None

    @staticmethod
    def more_general(a, b):
        hyp = zip(a, b)
        for i, j in hyp:
            if i == '?':
                continue
            elif j == '?':
                if i != '?':
                    return False
            elif i != j:
                return False
            else:  # i==j
                continue
        return True

    def remove_more_general(self, s):
        for s_i in s:
            for s_j in s:
                if s_i != s_j and self.more_general(s_i, s_j):
                    s.remove(s_j)
        return list(set(s))

    def minimal_specialization(self, concept, sample, s):
        h = []
        hypo = list(concept)
        for i, factor in enumerate(hypo):
            if factor == '?':
                values = self.factors[self.attr[i]]
                for j in values:
                    if sample[i] != j:
                        hyp = hypo[:]
                        hyp[i] = j
                        for k, each in enumerate(hyp):
                            if each == "?":
                                continue
                            elif each == sample[k]:
                                hyp[k] = '?'
                        hyp = tuple(hyp)
                        for each_s in s:
                            if self.more_general(hyp, each_s) or each_s == self.initial_s()[0]:
                                h.append(hyp)
                                break
        return h

    def remove_more_special(self, g):
        for g_i in g:
            for g_j in g:
                if g_i != g_j and self.more_general(g_j, g_i):
                    g.remove(g_j)
        return list(set(g))

    def get_concept(self, s, g):
        concepts = []
        for each_s in s:
            for each_g in g:
                for i in range(self.num_attr):
                    new_concept = list(each_g)[:]
                    if each_s[i] == each_g[i]:
                        continue
                    elif each_g[i] == '?':
                        new_concept[i] = each_s[i]
                        concepts.append(tuple(new_concept))
        print(set(self.remove_more_special(concepts)))


if __name__ == "__main__":
    samples = Samples("tennis.csv")
    algorithm = CandidateElimination(samples)
    algorithm.run()