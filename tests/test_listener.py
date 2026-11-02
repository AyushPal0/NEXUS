"""Exercise the actual UI callback without Qt, microphone, or model imports."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

class ListenerTests(unittest.TestCase):
    def test_repeated_click_does_not_start_second_worker(self):
        tree = ast.parse(Path("frontend/ui/nexus_window.py").read_text(encoding="utf-8"))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef))
        method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "start_listening")
        worker = Mock()
        worker.is_alive.return_value = True
        threading = SimpleNamespace(Thread=Mock(return_value=worker))
        context = {"threading": threading, "start_karna": Mock(), "start_nexus": Mock()}
        exec(compile(ast.Module(body=[method], type_ignores=[]), "listener", "exec"), context)
        window = SimpleNamespace(_assistant_thread=None, status=Mock())
        callback = context["start_listening"]
        callback(window)
        callback(window)
        threading.Thread.assert_called_once()
        worker.start.assert_called_once()
        worker.is_alive.return_value = False
        callback(window)
        self.assertEqual(threading.Thread.call_count, 2)
