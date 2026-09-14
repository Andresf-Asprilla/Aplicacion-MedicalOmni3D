import sys
import os
import signal
import subprocess

IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    import ctypes
    from ctypes import wintypes

    JobObjectExtendedLimitInformation = 9
    JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
    PROCESS_ALL_ACCESS = 0x1F0FFF

    class IO_COUNTERS(ctypes.Structure):
        _fields_ = [("ReadOperationCount", ctypes.c_ulonglong),
                    ("WriteOperationCount", ctypes.c_ulonglong),
                    ("OtherOperationCount", ctypes.c_ulonglong),
                    ("ReadTransferCount", ctypes.c_ulonglong),
                    ("WriteTransferCount", ctypes.c_ulonglong),
                    ("OtherTransferCount", ctypes.c_ulonglong)]

    class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64),
                    ("PerJobUserTimeLimit", ctypes.c_int64),
                    ("LimitFlags", wintypes.DWORD),
                    ("MinimumWorkingSetSize", ctypes.c_size_t),
                    ("MaximumWorkingSetSize", ctypes.c_size_t),
                    ("ActiveProcessLimit", wintypes.DWORD),
                    ("Affinity", ctypes.c_size_t),
                    ("PriorityClass", wintypes.DWORD),
                    ("SchedulingClass", wintypes.DWORD)]

    class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
                    ("IoInfo", IO_COUNTERS),
                    ("ProcessMemoryLimit", ctypes.c_size_t),
                    ("JobMemoryLimit", ctypes.c_size_t),
                    ("PeakProcessMemoryUsed", ctypes.c_size_t),
                    ("PeakJobMemoryUsed", ctypes.c_size_t)]

    class _JobWindows:
        def __init__(self):
            self.handle = ctypes.windll.kernel32.CreateJobObjectW(None, None)
            if not self.handle:
                raise ctypes.WinError()
            info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
            info.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
            if not ctypes.windll.kernel32.SetInformationJobObject(
                self.handle, JobObjectExtendedLimitInformation,
                ctypes.byref(info), ctypes.sizeof(info)
            ):
                raise ctypes.WinError()

        def asignar_pid(self, pid: int) -> bool:
            h_proc = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
            if not h_proc:
                return False
            ok = ctypes.windll.kernel32.AssignProcessToJobObject(self.handle, h_proc)
            ctypes.windll.kernel32.CloseHandle(h_proc)
            return bool(ok)

        def terminar(self, exit_code: int = 1):
            try:
                ctypes.windll.kernel32.TerminateJobObject(self.handle, exit_code)
            except Exception:
                pass

        def cerrar(self):
            try:
                ctypes.windll.kernel32.CloseHandle(self.handle)
            except Exception:
                pass


class _JobUnix:
    def __init__(self):
        self.pid = None
        self.pgid = None

    def asignar_pid(self, pid: int) -> bool:
        self.pid = pid
        try:
            pgid = os.getpgid(pid)
        except Exception:
            return False
        if pgid == pid:
            self.pgid = pgid
            return True
        return False

    def terminar(self, exit_code: int = 1):
        if self.pgid is not None and self.pgid == self.pid:
            try:
                os.killpg(self.pgid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            except Exception:
                pass

    def matar_fuerte(self):
        if self.pgid is not None and self.pgid == self.pid:
            try:
                os.killpg(self.pgid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            except Exception:
                pass

    def cerrar(self):
        pass


def crear_job():
    return _JobWindows() if IS_WINDOWS else _JobUnix()