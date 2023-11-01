#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import time
import atexit
from signal import SIGTERM


class Daemon(object):
    """
    A generic daemon class.
    Usage: subclass the Daemon class and override the run() method
    """
    def __init__(self, pidfile, debug_mode=False):
        if (hasattr(os, "devnull")):
            DEVNULL = os.devnull
        else:
            DEVNULL = "/dev/null"

        self.stdin = DEVNULL
        self.stdout = DEVNULL
        self.stderr = DEVNULL
        self.pidfile = pidfile
        self.debug_mode = debug_mode

    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                print(f"daemon > exit first parent")
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                print(f"daemon > exit second parent")
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        #si = file(self.stdin, 'r')
        #so = file(self.stdout, 'a+')
        #se = file(self.stderr, 'a+', 0)
        si = open(self.stdin, 'r')
        so = open(self.stdout, 'a+')
        se = open(self.stderr, 'a+')
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        print(f"daemon pid is {pid}")
        #file(self.pidfile, 'w+').write("%s\n" % pid)
        open(self.pidfile, 'w+').write("%s\n" % pid)

    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            #pf = file(self.pidfile, 'r')
            pf = open(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            print(message)
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)

        # Start the daemon
        if not self.debug_mode:
            self.daemonize()
        self.run()

    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        try:
            #pf = file(self.pidfile, 'r')
            pf = open(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return  # not an error in a restart

        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print((str(err)))
                sys.exit(1)

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()

    def status(self):
        try:
            #pf = file(self.pidfile, 'r')
            pf = open(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        try:
            # won't kill the process. kill is a bad named system call
            os.kill(pid, 0)
            sys.stdout.write("the process with the PID %d is running\n" % pid)
        except OSError:
            sys.stdout.write("there is not a process with the PID specified in %s\n" % self.pidfile)
        except TypeError:
            sys.stdout.write("pidfile %s does not exist\n" % self.pidfile)

        sys.exit(0)

    def run(self):
        """
        You should override this method when you subclass Daemon. It will be called after the process has been
        daemonized by start() or restart().
        """
