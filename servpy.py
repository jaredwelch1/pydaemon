import sys
import os
import atexit

class Daemon:
    def __init__(self):
        self.pidfile = '/tmp/' + __file__.replace('.py', '') + '_pid'

    def daemonize(self):
        '''Use double fork to detach service'''
        try:
            pid = os.fork()
            # exit parent
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            sys.stderr.write(f'Fork failed: {e}')
            sys.exit(1)

        os.chdir('/')
        os.setsid()
        os.umask(0)

        # second fork. This is for preventing tty access by process
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            sys.stderr.write(f"Fork failed: {e}")
            sys.exit(1)

        # redirect stdin, stdout, and stderr
        sys.stdout.flush()
        sys.stderr.flush()

        si = open(os.devnull,  'r')
        so = open(f'/tmp/stdout_{self.pidfile.replace("/", "")}', 'w+')
        se = so

        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        atexit.register(self.delete_pid)
        pid = os.getpid()
        with open(self.pidfile, 'w+') as pidfp:
            pidfp.write(f'{pid}\n')

    def start(self):
        try:
            with open(self.pidfile, 'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None
        if pid:
            sys.stderr.write(f'pid file {self.pidfile} already exists')
            sys.exit(1)
        self.daemonize()
        self.run()

    def stop(self):
        try:
            with open(self.pidfile, 'r') as pf:
                pid = int(pf.read())
        except IOError:
            pid = None
        if not pid:
            sys.stderr.write('pidfile does not exist. Daemon not running.')
            return

        try:
            os.kill(pid, signal.SIGTERM)
        except OSError as e:
            if 'No such process' in str(e):
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                raise e

    def restart(self):
        self.stop()
        self.start()

    def delete_pid(self):
        os.remove(self.pidfile)

    def run(self):
        raise NotImplementedError



if __name__ == '__main__':
    Daemon().start()
