#!/usr/bin/env python
'''This is a demo on how to use Gnuplot for potential fields.  We've
intentionally avoided "giving it all away."
'''

from __future__ import division
from itertools import cycle
from trackenemyfieldgen import TrackEnemyFieldGen
from bzrc import BZRC
try:
    from numpy import linspace
except ImportError:
    # This is stolen from numpy.  If numpy is installed, you don't
    # need this:
    def linspace(start, stop, num=50, endpoint=True, retstep=False):
        """Return evenly spaced numbers.

        Return num evenly spaced samples from start to stop.  If
        endpoint is True, the last sample is stop. If retstep is
        True then return the step value used.
        """
        num = int(num)
        if num <= 0:
            return []
        if endpoint:
            if num == 1:
                return [float(start)]
            step = (stop-start)/float((num-1))
            y = [x * step + start for x in xrange(0, num - 1)]
            y.append(stop)
        else:
            step = (stop-start)/float(num)
            y = [x * step + start for x in xrange(0, num)]
        if retstep:
            return y, step
        else:
            return y


########################################################################
# Constants

# Output file:
FILENAME = 'fields.gpi'
# Size of the world (one of the "constants" in bzflag):
WORLDSIZE = 800
# How many samples to take along each dimension:
SAMPLES = 25
# Change spacing by changing the relative length of the vectors.  It looks
# like scaling by 0.75 is pretty good, but this is adjustable:
VEC_LEN = 0.75 * WORLDSIZE / SAMPLES
# Animation parameters:
ANIMATION_MIN = 0
ANIMATION_MAX = 500
ANIMATION_FRAMES = 50

#BZRC
bzrc = BZRC('localhost', 50000)

track_enemy_field_gen = TrackEnemyFieldGen(bzrc)

def gnuplot_header(minimum, maximum, sigma_x, sigma_y, rho, x, y):

    '''Return a string that has all of the gnuplot sets and unsets.'''
    s = ''
    s += 'set xrange [%s: %s]\n' % (minimum, maximum)
    s += 'set yrange [%s: %s]\n' % (minimum, maximum)
    s += 'set pm3d\n'
    s += 'set view map\n'
    s += 'unset key\n'
    s += 'set size square\n'
    # Add a pretty title (optional):
    s += 'set palette model RGB functions 1-gray, 1-gray, 1-gray\n'
    s += 'set isosamples 100\n'
    s += 'sigma_x = ' + str(sigma_x) + '\n'
    s += 'sigma_y = ' + str(sigma_y) + '\n'
    s += 'rho = ' + str(rho) + '\n'
    s += 'splot 1.0/(2.0 * pi * sigma_x * sigma_y * sqrt(1 - rho**2) ) \
        * exp(-1.0/2.0 * ((x-'+ str(x) +')**2 / sigma_x**2 + (y-'+ str(y) +')**2 / sigma_y**2 \
        - 2.0*rho*(x-'+ str(x) +')*(y-'+ str(y) +')/(sigma_x*sigma_y) ) ) with pm3d\n'
    return s




########################################################################
# Plot the potential fields to a file

outfile = open(FILENAME, 'w')
print >>outfile, gnuplot_header(-WORLDSIZE / 2, WORLDSIZE / 2, 70, 100, 0, 300, 100)



########################################################################
# Animate a changing field, if the Python Gnuplot library is present

try:
    from Gnuplot import GnuplotProcess
except ImportError:
    print "Sorry.  You don't have the Gnuplot module installed."
    import sys
    sys.exit(-1)

forward_list = list(linspace(ANIMATION_MIN, ANIMATION_MAX, ANIMATION_FRAMES/2))
backward_list = list(linspace(ANIMATION_MAX, ANIMATION_MIN, ANIMATION_FRAMES/2))
anim_points = forward_list + backward_list

sigma_x, sigma_y, x, y = track_enemy_field_gen.get_sigma_t()
gp = GnuplotProcess(persist=False)
gp.write(gnuplot_header(-WORLDSIZE / 2, WORLDSIZE / 2, sigma_x, sigma_y, 0, x, y))

for scale in cycle(anim_points):
    sigma_x, sigma_y, x, y = track_enemy_field_gen.get_sigma_t()
    gp.write(gnuplot_header(-WORLDSIZE / 2, WORLDSIZE / 2, sigma_x, sigma_y, 0, x, y))
  
