from fabric import Connection


class FabException(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class RemoteConnect:
    def __init__(self) -> None:
        self.conn = None

    def connect(self, host, user) -> None:
        self.conn = Connection(host=host, user=user)

    def remote_run(self, cmd):
        r = self.conn.run(cmd, hide=True, warn=True, encoding="utf-8")
        result, err = r.stdout.strip(), r.stderr.strip()
        if err:
            raise FabException(err)
        return result

    def local_run(self, cmd):
        with Connection("localhost") as conn:
            r = conn.local(cmd, hide=True, warn=True, encoding="utf-8")
            result, err = r.stdout.strip(), r.stderr.strip()
            if err:
                raise FabException(err)
            return result

