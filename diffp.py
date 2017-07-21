import math
import random

def e_m(D, utilityF, sensitivity, S, epsilon):
    scores = (utilityF(D, e) for e in S)
    return e_m_scores(S, scores, sensitivity, epsilon)

def e_m_scores(S, quality_scores, sensitivity, epsilon):
    """Exponential mechanism samples value from list S based on
    quality_scores.  S and quality_scores must be parallel lists.
    """
    scores = compute_unnormalized_scores(quality_scores, sensitivity, epsilon)
    idx = sample(normalize(scores))
    return S[idx]

def compute_unnormalized_scores(quality_scores, sensitivity, epsilon):
    exp_vector = [float(epsilon) * score / (2.0 * sensitivity) for score in quality_scores]
    max_val = max(exp_vector)
    # subtract off largest before exponentiating to avoid math overflow
    # note: "underflow" may cause some values to be 0, rather than very small -- that's acceptable in this case
    exp_vector = [math.exp(val - max_val) for val in exp_vector]
    return exp_vector

def sample(prob):
    assert abs(sum(prob) - 1.0) < 0.000001, "Probability vector does not sum to 1!"
    r = random.random()
    i = 0
    n = 0
    while n <= r:
        n += prob[i]
        i += 1
    return i - 1

def normalize(xs):
    tot = sum(xs)
    return [float(x)/tot for x in xs]

def noisy_count(N, epsilon):
    # https://en.wikipedia.org/wiki/Laplace_distribution#Generating_random_variables_according_to_the_Laplace_distribution
    b = 1.0 / epsilon
    u = random.uniform(-0.5, 0.5)
    return N + (-1 * b * sgn(u) * math.log(1 - 2 * math.fabs(u)))

def sgn(n):
    if n >= 0:
        return 1
    else:
        return -1


if __name__ == "__main__":

    # draw random samples from noisy_count and plot them
    # a poor man's test to make sure they look about right
    import matplotlib.pyplot as plt
    N = 10000
    data = [noisy_count(42, 1.0) for _ in range(N)]
    plt.hist(data, bins=100)
    data = [noisy_count(-50, 0.1) for _ in range(N)]
    plt.hist(data, bins=100)
    plt.show()
