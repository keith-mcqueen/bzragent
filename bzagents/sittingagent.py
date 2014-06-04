#!/usr/bin/python -tt

import sys
import time

from bzrc import BZRC
from pfagent import Agent


class SittingDuck(Agent):
    """Class handles all command and control logic for a teams tanks."""
    def __init__(self, bzrc):
        super(SittingDuck, self).__init__(bzrc)

    def tick(self, time_diff):
        # do nothing
        pass


def main():
    # Process CLI arguments.
    try:
        execname, host, port = sys.argv
    except ValueError:
        execname = sys.argv[0]
        print >> sys.stderr, '%s: incorrect number of arguments' % execname
        print >> sys.stderr, 'usage: %s hostname port' % sys.argv[0]
        sys.exit(-1)

    # Connect.
    #bzrc = BZRC(host, int(port), debug=True)
    bzrc = BZRC(host, int(port))

    agent = SittingDuck(bzrc)

    prev_time = time.time()

    # Run the agent
    try:
        while True:
            time_diff = time.time() - prev_time
            agent.tick(time_diff)
    except KeyboardInterrupt:
        print "Exiting due to keyboard interrupt."
        bzrc.close()


if __name__ == '__main__':
    main()

# vim: et sw=4 sts=4
