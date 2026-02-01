/*
 * View model for OctoPrint-FilamentReloaded
 * Author: Nick Mitchko
 * License: AGPLv3
 * 
 * Enhanced with version compatibility and robust status updates
 */
$(function() {
    function FilamentReloadViewModel(parameters) {
        var self = this;
        
        self.loginState = parameters[0];
        self.settings = parameters[1];
        
        self.sensorEnabled = ko.observable(false);
        self.filamentStatus = ko.observable(-1);
        self.isPolling = false;
        self.pollInterval = null;
        
        // CSS classes for the icon based on status
        self.iconClass = ko.pureComputed(function() {
            var status = self.filamentStatus();
            if (status === -1) {
                return "icon-disabled";
            } else if (status === 0) {
                return "icon-no-filament";
            } else {
                return "icon-filament-ok";
            }
        });
        
        // Tooltip text based on status
        self.tooltipText = ko.pureComputed(function() {
            var status = self.filamentStatus();
            if (status === -1) {
                return "Filament Sensor Disabled";
            } else if (status === 0) {
                return "No Filament Detected";
            } else {
                return "Filament Detected";
            }
        });
        
        // Handle plugin messages from backend (OctoPrint 1.9+)
        self.onDataUpdaterPluginMessage = function(plugin, data) {
            if (plugin !== "filamentreload") {
                return;
            }
            
            // Handle status updates from backend
            if (data.type === "status_update" && data.hasOwnProperty("status")) {
                var newStatus = parseInt(data.status);
                if (self.filamentStatus() !== newStatus) {
                    console.log("Filament status updated via plugin message:", newStatus);
                    self.filamentStatus(newStatus);
                }
            }
        };
        
        // Request status from API endpoint
        self.requestStatus = function() {
            $.ajax({
                url: API_BASEURL + "plugin/filamentreload/status",
                type: "GET",
                dataType: "json",
                success: function(response) {
                    if (response.hasOwnProperty("status")) {
                        var newStatus = parseInt(response.status);
                        if (self.filamentStatus() !== newStatus) {
                            console.log("Filament status updated via API:", newStatus);
                            self.filamentStatus(newStatus);
                        }
                    }
                },
                error: function(xhr, status, error) {
                    console.error("Failed to get filament sensor status:", error);
                }
            });
        };
        
        // Start polling at configured frequency
        self.startPolling = function() {
            if (self.isPolling) {
                return;
            }
            
            var checkFreq = 5; // Default 5 seconds
            try {
                if (self.settings.settings.plugins.filamentreload) {
                    checkFreq = self.settings.settings.plugins.filamentreload.check_freq() || 5;
                }
            } catch (e) {
                console.log("Could not read check_freq from settings, using default");
            }
            
            console.log("Starting filament sensor polling every " + checkFreq + " seconds");
            self.isPolling = true;
            
            // Poll at configured frequency
            self.pollInterval = setInterval(function() {
                self.requestStatus();
            }, checkFreq * 1000);
        };
        
        // Stop polling
        self.stopPolling = function() {
            if (self.pollInterval) {
                clearInterval(self.pollInterval);
                self.pollInterval = null;
            }
            self.isPolling = false;
        };
        
        // Called when view model binds to page
        self.onBeforeBinding = function() {
            console.log("FilamentReload: Initializing");
            self.requestStatus();
        };
        
        // Called when startup is complete
        self.onStartupComplete = function() {
            console.log("FilamentReload: Startup complete, starting polling");
            self.requestStatus();
            self.startPolling();
        };
        
        // Called when settings are shown
        self.onSettingsShown = function() {
            self.requestStatus();
        };
        
        // Called when settings are saved
        self.onSettingsHidden = function() {
            // Restart polling with new frequency
            self.stopPolling();
            self.startPolling();
        };
        
        // Clean up on disconnect
        self.onUserLoggedOut = function() {
            self.stopPolling();
        };
    }
    
    // Register the view model
    OCTOPRINT_VIEWMODELS.push({
        construct: FilamentReloadViewModel,
        dependencies: ["loginStateViewModel", "settingsViewModel"],
        elements: ["#navbar_plugin_filamentreload"]
    });
});