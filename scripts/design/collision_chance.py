import math

SET = {
    'pink': {
        'N': 9,
        'k': 2_000
    },
    'lemon': {
        'N': 10,
        'k': 2_000 * 3
    },
    'proj': {
        'N': 11,
        'k': 20_000
    },
    'role': {
        'N': 12,
        'k': 20_000 * 20
    },
    'pit': {
        'N': 13,
        'k': 20_000 * 20 * 5
    },
    'mango': {
        'N': 14,
        'k': 20_000 * 20 * 5 * 10
    }
}

for model, parm in SET.items():
    N = 67**parm['N']
    k = parm['k']
    print(model, 1 - math.exp(-0.5 * k * (k - 1) / N))
