import sys
import time
import logging
import subprocess
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler, PatternMatchingEventHandler
import pytoml as toml
import platform


class SyncToRemoteNode(PatternMatchingEventHandler):
    """
    Sync changed files to a remote server
    """
    def __init__(self, local_path, remote_path, remote_server_cs, remote_server_cs_port=22, patterns=['*.py', '*.sh', '*.yaml', '*.capnp', '*.go'], ignore_patterns=None, ignore_directories=False, case_sensitive=False):
        super(SyncToRemoteNode, self).__init__(patterns=patterns, ignore_patterns=ignore_patterns, ignore_directories=ignore_directories, case_sensitive=case_sensitive)
        self._local_path = local_path
        self._remote_path = remote_path
        self._remote_server_cs = remote_server_cs
        self._remote_server_cs_port = remote_server_cs_port
        self._cmd = 'scp -P {} -rp {} {}:{}'


    def on_any_event(self, event):
        """
        Triggered when any filesystem
        """
        logging.info('Got an event of type {} on path {}'.format(event.event_type, event.src_path))
        relative_path = event.src_path.replace(self._local_path, '')
        remote_path = '{}/{}'.format(self._remote_path, relative_path)
        local_path = self.get_local_path(event.src_path)
        cmd = self._cmd.format(self._remote_server_cs_port, local_path, self._remote_server_cs, remote_path)
        logging.info("Executing command {}".format(cmd))
        ret_code = subprocess.call(cmd, shell=True)
        if ret_code:
            logging.error('failed to execute command {}'.format(cmd))


    def get_local_path(self, path):
        """
        Convert the given local path to an appropriate path to use for a scp command. If current platform is windows (running cygwin) then the
        path needed to be modified
        """
        curr_platform = platform.platform()
        if 'CYGWIN_NT' in  curr_platform or 'Windows' in curr_platform:
            path = path.replace('C:', '/cygdrive/c')
        return path


def parse_config(config_file):
    """
    Parse a toml config file containing the configurations of syncing servers and paths
    """
    with open(config_file, 'rb') as cf:
        config = toml.load(cf)

    for item, values in config.items():
        yield (item, values)



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    # path, remote_path, remote_server_cs = sys.argv[1:]
    config_file = sys.argv[1]
    observers = []
    for config_name, config_item in parse_config(config_file):
        logging.info('Creating new observer for {}'.format(config_name))
        remote_sync_handler = SyncToRemoteNode(config_item['path'], config_item['remote_path'],
                                                config_item['remote_server_cs'],
                                                config_item.get('remote_server_cs_port', 22))
        # event_handler = LoggingEventHandler()
        observer = Observer()
        observer.schedule(remote_sync_handler, config_item['path'], recursive=True)
        observer.start()
        observers.append(observer)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        for observer in observers:
            observer.stop()

    for observer in observers:
        observer.join()
