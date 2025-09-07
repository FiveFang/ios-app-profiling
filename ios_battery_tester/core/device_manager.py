"""
Device Manager for iOS devices.
Handles device discovery, connection, and basic operations.
"""

import logging
import subprocess
import time
from typing import Dict, List, Optional, Any
import pymobiledevice3
from pymobiledevice3.services.device_arbitration import DeviceArbitrationService
from pymobiledevice3.services.lockdown import LockdownClient
from pymobiledevice3.services.installation_proxy import InstallationProxyService
from pymobiledevice3.usbmux import select_devices_by_connection_type


logger = logging.getLogger(__name__)


class DeviceManager:
    """Manages iOS device connections and operations."""
    
    def __init__(self):
        self.devices = {}
        self.lockdown_clients = {}
        
    def discover_devices(self) -> List[Dict[str, Any]]:
        """
        Discover all connected iOS devices.
        
        Returns:
            List of device information dictionaries
        """
        try:
            devices = select_devices_by_connection_type('USB')
            device_list = []
            
            for device in devices:
                try:
                    lockdown = LockdownClient(device)
                    device_info = {
                        'udid': device.udid,
                        'name': lockdown.get_value('', 'DeviceName'),
                        'version': lockdown.get_value('', 'ProductVersion'),
                        'model': lockdown.get_value('', 'ProductType'),
                        'battery_level': self._get_battery_level(lockdown),
                        'connection_type': 'USB'
                    }
                    device_list.append(device_info)
                    self.devices[device.udid] = device
                    self.lockdown_clients[device.udid] = lockdown
                    logger.info(f"Discovered device: {device_info['name']} ({device.udid})")
                except Exception as e:
                    logger.error(f"Failed to get info for device {device.udid}: {e}")
                    
            return device_list
            
        except Exception as e:
            logger.error(f"Failed to discover devices: {e}")
            return []
    
    def get_device_info(self, udid: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific device.
        
        Args:
            udid: Device UDID
            
        Returns:
            Device information dictionary or None if not found
        """
        if udid not in self.lockdown_clients:
            logger.error(f"Device {udid} not found")
            return None
            
        try:
            lockdown = self.lockdown_clients[udid]
            return {
                'udid': udid,
                'name': lockdown.get_value('', 'DeviceName'),
                'version': lockdown.get_value('', 'ProductVersion'),
                'model': lockdown.get_value('', 'ProductType'),
                'build_version': lockdown.get_value('', 'BuildVersion'),
                'serial_number': lockdown.get_value('', 'SerialNumber'),
                'battery_level': self._get_battery_level(lockdown),
                'wifi_address': lockdown.get_value('', 'WiFiAddress'),
                'bluetooth_address': lockdown.get_value('', 'BluetoothAddress'),
            }
        except Exception as e:
            logger.error(f"Failed to get device info for {udid}: {e}")
            return None
    
    def get_installed_apps(self, udid: str) -> List[Dict[str, Any]]:
        """
        Get list of installed applications on the device.
        
        Args:
            udid: Device UDID
            
        Returns:
            List of application information dictionaries
        """
        if udid not in self.devices:
            logger.error(f"Device {udid} not found")
            return []
            
        try:
            lockdown = self.lockdown_clients[udid]
            
            with InstallationProxyService(lockdown=lockdown) as installation_proxy:
                apps = installation_proxy.get_apps()
                app_list = []
                
                for bundle_id, app_info in apps.items():
                    if app_info.get('ApplicationType') == 'User':
                        app_list.append({
                            'bundle_id': bundle_id,
                            'name': app_info.get('CFBundleDisplayName', bundle_id),
                            'version': app_info.get('CFBundleShortVersionString', ''),
                            'identifier': app_info.get('CFBundleIdentifier', bundle_id),
                            'install_date': app_info.get('com.apple.iTunesStore.downloadInfo', {}).get('purchaseDate'),
                        })
                
                return sorted(app_list, key=lambda x: x['name'])
                
        except Exception as e:
            logger.error(f"Failed to get installed apps for {udid}: {e}")
            return []
    
    def launch_app(self, udid: str, bundle_id: str) -> bool:
        """
        Launch an application on the device.
        
        Args:
            udid: Device UDID
            bundle_id: Application bundle identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Use iOS Debug Bridge (idb) or similar tool for app launching
            cmd = ['idevicedebug', '-u', udid, 'run', bundle_id]
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info(f"Launched app {bundle_id} on device {udid}")
            return True
        except Exception as e:
            logger.error(f"Failed to launch app {bundle_id} on {udid}: {e}")
            return False
    
    def kill_app(self, udid: str, bundle_id: str) -> bool:
        """
        Kill an application on the device.
        
        Args:
            udid: Device UDID
            bundle_id: Application bundle identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # This would typically use private APIs or developer tools
            cmd = ['idevicedebug', '-u', udid, 'kill', bundle_id]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info(f"Killed app {bundle_id} on device {udid}")
            return True
        except Exception as e:
            logger.error(f"Failed to kill app {bundle_id} on {udid}: {e}")
            return False
    
    def _get_battery_level(self, lockdown: LockdownClient) -> Optional[int]:
        """Get battery level from device."""
        try:
            # Try to get battery information
            battery_info = lockdown.get_value('com.apple.mobile.battery')
            if battery_info and 'BatteryCurrentCapacity' in battery_info:
                return battery_info['BatteryCurrentCapacity']
        except Exception:
            pass
        return None
    
    def is_device_connected(self, udid: str) -> bool:
        """Check if device is still connected."""
        return udid in self.devices and udid in self.lockdown_clients
    
    def disconnect_device(self, udid: str) -> None:
        """Disconnect from a specific device."""
        if udid in self.lockdown_clients:
            del self.lockdown_clients[udid]
        if udid in self.devices:
            del self.devices[udid]
        logger.info(f"Disconnected from device {udid}")
    
    def disconnect_all(self) -> None:
        """Disconnect from all devices."""
        self.lockdown_clients.clear()
        self.devices.clear()
        logger.info("Disconnected from all devices")
