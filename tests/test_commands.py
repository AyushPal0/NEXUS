import importlib
import sys
import unittest
from unittest.mock import Mock, patch
from types import ModuleType

class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.plan = Mock(return_value=[])
        self.ask = Mock(return_value="unknown")
        self.actions = {name: Mock() for name in (
            "open_chrome", "open_youtube", "create_folder", "take_screenshot", "take_photo",
            "analyze_screen", "remember", "recall")}
        modules = {}
        bindings = {
            "backend.brain.ai_brain": {"ask_ai": self.ask},
            "backend.brain.task_agent": {"plan_tasks": self.plan},
            "backend.automation.system_control": {k: self.actions[k] for k in ("open_chrome", "open_youtube")},
            "backend.automation.file_manager": {"create_folder": self.actions["create_folder"]},
            "backend.automation.screenshot": {"take_screenshot": self.actions["take_screenshot"]},
            "backend.automation.camera": {"take_photo": self.actions["take_photo"]},
            "backend.brain.screen_vision": {"analyze_screen": self.actions["analyze_screen"]},
            "backend.utils.memory_manager": {k: self.actions[k] for k in ("remember", "recall")},
        }
        for name, attrs in bindings.items():
            modules[name] = ModuleType(name)
            modules[name].__dict__.update(attrs)
        self.patcher = patch.dict(sys.modules, modules)
        self.patcher.start()
        sys.modules.pop("backend.brain.command_handler", None)
        self.handle = importlib.import_module("backend.brain.command_handler").handle_command
        self.speak = Mock()

    def tearDown(self):
        sys.modules.pop("backend.brain.command_handler", None)
        self.patcher.stop()

    def test_stop_does_not_call_planner(self):
        self.assertFalse(self.handle("stop", self.speak))
        self.plan.assert_not_called()

    def test_screen_request_bypasses_memory(self):
        self.handle("what is on my screen", self.speak)
        self.actions["analyze_screen"].assert_called_once()
        self.actions["recall"].assert_not_called()

    def test_invalid_plan_reaches_fallback(self):
        self.plan.return_value = ["Here are the steps:", "do_not_open_chrome"]
        self.ask.return_value = "open_youtube"
        self.handle("play a video", self.speak)
        self.actions["open_chrome"].assert_not_called()
        self.actions["open_youtube"].assert_called_once()

    def test_numbered_plan_and_folder_name(self):
        self.plan.return_value = ["1. create_folder"]
        self.handle("create folder called My Project", self.speak)
        self.actions["create_folder"].assert_called_once_with("My Project")

    def test_folder_path_rejected(self):
        self.handle("create folder called ../outside", self.speak)
        self.plan.assert_not_called()
        self.actions["create_folder"].assert_not_called()

    def test_empty_command_does_not_call_planner(self):
        self.handle("  ", self.speak)
        self.plan.assert_not_called()

    def test_planned_stop(self):
        self.plan.return_value = ["stop"]
        self.assertFalse(self.handle("please finish", self.speak))
