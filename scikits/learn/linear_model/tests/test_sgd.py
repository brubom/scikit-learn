import numpy as np
from scikits.learn import linear_model
from numpy.testing import assert_array_equal
from numpy.testing import assert_almost_equal

import unittest
from nose.tools import raises
from nose.tools import assert_raises

# test sample 1
X = np.array([[-2, -1], [-1, -1], [-1, -2], [1, 1], [1, 2], [2, 1]])
Y = [1, 1, 1, 2, 2, 2]
T = np.array([[-1, -1], [2, 2], [3, 2]])
true_result = [1, 2, 2]

# test sample 2
X2 = np.array([[-1, 1], [-0.75, 0.5], [-1.5, 1.5],
               [1, 1], [0.75, 0.5], [1.5, 1.5],
               [-1, -1], [0, -0.5], [1, -1]])
Y2 = [1, 1, 1, 2, 2, 2, 3, 3, 3]
T2 = np.array([[-1.5, 0.5], [1, 2], [0, -2]])
true_result2 = [1, 2, 3]

# test sample 3
X3 = np.array([[1,1,0,0,0,0], [1,1,0,0,0,0],
               [0,0,1,0,0,0], [0,0,1,0,0,0],
               [0,0,0,0,1,1], [0,0,0,0,1,1],
               [0,0,0,1,0,0], [0,0,0,1,0,0]])
Y3 = np.array([1, 1, 1, 1, 2, 2, 2, 2])

# test sample 4 - two more or less redundent feature groups
X4 = np.array([[1,0.9,0.8,0,0,0], [1,.84,.98,0,0,0],
               [1,.96,.88,0,0,0], [1,.91,.99,0,0,0],
               [0,0,0,.89,.91,1], [0,0,0,.79,.84,1],
               [0,0,0,.91,.95,1], [0,0,0,.93,1,1]])
Y4 = np.array([1, 1, 1, 1, 2, 2, 2, 2])


class DenseSGDClassifierTestCase(unittest.TestCase):
    """Test suite for the dense representation variant of SGD"""

    factory = linear_model.SGDClassifier

    def test_sgd(self):
        """Check that SGD gives any results :-)"""

        clf = self.factory(penalty='l2', alpha=0.01, fit_intercept=True,
                      n_iter=10, shuffle=True)
        clf.fit(X, Y)
        #assert_almost_equal(clf.coef_[0], clf.coef_[1], decimal=7)
        assert_array_equal(clf.predict(T), true_result)

    def test_sgd_penalties(self):
        """Check whether penalties and hyperparameters are set properly"""
        clf = self.factory(penalty='l2')
        assert clf.rho == 1.0
        clf = self.factory(penalty='l1')
        assert clf.rho == 0.0
        clf = self.factory(penalty='elasticnet', rho=0.85)
        assert clf.rho == 0.85

    @raises(ValueError)
    def test_sgd_bad_penalty(self):
        """Check whether expected ValueError on bad penalty"""
        clf = self.factory(penalty='foobar', rho=0.85)

    def test_sgd_losses(self):
        """Check whether losses and hyperparameters are set properly"""
        clf = self.factory(loss='hinge')
        assert isinstance(clf.loss_function, linear_model.Hinge)

        clf = self.factory(loss='log')
        assert isinstance(clf.loss_function, linear_model.Log)

        clf = self.factory(loss='modified_huber')
        assert isinstance(clf.loss_function, linear_model.ModifiedHuber)

    @raises(ValueError)
    def test_sgd_bad_loss(self):
        """Check whether expected ValueError on bad loss"""
        clf = self.factory(loss="foobar")

    @raises(ValueError)
    def test_sgd_n_iter_param(self):
        """Test parameter validity check"""
        clf = self.factory(n_iter=-10000)

    @raises(ValueError)
    def test_sgd_shuffle_param(self):
        """Test parameter validity check"""
        clf = self.factory(shuffle="false")

    @raises(TypeError)
    def test_arument_coef(self):
        """Checks coef_init not allowed as model argument (only fit)"""
        # Provided coef_ does not match dataset.
        clf = self.factory(coef_init=np.zeros((3,))).fit(X, Y)

    @raises(ValueError)
    def test_provide_coef(self):
        """Checks coef_init shape for the warm starts"""
        # Provided coef_ does not match dataset.
        clf = self.factory().fit(X, Y, coef_init=np.zeros((3,)))

    @raises(ValueError)
    def test_set_intercept(self):
        """Checks intercept_ shape for the warm starts"""
        # Provided intercept_ does not match dataset.
        clf = self.factory().fit(X, Y, intercept_init=np.zeros((3,)))

    @raises(ValueError)
    def test_sgd_at_least_two_labels(self):
        """Target must have at least two labels"""
        self.factory(alpha=0.01, n_iter=20).fit(X2, np.ones(9))

    def test_sgd_multiclass(self):
        """Multi-class test case"""
        clf = self.factory(alpha=0.01, n_iter=20).fit(X2, Y2)
        assert clf.coef_.shape == (3, 2)
        assert clf.intercept_.shape == (3,)
        assert clf.decision_function([0, 0]).shape == (1, 3)
        pred = clf.predict(T2)
        assert_array_equal(pred, true_result2)

    def test_sgd_multiclass_with_init_coef(self):
        """Multi-class test case"""
        clf = self.factory(alpha=0.01, n_iter=20)
        clf.fit(X2, Y2, coef_init=np.zeros((3, 2)),
                intercept_init=np.zeros(3))
        assert clf.coef_.shape == (3, 2)
        assert clf.intercept_.shape == (3,)
        pred = clf.predict(T2)
        assert_array_equal(pred, true_result2)

    def test_sgd_multiclass_njobs(self):
        """Multi-class test case with multi-core support"""
        clf = self.factory(alpha=0.01, n_iter=20, n_jobs=2).fit(X2, Y2)
        assert clf.coef_.shape == (3, 2)
        assert clf.intercept_.shape == (3,)
        assert clf.decision_function([0, 0]).shape == (1, 3)
        pred = clf.predict(T2)
        assert_array_equal(pred, true_result2)

    def test_set_coef_multiclass(self):
        """Checks coef_init and intercept_init shape for for multi-class
        problems"""
        # Provided coef_ does not match dataset
        clf = self.factory()
        assert_raises(ValueError, clf.fit, X2, Y2, coef_init=np.zeros((2, 2)))

        # Provided coef_ does match dataset
        clf = self.factory().fit(X2, Y2, coef_init=np.zeros((3,2)))

        # Provided intercept_ does not match dataset
        clf = self.factory()
        assert_raises(ValueError, clf.fit, X2, Y2,
                      intercept_init=np.zeros((1,)))

        # Provided intercept_ does match dataset.
        clf = self.factory().fit(X2, Y2, intercept_init=np.zeros((3,)))

    def test_sgd_proba(self):
        """Check SGD.predict_proba for log loss only"""

        # hinge loss does not allow for conditional prob estimate
        clf = self.factory(loss="hinge", alpha=0.01, n_iter=10).fit(X, Y)
        assert_raises(NotImplementedError, clf.predict_proba, [3, 2])

        # log loss implements the logistic regression prob estimate
        clf = self.factory(loss="log", alpha=0.01, n_iter=10).fit(X, Y)
        p = clf.predict_proba([3, 2])
        assert p > 0.5
        p = clf.predict_proba([-1, -1])
        assert p < 0.5

    def test_sgd_l1(self):
        """Test L1 regularization"""
        n = len(X4)
        np.random.seed(13)
        idx = np.arange(n)
        np.random.shuffle(idx)

        X = X4[idx, :]
        Y = Y4[idx, :]

        clf = self.factory(penalty='l1', alpha=.2, fit_intercept=False,
                           n_iter=2000)
        clf.fit(X, Y)
        assert_array_equal(clf.coef_[1:-1], np.zeros((4,)))

        pred = clf.predict(X)
        assert_array_equal(pred, Y)


class SparseSGDClassifierTestCase(DenseSGDClassifierTestCase):
    """Run exactly the same tests using the sparse representation variant"""

    factory = linear_model.sparse.SGDClassifier


