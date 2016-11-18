#!/usr/bin/env python
"""
Usage:
    simpid --p=<p> --i=<i> --d=<d> [--k=<k>] [--dt=<dt>] [--T=<T>] <filename>
    simpid --help

Options:
    (-h | --help)   displays this page
    --p=<p>         comma-separated k_p values
    --i=<i>         comma-separated k_i values
    --d=<d>         comma-separated k_d values
    --dt=<dt>       the timestep/sampling interval [default: 1]
    --k=<k>         comma-separated targets [default: 1]
    --T=<T>         max simulation time [default: 100]
"""

from __future__ import division
from itertools import product, chain
import docopt
import matplotlib.pyplot as plt
from numpy import linspace


class PID:
    def __init__(self, k_p, k_i, k_d, dt):
        self.k_p = k_p
        self.k_i = k_i
        self.k_d = k_d
        self.dt = dt
        self.error_sum = 0
        self.prev_error = 0

    def update(self, target, value):
        error = target - value
        self.error_sum += error * self.dt
        predicted_error = (error - self.prev_error) / self.dt
        self.prev_error = error
        return (
            (self.k_p * error) +
            (self.k_i * self.error_sum) +
            (self.k_d * predicted_error)
            )


def correct(desired, pid, T):
    v = 0
    for _ in range(T):
        yield v
        v = pid.update(desired, v)


legend_opts = {
    'columnspacing':  1.0,
    'labelspacing':   0.0,
    'handletextpad':  0.25,
    'handlelength':   1.5,
    'bbox_to_anchor': (1, 0.5),
    'loc':            'center left',
}


def target_partition(max_time, targets):
    n = len(targets)
    step = max_time // n
    start, end = 0, step
    for i, t in enumerate(targets):
        if i == n - 1:
            end += max_time - n * step
        yield t, (start, end)
        start = end
        end += step


def main(args, colormap=plt.cm.viridis):
    kp_values = [float(k) for k in args['--p'].split(',')]
    ki_values = [float(k) for k in args['--i'].split(',')]
    kd_values = [float(k) for k in args['--d'].split(',')]
    T = float(args['--T'])
    dt = float(args['--dt'])
    targets = [float(k) for k in args['--k'].split(',')]

    num_plots = 0
    x = int(T/dt) + 1
    X = [i*dt for i in range(x)]
    ranges = list(target_partition(x, targets))

    fig, ax = plt.subplots()
    Y = chain.from_iterable((t for _ in range(a, b)) for (t, (a, b)) in ranges)
    ax.plot(X, list(Y), '-', color='black')

    for k_p, k_i, k_d in product(kp_values, ki_values, kd_values):
        pid = PID(k_p, k_i, k_d, dt)
        V = chain.from_iterable(
                correct(t, pid, b - a) for (t,(a, b)) in ranges
            )
        ax.plot(X, list(V), label='$ {0}, {1}, {2} $'.format(k_p, k_i, k_d))
        num_plots += 1

    colors = [colormap(i) for i in linspace(0, 1, num_plots)]
    for i, line in enumerate(ax.lines):
        if i == 0:
            continue
        line.set_color(colors[i-1])

    ax.set_xlabel('t')
    legend = ax.legend(**legend_opts)
    plt.xlim([0, T])
    plt.grid(True)
    plt.savefig(args['<filename>'], bbox_extra_artists=(legend,), bbox_inches='tight')


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    main(args)
