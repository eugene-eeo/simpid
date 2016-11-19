#!/usr/bin/env python
"""
Usage:
    simpid --p=<p> --i=<i> --d=<d> [--k=<k>] [--dt=<dt>] [--T=<T>] [--cmap=<cmap>] <filename>
    simpid --help

Options:
    (-h | --help)   displays this page
    --p=<p>         comma-separated k_p values
    --i=<i>         comma-separated k_i values
    --d=<d>         comma-separated k_d values
    --dt=<dt>       the timestep/sampling interval [default: 1]
    --k=<k>         comma-separated targets [default: 1]
    --T=<T>         max simulation time [default: 100]
    --cmap=<cmap>   colormap [default: Set2]
"""

from itertools import product, chain
import docopt
import matplotlib.pyplot as plt
from numpy import linspace


class PID:
    def __init__(self, kp, ki, kd, dt):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.dt = dt
        self.error_sum = 0
        self.prev_error = 0

    def update(self, target, value):
        error = target - value
        trend = (error - self.prev_error) / self.dt
        self.error_sum += error * self.dt
        self.prev_error = error
        return (
            (self.kp * error) +
            (self.ki * self.error_sum) +
            (self.kd * trend)
            )


def correct(stream, pid):
    v = 0
    for target in stream:
        yield v
        v += pid.update(target, v)


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


def parse_csv_floats(line):
    return [float(k.strip()) for k in line.split(',')]


def n_target_ranges(max_time, targets):
    for target, (a,b) in target_partition(max_time, targets):
        for _ in range(a, b):
            yield target


def main(args):
    kp_values = parse_csv_floats(args['--p'])
    ki_values = parse_csv_floats(args['--i'])
    kd_values = parse_csv_floats(args['--d'])
    colormap = plt.get_cmap(args['--cmap'])
    targets = parse_csv_floats(args['--k'])
    T = float(args['--T'])
    dt = float(args['--dt'])

    x = int(T/dt) + 1
    X = [i*dt for i in range(x)]

    fig, ax = plt.subplots()
    ax.plot(X, list(n_target_ranges(x, targets)), color='black')

    num_plots = 0
    for kp, ki, kd in product(kp_values, ki_values, kd_values):
        num_plots += 1
        pid = PID(kp, ki, kd, dt)
        ax.plot(
            X,
            list(correct(n_target_ranges(x, targets), pid)),
            label='$ {0}, {1}, {2} $'.format(kp, ki, kd),
            )

    for f, line in zip(linspace(0, 1, num_plots), ax.lines[1:]):
        color = colormap(f)
        line.set_color(color)

    ax.set_xlabel('t')
    legend = ax.legend(**legend_opts)
    plt.xlim([0, T])
    plt.grid(True)
    plt.savefig(args['<filename>'], bbox_extra_artists=(legend,), bbox_inches='tight')


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    main(args)
