# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
from octoprint.events import Events
import RPi.GPIO as GPIO
from time import sleep
from flask import jsonify
import re

class FilamentReloadedPlugin(octoprint.plugin.StartupPlugin,
                              octoprint.plugin.EventHandlerPlugin,
                              octoprint.plugin.TemplatePlugin,
                              octoprint.plugin.SettingsPlugin,
                              octoprint.plugin.AssetPlugin,
                              octoprint.plugin.SimpleApiPlugin,
                              octoprint.plugin.BlueprintPlugin):

    def initialize(self):
        self._logger.info("Running RPi.GPIO version %s" % GPIO.VERSION)
        if GPIO.VERSION < "0.6":
            raise Exception("RPi.GPIO version 0.6.0 or greater required")
        
        # Detect OctoPrint version for compatibility
        self.octoprint_version = self._get_octoprint_version()
        self._logger.info("OctoPrint version detected: %s" % self.octoprint_version)
        
        self.pin = -1
        self.bounce = 0
        self.switch = 0
        self.mode = 0
        self.check_freq = 0
        self.sensor_status = -1
        self._setup_sensor()

    def _get_octoprint_version(self):
        """Get OctoPrint version as tuple for comparison"""
        try:
            from octoprint import __version__
            match = re.match(r'(\d+)\.(\d+)\.(\d+)', __version__)
            if match:
                return tuple(int(x) for x in match.groups())
            return (1, 0, 0)
        except:
            return (1, 0, 0)

    def on_after_startup(self):
        self._logger.info("Filament Sensor Reloaded started")
        self._setup_sensor()
        # Send initial status to frontend for newer OctoPrint versions
        if self._needs_plugin_messages():
            self._send_status_update()

    def _needs_plugin_messages(self):
        """Check if we need to use plugin messages (OctoPrint 1.9+)"""
        return self.octoprint_version >= (1, 9, 0)

    def _setup_sensor(self):
        if self.sensor_enabled():
            self._logger.info("Setting up sensor")
            self._logger.info("Filament Sensor active on GPIO Pin [%s]" % self.pin)
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=self.mode)
            self.sensor_status = self.get_status()
        else:
            self._logger.info("Pin not configured, won't work unless configured!")

    def _send_status_update(self):
        """Send current sensor status to frontend via plugin message"""
        if not self._needs_plugin_messages():
            return
            
        status = self.get_status()
        self._plugin_manager.send_plugin_message(self._identifier, dict(
            status=status,
            type="status_update"
        ))

    def get_status(self):
        """Get current sensor status"""
        if not self.sensor_enabled():
            return -1
        try:
            return 1 if GPIO.input(self.pin) == self.switch else 0
        except:
            return -1

    @octoprint.plugin.BlueprintPlugin.route("/status", methods=["GET"])
    def check_status(self):
        status = self.get_status()
        return jsonify(status=status)

    def on_event(self, event, payload):
        if event == Events.PRINT_STARTED:
            self._logger.info("Printing started: Sensor enabled: %s" % self.sensor_enabled())
            if self.sensor_enabled():
                self._logger.info("Filament Sensor active, monitoring...")
        elif event in (Events.PRINT_DONE, Events.PRINT_FAILED, Events.PRINT_CANCELLED):
            self._logger.info("Print done/failed/cancelled")

    def sensor_enabled(self):
        return self.pin != -1

    def no_filament(self):
        return GPIO.input(self.pin) != self.switch

    def sensor_check_event(self):
        """Periodic check that also sends updates to frontend if needed"""
        if self.sensor_enabled():
            new_status = self.get_status()
            
            # Send status update for newer OctoPrint versions
            if self._needs_plugin_messages() and new_status != self.sensor_status:
                self._send_status_update()
            
            self.sensor_status = new_status

            if self.no_filament():
                self._logger.info("No filament detected!")
                if self._settings.get_boolean(["pause_print"]):
                    self._logger.info("Pausing print")
                    self._printer.pause_print()
                if self._settings.get(["gcode"]) and self._settings.get(["gcode"]) != "":
                    self._logger.info("Sending GCODE: %s" % self._settings.get(["gcode"]))
                    self._printer.commands(self._settings.get(["gcode"]))

    def get_settings_defaults(self):
        return dict(
            pin=-1,
            bounce=300,
            switch=0,
            mode=GPIO.PUD_UP,
            gcode='',
            pause_print=True,
            check_freq=5
        )

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        self.pin = self._settings.get_int(["pin"])
        self.bounce = self._settings.get_int(["bounce"])
        self.switch = self._settings.get_int(["switch"])
        self.mode = self._settings.get_int(["mode"])
        self.check_freq = self._settings.get_int(["check_freq"])
        self._setup_sensor()

    def get_settings_version(self):
        return 1

    def on_settings_migrate(self, target, current=None):
        pass

    def get_template_configs(self):
        return [
            dict(type="navbar", custom_bindings=False),
            dict(type="settings", custom_bindings=False)
        ]

    def get_assets(self):
        return {
            "js": ["js/filamentreload.js"],
            "css": ["css/filamentreload.css"],
            "less": ["less/filamentreload.less"]
        }

    def get_update_information(self):
        return dict(
            filamentreload=dict(
                displayName="Filament Sensor Reloaded",
                displayVersion=self._plugin_version,

                type="github_release",
                user="nickmitchko",
                repo="Octoprint-Filament-Reloaded",
                current=self._plugin_version,

                pip="https://github.com/nickmitchko/Octoprint-Filament-Reloaded/archive/{target_version}.zip"
            )
        )


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = FilamentReloadedPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }