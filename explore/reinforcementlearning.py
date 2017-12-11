from sys import stderr
import scipy
from scipy.sparse.linalg import spsolve
import numpy as np
from numpy import linalg

def linrel(articles, feedback, data, start, n, from_date, to_date, mew=1.0, exploration_rate=1.0) :
    assert len(articles) == len(feedback), "articles and feedback are not the same length"

    num_articles,num_features = data.shape

    X_t = data[ np.array(articles) ]
    Y_t = np.matrix(feedback).transpose()
    I = mew * scipy.sparse.identity(num_features, format='dia')

    W = spsolve((X_t.transpose() * X_t) + (mew * I), X_t.transpose())
    #K = W * Y_t # keyword weights
    A = data * W
    normL2 = np.matrix(linalg.norm(A.todense(), axis=1)).transpose()

    mean = A * Y_t
    variance = (exploration_rate / 2.0) * normL2
    I_t = mean + variance

    linrel_ordered = np.argsort(I_t.transpose()[0]).tolist()[0]
    top_n = []

    for i in linrel_ordered[::-1] :
        if i not in articles :
            top_n.append(i)

        if len(top_n) == n :
            break

    return top_n, None, None, None

