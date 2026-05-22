from pythreader import synchronized, ShellCommand, Primitive
import re, os, os.path, traceback

def canonic_path(path):
    while path and "//" in path:
        path = path.replace("//", "/")
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    return path

class GFALClient(Primitive):

    def __init__(self, server, server_root, timeout=300, name=None):
        Primitive.__init__(self, name=name)
        self.Timeout = timeout
        self.Server = server
        self.ServerRoot = canonic_path(server_root)
        self.Servers = [server]

    def url(self, path):
        path = canonic_path(path)
        return "https://%s%s" % (self.Server, path)

    def absolute_path(self, path):
        path = canonic_path(path)
        return canonic_path(path if path.startswith(self.ServerRoot) else self.ServerRoot + "/" + path)

    LinePattern = re.compile(r"""
        (?P<mask>[drwx-]{10})\s+
        \d+\s+
        \S+\s+
        \S+\s+
        (?P<size>\d+)\s+
        \w+\s+\d+\s+[\d:]+\s+
        (?P<path>.+)$
    """, re.VERBOSE)

    def parse_scan_line(self, line, with_meta, location):
        if with_meta:
            line = line.strip()
            m = self.LinePattern.match(line)
            if not m:
                return None
            is_file = m.group("mask")[0] != 'd'
            size = int(m.group("size"))
            name = m.group("path").strip()
            path = canonic_path(location + "/" + name) if not name.startswith("/") else canonic_path(name)
            return is_file, size, path
        else:
            path = line.strip()
            is_file = "." in path.rsplit("/", 1)[-1]
            path = canonic_path(location + "/" + path) if not path.startswith("/") else canonic_path(path)
            return is_file, None, path

    def stat(self, path):
        path = self.absolute_path(path)
        command = "gfal-stat '%s'" % self.url(path)
        try:
            retcode, out, err = ShellCommand.execute(command, timeout=self.Timeout)
        except RuntimeError:
            return "timeout", None, None, None
        if retcode:
            return "failed", err or out, None, None
        size = None
        typ = None
        for line in out.split("\n"):
            line = line.strip()
            if line.startswith("Size:"):
                try:
                    size = int(line.split(None, 1)[1])
                except:
                    pass
            elif "regular file" in line:
                typ = "f"
            elif "directory" in line:
                typ = "d"
        if typ is None:
            return "failed", "type not found in gfal-stat output", None, None
        return "OK", None, typ, size

    def rmdir(self, path):
        path = self.absolute_path(path)
        command = "gfal-rm '%s'" % self.url(path)
        try:
            retcode, out, err = ShellCommand.execute(command, timeout=self.Timeout)
            if retcode == 0:
                status = "OK"
            else:
                status = "failed"
                reason = err or out
        except RuntimeError:
            status = "timeout"
            reason = f"timeout ({self.Timeout})"
        except Exception as e:
            status = "failed"
            reason = str(e)
        return status, reason

    def ls(self, location, recursive, with_meta, timeout=None):
        files = []
        dirs = []
        status = "OK"
        reason = ""
        timeout = timeout or self.Timeout

        location = self.absolute_path(location)
        url = self.url(location)
        lscommand = "gfal-ls %s '%s'" % (
            "-l" if with_meta else "",
            url
        )

        try:
            retcode, out, err = ShellCommand.execute(lscommand, timeout=timeout)
        except RuntimeError:
            status = "failed"
            reason = f"timeout ({self.Timeout})"
        else:
            if retcode:
                status = "failed"
                reason = "ls status code: %s, %s" % (retcode, err)

                stat_status, reasoon, typ, size = self.stat(location)
                if stat_status != "OK":
                    reason = "stat failed: " + (reason or "")
                else:
                    if typ == 'f':
                        status = "OK"
                        reason = ""
                        files = [(location, size)]
            else:
                lines = [x.strip() for x in out.split("\n")]
                for l in lines:
                    if not l:
                        continue
                    tup = self.parse_scan_line(l, with_meta, location)
                    if not tup:
                        status = "failed"
                        reason = "Invalid line in output: %s" % (l,)
                        break
                    is_file, size, path = tup
                    if path.endswith("/."):
                        continue
                    path = canonic_path(path)
                    if self.ServerRoot != '/':
                        assert path.startswith(self.ServerRoot + "/"), \
                            f"Parsed path {path} is expected to start with server root {self.ServerRoot}"
                        path = path[len(self.ServerRoot):]
                    if is_file:
                        files.append((path, size))
                    else:
                        dirs.append((path, size))
        return status, reason, dirs, files
