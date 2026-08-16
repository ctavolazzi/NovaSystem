"""Concurrency primitives for workspace writes.

Several writers touch the same document: the agent you are talking to, a shell
hook firing on every tool call, a second terminal, a cron job. Without a lock
they race and the last writer silently wins, which is the Lost Update Anomaly
and it eats work.

Three primitives:

    workspace_lock(root)   advisory lock at the workspace root
    atomic_write(path, s)  temp file + fsync + os.replace
    write(path, s, root)   both together, the one-call form

The lock file lives at ``<root>/.coworking.lock``. Every process that mutates
workspace content must acquire it first.

``portalocker`` is an optional dependency. Without it this module degrades to a
directory-based mutex rather than failing: losing cross-platform robustness is
survivable, losing the ability to write anything is not.
"""

from __future__ import annotations

import errno
import logging
import os
import signal
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional, Union

LOG = logging.getLogger(__name__)

LOCK_FILENAME = ".coworking.lock"
FALLBACK_LOCK_DIRNAME = ".coworking.lock.d"

DEFAULT_TIMEOUT_S = 8.0
DEFAULT_CHECK_INTERVAL_S = 0.25

try:  # pragma: no cover - presence depends on the install
    import portalocker
except ImportError:  # pragma: no cover
    portalocker = None


class LockTimeout(RuntimeError):
    """Another writer held the workspace lock for longer than the timeout."""


class DelayedKeyboardInterrupt:
    """Defer SIGINT until the critical section completes.

    Ctrl+C landing between "temp file written" and "os.replace" is how a
    half-written document happens. Trap the signal, finish the swap, then
    re-raise.
    """

    def __enter__(self):
        self.signal_received = False
        try:
            self.old_handler = signal.signal(signal.SIGINT, self._handler)
            self._installed = True
        except ValueError:
            # Not on the main thread; nothing to defer.
            self.old_handler = None
            self._installed = False
        return self

    def _handler(self, sig, frame):
        self.signal_received = (sig, frame)
        LOG.debug("SIGINT deferred until the critical section ends")

    def __exit__(self, exc_type, exc, tb):
        if self._installed:
            signal.signal(signal.SIGINT, self.old_handler)
        if self.signal_received and self.old_handler not in (
                None, signal.SIG_IGN, signal.SIG_DFL):
            self.old_handler(*self.signal_received)
        elif self.signal_received and self.old_handler is signal.SIG_DFL:
            raise KeyboardInterrupt
        return False


@contextmanager
def _fallback_lock(root: Path, timeout: float,
                   check_interval: float) -> Iterator[None]:
    """Directory-mutex lock for installs without portalocker.

    ``mkdir`` is atomic on every filesystem worth supporting. A lock left by a
    process that died is cleared once it is older than the timeout, so one
    crash cannot wedge the workspace permanently.
    """
    lock_dir = root / FALLBACK_LOCK_DIRNAME
    deadline = time.monotonic() + timeout
    while True:
        try:
            lock_dir.mkdir()
            break
        except FileExistsError:
            try:
                age = time.time() - lock_dir.stat().st_mtime
                if age > timeout:
                    lock_dir.rmdir()
                    continue
            except OSError:
                pass
            if time.monotonic() >= deadline:
                raise LockTimeout(
                    f"workspace lock held longer than {timeout}s: {lock_dir}"
                )
            time.sleep(check_interval)
        except OSError as e:  # pragma: no cover - unusual filesystems
            if e.errno == errno.EROFS:
                yield  # read-only workspace: nothing to serialize
                return
            raise
    try:
        yield
    finally:
        try:
            lock_dir.rmdir()
        except OSError:
            pass


@contextmanager
def workspace_lock(root: Union[Path, str],
                   timeout: float = DEFAULT_TIMEOUT_S,
                   check_interval: float = DEFAULT_CHECK_INTERVAL_S
                   ) -> Iterator[None]:
    """Hold the workspace lock for the duration of the block."""
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)

    if portalocker is None:
        with DelayedKeyboardInterrupt():
            with _fallback_lock(root, timeout, check_interval):
                yield
        return

    # Letting portalocker default its flags is what actually honours `timeout`;
    # passing LOCK_EX explicitly puts it in blocking mode where timeout is
    # ignored and warns about exactly that.
    lock = portalocker.Lock(
        str(root / LOCK_FILENAME),
        mode="a",
        timeout=timeout,
        check_interval=check_interval,
        fail_when_locked=False,
    )
    with DelayedKeyboardInterrupt():
        try:
            with lock:
                yield
        except portalocker.exceptions.LockException as e:
            raise LockTimeout(
                f"workspace lock held longer than {timeout}s: {root}"
            ) from e


def atomic_write(path: Union[Path, str], content: str,
                 encoding: str = "utf-8") -> None:
    """Write `content` to `path` so readers never observe a partial file.

    Streams to a sibling temp file, fsyncs, then ``os.replace`` swaps it into
    place. ``os.replace`` is atomic on POSIX and on Windows, so a reader sees
    either the old file or the new one.

    Callers mutating shared workspace files must hold ``workspace_lock``, or
    just use ``write()`` which does both.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp_fd, tmp_path = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent),
    )
    try:
        with os.fdopen(tmp_fd, "w", encoding=encoding) as fh:
            fh.write(content)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def write(path: Union[Path, str], content: str,
          root: Optional[Union[Path, str]] = None,
          encoding: str = "utf-8") -> None:
    """Lock the workspace and atomically write one file.

    The canonical single-shot write. `root` defaults to the file's parent,
    which is right for standalone files and wrong for a shared workspace, so
    pass the workspace root whenever there is one.
    """
    path = Path(path)
    with workspace_lock(root if root is not None else path.parent):
        atomic_write(path, content, encoding)