class DenseSGDRegressorTestCase(unittest.TestCase):
    """Test suite for the dense representation variant of SGD"""

    factory = linear_model.SGDRegressor

    def test_sgd(self):
        """Check that SGD gives any results."""
        clf = self.factory(alpha=0.1, n_iter=2,
                           fit_intercept=False)
        clf.fit ([[0, 0], [1, 1], [2, 2]], [0, 1, 2])
        assert clf.coef_[0] == clf.coef_[1]

    def test_sgd_penalties(self):
        """Check whether penalties and hyperparameters are set properly"""
        clf = self.factory(penalty='l2')
        assert clf.rho == 1.0
        clf = self.factory(penalty='l1')
        assert clf.rho == 0.0
        clf = self.factory(penalty='elasticnet', rho=0.85)
        assert clf.rho == 0.85

    @raises(ValueError)
    def test_sgd_bad_penalty(self):
        """Check whether expected ValueError on bad penalty"""
        clf = self.factory(penalty='foobar', rho=0.85)

    def test_sgd_losses(self):
        """Check whether losses and hyperparameters are set properly"""
        clf = self.factory(loss='squared_loss')
        assert isinstance(clf.loss_function, linear_model.SquaredLoss)

        clf = self.factory(loss='huber', p=0.5)
        assert isinstance(clf.loss_function, linear_model.Huber)
        assert clf.p == 0.5

    @raises(ValueError)
    def test_sgd_bad_loss(self):
        """Check whether expected ValueError on bad loss"""
        clf = self.factory(loss="foobar")

    def test_sgd_least_squares_fit(self):
        xmin, xmax = -5, 5
        n_samples = 100
        X = np.linspace(xmin, xmax, n_samples).reshape(n_samples, 1)

        # simple linear function without noise
        y = 0.5 * X.ravel()

        clf = self.factory(loss='squared_loss', alpha=0.1, n_iter=20,
                           fit_intercept=False)
        clf.fit(X, y)
        score = clf.score(X, y)
        assert  score > 0.99

        # simple linear function with noise
        y = 0.5 * X.ravel() \
            + np.random.randn(n_samples, 1).ravel()

        clf = self.factory(loss='squared_loss', alpha=0.1, n_iter=20,
                           fit_intercept=False)
        clf.fit(X, y)
        score = clf.score(X, y)
        assert  score > 0.5

    def test_sgd_huber_fit(self):
        xmin, xmax = -5, 5
        n_samples = 100
        X = np.linspace(xmin, xmax, n_samples).reshape(n_samples, 1)

        # simple linear function without noise
        y = 0.5 * X.ravel()

        clf = self.factory(loss="huber", p=0.1, alpha=0.1, n_iter=20,
                           fit_intercept=False)
        clf.fit(X, y)
        score = clf.score(X, y)
        assert  score > 0.99

        # simple linear function with noise
        y = 0.5 * X.ravel() \
            + np.random.randn(n_samples, 1).ravel()

        clf = self.factory(loss="huber", p=0.1, alpha=0.1, n_iter=20,
                           fit_intercept=False)
        clf.fit(X, y)
        score = clf.score(X, y)
        assert  score > 0.5

    def test_elasticnet_convergence(self):
        """Check that the SGD ouput is consistent with coordinate descent"""

        n_samples, n_features = 1000, 5
        np.random.seed(0)
        X = np.random.randn(n_samples, n_features)
        # ground_truth linear model that generate y from X and to which the
        # models should converge if the regularizer would be set to 0.0
        ground_truth_coef = np.random.randn(n_features)
        y = np.dot(X, ground_truth_coef)

        # XXX: alpha = 0.1 seems to cause convergence problems
        for alpha in [0.01, 0.001]:
            for rho in [0.5, 0.8, 1.0]:
                cd = linear_model.ElasticNet(alpha=alpha, rho=rho,
                                             fit_intercept=False)
                cd.fit(X, y)
                sgd = self.factory(penalty='elasticnet', n_iter=50,
                                   alpha=alpha, rho=rho, fit_intercept=False)
                sgd.fit(X, y)
                err_msg = ("cd and sgd did not converge to comparable "
                           "results for alpha=%f and rho=%f" % (alpha, rho))
                assert_almost_equal(cd.coef_, sgd.coef_, decimal=2,
                                    err_msg=err_msg)


class SparseSGDRegressorTestCase(DenseSGDRegressorTestCase):
    """Run exactly the same tests using the sparse representation variant"""

    factory = linear_model.sparse.SGDRegressor
