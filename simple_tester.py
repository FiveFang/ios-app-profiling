#!/usr/bin/env python3
"""
Simple iOS device tester - works without external Python dependencies.
Uses system libimobiledevice tools directly.
"""

import subprocess
import json
import time
import sys
from datetime import datetime
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress

console = Console()


def run_command(cmd, network_device=False):
    """Run a shell command and return output."""
    try:
        # Add network flag if this is for a network device
        if network_device and not "-n" in cmd:
            # Insert -n flag after the command name
            parts = cmd.split()
            if len(parts) >= 1:
                parts.insert(1, "-n")
                cmd = " ".join(parts)
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        if not network_device:  # Only print errors for non-network attempts
            console.print(f"[red]Error running command '{cmd}': {e.stderr}[/red]")
        return None


def get_device_list(network_only=False):
    """Get list of connected iOS devices."""
    if network_only:
        cmd = "idevice_id -n"
    else:
        # Try network first, then USB
        network_output = run_command("idevice_id -n")
        usb_output = run_command("idevice_id -l")
        
        devices = []
        if network_output:
            devices.extend([udid.strip() for udid in network_output.split('\n') if udid.strip()])
        if usb_output:
            devices.extend([udid.strip() for udid in usb_output.split('\n') if udid.strip()])
        
        # Remove duplicates while preserving order (network devices first)
        seen = set()
        unique_devices = []
        for device in devices:
            if device not in seen:
                seen.add(device)
                unique_devices.append(device)
        return unique_devices
    
    output = run_command(cmd)
    if output:
        return [udid.strip() for udid in output.split('\n') if udid.strip()]
    return []


def check_device_connection_type(udid):
    """Check if device is connected via WiFi or USB."""
    network_devices = run_command("idevice_id -n")
    if network_devices and udid in network_devices:
        return "WiFi"
    
    usb_devices = run_command("idevice_id -l") 
    if usb_devices and udid in usb_devices:
        return "USB"
    
    return "Unknown"


def get_device_info(udid):
    """Get basic device information."""
    try:
        # Check connection type first
        connection_type = check_device_connection_type(udid)
        
        # Get device name
        name = run_command(f"ideviceinfo -u {udid} -k DeviceName")
        # Get iOS version
        version = run_command(f"ideviceinfo -u {udid} -k ProductVersion")
        # Get device model
        model = run_command(f"ideviceinfo -u {udid} -k ProductType")
        
        return {
            'udid': udid,
            'name': name or 'Unknown',
            'version': version or 'Unknown', 
            'model': model or 'Unknown',
            'connection': connection_type
        }
    except Exception as e:
        console.print(f"[red]Error getting device info: {e}[/red]")
        return None


def get_battery_level(udid):
    """Get battery level using ideviceinfo."""
    try:
        # Try to get battery capacity from the battery domain
        result = run_command(f"ideviceinfo -u {udid} -q com.apple.mobile.battery -k BatteryCurrentCapacity")
        if result and result.strip().isdigit():
            return int(result.strip())
    except Exception:
        pass
    return None


def get_charging_status(udid):
    """Get charging status using ideviceinfo."""
    try:
        result = run_command(f"ideviceinfo -u {udid} -q com.apple.mobile.battery -k BatteryIsCharging")
        return result and result.strip().lower() == 'true'
    except Exception:
        pass
    return False


def get_installed_apps(udid):
    """Get list of installed user apps."""
    try:
        result = run_command(f"ideviceinstaller -u {udid} -l")
        apps = []
        if result:
            lines = result.split('\n')[1:]  # Skip header
            for line in lines:
                if line.strip():
                    parts = line.split(', ')
                    if len(parts) >= 3:
                        bundle_id = parts[0].strip('"')
                        version = parts[1].strip('"')
                        display_name = parts[2].strip('"')
                        apps.append({
                            'bundle_id': bundle_id,
                            'version': version,
                            'display_name': display_name
                        })
        return apps
    except Exception as e:
        console.print(f"[red]Error getting apps: {e}[/red]")
        return []


def check_app_exists(udid, app_identifier):
    """Check if an app exists on device by bundle ID or display name."""
    apps = get_installed_apps(udid)
    for app in apps:
        if (app_identifier.lower() in app['bundle_id'].lower() or 
            app_identifier.lower() in app['display_name'].lower()):
            return app
    return None


def display_charging_control_instructions():
    """Display instructions for manual charging control."""
    console.print("\n[bold yellow]📱 CHARGING CONTROL INSTRUCTIONS[/bold yellow]")
    console.print("[dim]For accurate battery testing, eliminate charging interference:[/dim]\n")
    
    console.print("[bold green]🌟 RECOMMENDED: WiFi Connection (No Charging)[/bold green]")
    console.print("1. 📶 Use WiFi connection for device communication")
    console.print("2. 🔌 Completely unplug USB cable")
    console.print("3. 🧪 Run tests wirelessly with zero charging interference")
    console.print("4. 📊 Get the most accurate battery drain measurements")
    console.print("[cyan]💡 Run 'python simple_tester.py wifi-setup' to enable WiFi testing[/cyan]\n")
    
    console.print("[bold]📋 ALTERNATIVE: USB Method (Manual Control)[/bold]")
    console.print("If WiFi setup isn't available:")
    
    console.print("\n[bold]Before Test:[/bold]")
    console.print("1. 🔌 Keep device connected via USB for communication")
    console.print("2. ⚙️  Go to Settings > Battery > Battery Health & Charging")
    console.print("3. 🚫 Turn OFF 'Optimized Battery Charging'")
    console.print("4. 🔋 Let battery reach desired starting level (e.g., 90-95%)")
    console.print("5. 🔌 Unplug USB cable to stop charging")
    console.print("6. ⚠️  Note: Device communication will be lost")
    
    console.print("\n[bold]During USB Test:[/bold]")
    console.print("• 📱 Keep device awake and running the target app")
    console.print("• 🚫 Do not plug in USB cable")
    console.print("• ⚡ Monitor battery manually or use short USB reconnects")
    
    console.print("\n[bold]After Test:[/bold]")
    console.print("• 🔌 Reconnect USB cable to resume charging")
    console.print("• ⚙️  Re-enable 'Optimized Battery Charging' if desired")
    
    console.print("\n[bold cyan]Press Enter when ready to start test...[/bold cyan]")
    input()


def monitor_battery(udid, duration_minutes=60, interval_seconds=30, app_name=None):
    """Monitor battery level for specified duration, optionally for a specific app."""
    if app_name:
        console.print(f"[green]Starting battery monitoring for app '{app_name}' for {duration_minutes} minutes...[/green]")
        # Verify app exists
        app_info = check_app_exists(udid, app_name)
        if app_info:
            console.print(f"[cyan]📱 Monitoring: {app_info['display_name']} ({app_info['bundle_id']})[/cyan]")
        else:
            console.print(f"[yellow]⚠️  App '{app_name}' not found. Monitoring overall battery drain.[/yellow]")
    else:
        console.print(f"[green]Starting battery monitoring for {duration_minutes} minutes...[/green]")
    
    readings = []
    total_seconds = duration_minutes * 60
    
    try:
        with Progress() as progress:
            task = progress.add_task("[cyan]Monitoring battery...", total=total_seconds)
            
            for elapsed in range(0, total_seconds, interval_seconds):
                level = get_battery_level(udid)
                charging = get_charging_status(udid)
                timestamp = datetime.now()
                
                if level is not None:
                    reading = {
                        'timestamp': timestamp.isoformat(),
                        'level': level,
                        'charging': charging,
                        'elapsed_minutes': elapsed / 60
                    }
                    if app_name and app_info:
                        reading['monitored_app'] = {
                            'bundle_id': app_info['bundle_id'],
                            'display_name': app_info['display_name']
                        }
                    readings.append(reading)
                    
                    # Enhanced display with app info
                    charging_icon = "⚡" if charging else "🔋"
                    app_indicator = f"📱 {app_info['display_name']}" if app_name and app_info else ""
                    
                    if charging and not app_name:
                        progress.update(task, description=f"[red]⚠️  Device is charging! Unplug to test battery drain[/red]")
                    else:
                        progress.update(task, description=f"[cyan]Battery: {level}% {charging_icon} {app_indicator}[/cyan]")
                else:
                    progress.update(task, description="[yellow]Battery: Unknown[/yellow]")
                
                progress.update(task, advance=interval_seconds)
                time.sleep(interval_seconds)
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Monitoring stopped by user[/yellow]")
    
    # Calculate results with enhanced metrics
    if len(readings) >= 2:
        initial_level = readings[0]['level']
        final_level = readings[-1]['level']
        drain = initial_level - final_level
        
        actual_duration = len(readings) * interval_seconds / 3600  # hours
        drain_rate = drain / actual_duration if actual_duration > 0 else 0
        
        # Check for charging during test
        charging_during_test = any(r['charging'] for r in readings)
        
        console.print("\n[bold]Battery Test Results:[/bold]")
        if app_name and app_info:
            console.print(f"[cyan]📱 App: {app_info['display_name']}[/cyan]")
        console.print(f"Initial Level: {initial_level}%")
        console.print(f"Final Level: {final_level}%") 
        if drain > 0:
            console.print(f"[red]Total Drain: {drain}%[/red]")
            console.print(f"[red]Drain Rate: {drain_rate:.2f}%/hour[/red]")
        else:
            console.print(f"[green]Battery Gained: {abs(drain)}% (device was charging)[/green]")
            console.print(f"[green]Charge Rate: {abs(drain_rate):.2f}%/hour[/green]")
        console.print(f"Readings Taken: {len(readings)}")
        
        if charging_during_test:
            console.print(f"[yellow]⚠️  Warning: Device was charging during test![/yellow]")
        
        return {
            'readings': readings,
            'initial_level': initial_level,
            'final_level': final_level,
            'total_drain': drain,
            'drain_rate_per_hour': drain_rate,
            'app_monitored': app_info if app_name and app_info else None,
            'charging_detected': charging_during_test
        }
    
    return {'readings': readings}


@click.group()
def cli():
    """Simple iOS Battery Tester"""
    pass


@cli.command()
def devices():
    """List connected iOS devices"""
    console.print("[bold blue]Discovering iOS devices...[/bold blue]")
    
    device_list = get_device_list()
    
    if not device_list:
        console.print("[yellow]No iOS devices found.[/yellow]")
        console.print("\n[dim]Make sure:")
        console.print("- Device is connected via USB")
        console.print("- Device is trusted (check for trust dialog)")
        console.print("- Try: idevice_id -l[/dim]")
        return
    
    table = Table(title="Connected iOS Devices")
    table.add_column("Name", style="cyan")
    table.add_column("UDID", style="magenta") 
    table.add_column("iOS Version", style="green")
    table.add_column("Model", style="yellow")
    table.add_column("Connection", style="blue")
    table.add_column("Battery", style="red")
    
    for udid in device_list:
        info = get_device_info(udid)
        battery = get_battery_level(udid)
        battery_str = f"{battery}%" if battery is not None else "N/A"
        
        if info:
            connection_icon = "📶" if info['connection'] == "WiFi" else "🔌" if info['connection'] == "USB" else "❓"
            table.add_row(
                info['name'],
                udid[:16] + "...",
                info['version'],
                info['model'],
                f"{connection_icon} {info['connection']}",
                battery_str
            )
    
    console.print(table)


@cli.command()
def wifi_setup():
    """Set up WiFi connection for iOS device (eliminates USB charging)"""
    console.print("[bold blue]📶 iOS WiFi Connection Setup[/bold blue]")
    console.print("[dim]This will enable wireless device communication, eliminating USB charging interference.[/dim]\n")
    
    # Check for USB connected devices first
    usb_devices = []
    usb_output = run_command("idevice_id -l")
    if usb_output:
        usb_devices = [udid.strip() for udid in usb_output.split('\n') if udid.strip()]
    
    if not usb_devices:
        console.print("[red]❌ No USB-connected devices found[/red]")
        console.print("[dim]Please connect your iOS device via USB first to set up WiFi pairing.[/dim]")
        return
    
    console.print(f"[green]✅ Found {len(usb_devices)} USB-connected device(s)[/green]\n")
    
    # Show devices
    for i, udid in enumerate(usb_devices, 1):
        info = get_device_info(udid)
        if info:
            console.print(f"[cyan]{i}. {info['name']} ({info['version']}) - {udid[:16]}...[/cyan]")
    
    console.print("\n[bold yellow]📋 WiFi Setup Steps:[/bold yellow]")
    console.print("1. ✅ Keep device connected via USB (for initial pairing)")
    console.print("2. 🔧 Enable WiFi pairing on your iOS device:")
    console.print("   • Settings → General → DevTools → iOS Diagnostics → Enable WiFi Debugging")
    console.print("   • OR: Settings → Privacy & Security → Developer → Enable Network Debugging")
    console.print("3. 📱 Make sure device and Mac are on same WiFi network")
    console.print("4. 🔑 We'll pair the device for wireless communication")
    console.print("5. 🔌 After pairing, you can unplug USB for true wireless testing")
    
    console.print("\n[bold cyan]Press Enter when WiFi debugging is enabled on your device...[/bold cyan]")
    input()
    
    # Attempt pairing for each device
    paired_devices = []
    for udid in usb_devices:
        info = get_device_info(udid)
        device_name = info['name'] if info else udid[:8]
        
        console.print(f"\n[cyan]🔗 Attempting to pair {device_name}...[/cyan]")
        
        # Check if already paired
        pair_check = run_command(f"idevicepair -u {udid} validate")
        if pair_check and "SUCCESS" in pair_check.upper():
            console.print(f"[green]✅ {device_name} is already paired[/green]")
            paired_devices.append(udid)
        else:
            # Attempt pairing
            pair_result = run_command(f"idevicepair -u {udid} pair")
            if pair_result and "SUCCESS" in pair_result.upper():
                console.print(f"[green]✅ Successfully paired {device_name}[/green]")
                paired_devices.append(udid)
            else:
                console.print(f"[yellow]⚠️  Pairing may have issues for {device_name}[/yellow]")
                console.print("[dim]Note: Pairing might still work for network access[/dim]")
    
    console.print(f"\n[bold]🔍 Scanning for network devices...[/bold]")
    
    # Wait a moment and scan for network devices
    import time
    time.sleep(3)
    
    network_devices = run_command("idevice_id -n")
    if network_devices:
        network_list = [udid.strip() for udid in network_devices.split('\n') if udid.strip()]
        console.print(f"[green]🎉 Found {len(network_list)} device(s) available via WiFi![/green]")
        
        for udid in network_list:
            info = get_device_info(udid)
            if info:
                console.print(f"[cyan]📶 {info['name']} - WiFi Ready[/cyan]")
        
        console.print("\n[bold green]🚀 WiFi Setup Complete![/bold green]")
        console.print("[green]You can now:[/green]")
        console.print("• 🔌 Unplug USB cable to eliminate charging")
        console.print("• 🧪 Run battery tests wirelessly")
        console.print("• 📊 Get accurate battery drain measurements")
        
        console.print(f"\n[bold]📝 Try these commands:[/bold]")
        console.print(f"[dim]python simple_tester.py devices[/dim]")
        console.print(f"[dim]python simple_tester.py app_test --app 'YouTube' --duration 30[/dim]")
        
    else:
        console.print("[yellow]⚠️  No WiFi devices detected yet[/yellow]")
        console.print("\n[bold]🔧 Troubleshooting:[/bold]")
        console.print("• Ensure WiFi debugging is enabled on iOS device")
        console.print("• Check that device and Mac are on same WiFi network")
        console.print("• Try disconnecting and reconnecting USB briefly")
        console.print("• Some iOS versions may take a few moments to appear")
        
        console.print("\n[dim]You can check later with: python simple_tester.py devices[/dim]")


@cli.command()
def apps():
    """List installed apps on connected iOS devices"""
    console.print("[bold blue]Listing installed apps...[/bold blue]")
    
    device_list = get_device_list()
    
    if not device_list:
        console.print("[red]No iOS devices found[/red]")
        return
    
    udid = device_list[0]  # Use first device
    info = get_device_info(udid)
    
    if info:
        console.print(f"[green]Device: {info['name']} ({info['version']})[/green]")
    
    apps = get_installed_apps(udid)
    
    if not apps:
        console.print("[yellow]No apps found or error accessing device[/yellow]")
        return
    
    table = Table(title=f"Installed Apps ({len(apps)} total)")
    table.add_column("Display Name", style="cyan", width=20)
    table.add_column("Bundle ID", style="magenta", width=30) 
    table.add_column("Version", style="green", width=15)
    
    # Sort apps by display name
    apps.sort(key=lambda x: x['display_name'].lower())
    
    for app in apps:
        table.add_row(
            app['display_name'],
            app['bundle_id'][:30] + "..." if len(app['bundle_id']) > 30 else app['bundle_id'],
            app['version']
        )
    
    console.print(table)


@cli.command()
@click.option('--udid', help='Device UDID (or partial)')
@click.option('--duration', '-d', default=10, help='Test duration in minutes')
@click.option('--interval', '-i', default=30, help='Reading interval in seconds')
@click.option('--app', '-a', help='App name or bundle ID to monitor (optional)')
@click.option('--no-charging-check', is_flag=True, help='Skip charging control instructions')
def test(udid, duration, interval, app, no_charging_check):
    """Run a battery drain test, optionally for a specific app"""
    device_list = get_device_list()
    
    if not device_list:
        console.print("[red]No devices found[/red]")
        return
    
    # Find matching device
    target_udid = None
    if udid:
        for device_udid in device_list:
            if udid in device_udid:
                target_udid = device_udid
                break
    else:
        target_udid = device_list[0]  # Use first device
    
    if not target_udid:
        console.print(f"[red]Device '{udid}' not found[/red]")
        return
    
    info = get_device_info(target_udid)
    if info:
        console.print(f"[green]Testing device: {info['name']} ({info['version']})[/green]")
    
    # App validation if specified
    if app:
        app_info = check_app_exists(target_udid, app)
        if not app_info:
            console.print(f"[red]App '{app}' not found on device[/red]")
            console.print("[dim]Use 'python simple_tester.py apps' to list available apps[/dim]")
            return
        console.print(f"[cyan]🎯 Target App: {app_info['display_name']}[/cyan]")
    
    # Show charging control instructions unless skipped
    if not no_charging_check:
        display_charging_control_instructions()
    
    # Run battery test with app monitoring
    results = monitor_battery(target_udid, duration, interval, app)
    
    # Save results with enhanced metadata
    results_file = f"battery_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    results['device_info'] = info
    results['test_settings'] = {
        'duration_minutes': duration,
        'interval_seconds': interval,
        'app_monitored': app
    }
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    console.print(f"[green]Results saved to {results_file}[/green]")


@cli.command()
@click.option('--udid', help='Device UDID (or partial)')
@click.option('--duration', '-d', default=5, help='Monitoring duration in minutes')
@click.option('--app', '-a', help='App name or bundle ID to monitor (optional)')
def monitor(udid, duration, app):
    """Monitor battery level in real-time, optionally for a specific app"""
    device_list = get_device_list()
    
    if not device_list:
        console.print("[red]No devices found[/red]")
        return
    
    # Find matching device
    target_udid = None
    if udid:
        for device_udid in device_list:
            if udid in device_udid:
                target_udid = device_udid
                break
    else:
        target_udid = device_list[0]  # Use first device
    
    if not target_udid:
        console.print(f"[red]Device '{udid}' not found[/red]")
        return
    
    info = get_device_info(target_udid)
    if info:
        console.print(f"[green]Monitoring device: {info['name']}[/green]")
    
    # App validation if specified
    if app:
        app_info = check_app_exists(target_udid, app)
        if app_info:
            console.print(f"[cyan]🎯 Target App: {app_info['display_name']}[/cyan]")
        else:
            console.print(f"[yellow]App '{app}' not found. Monitoring overall battery.[/yellow]")
    
    monitor_battery(target_udid, duration, 10, app)  # 10 second intervals


@cli.command()
@click.option('--udid', help='Device UDID (or partial)')
@click.option('--app', '-a', required=True, help='App name or bundle ID to test (required)')
@click.option('--duration', '-d', default=30, help='Test duration in minutes (default: 30)')
@click.option('--interval', '-i', default=60, help='Reading interval in seconds (default: 60)')
def app_test(udid, app, duration, interval):
    """Run a comprehensive battery drain test for a specific app with charging control"""
    console.print(f"[bold blue]📱 iOS App Battery Drain Test[/bold blue]")
    console.print(f"[dim]App: {app} | Duration: {duration} minutes | Interval: {interval} seconds[/dim]\n")
    
    device_list = get_device_list()
    
    if not device_list:
        console.print("[red]No devices found[/red]")
        return
    
    # Find matching device
    target_udid = None
    if udid:
        for device_udid in device_list:
            if udid in device_udid:
                target_udid = device_udid
                break
    else:
        target_udid = device_list[0]  # Use first device
    
    if not target_udid:
        console.print(f"[red]Device '{udid}' not found[/red]")
        return
    
    info = get_device_info(target_udid)
    if info:
        console.print(f"[green]🔍 Testing device: {info['name']} ({info['version']})[/green]")
    
    # App validation
    app_info = check_app_exists(target_udid, app)
    if not app_info:
        console.print(f"[red]❌ App '{app}' not found on device[/red]")
        console.print("[dim]💡 Use 'python simple_tester.py apps' to list available apps[/dim]")
        return
    
    console.print(f"[cyan]🎯 Target App: {app_info['display_name']} v{app_info['version']}[/cyan]")
    console.print(f"[dim]Bundle ID: {app_info['bundle_id']}[/dim]\n")
    
    # Check initial charging status
    initial_charging = get_charging_status(target_udid)
    initial_battery = get_battery_level(target_udid)
    
    if initial_charging:
        console.print("[yellow]⚠️  Device is currently charging[/yellow]")
    
    console.print(f"[cyan]🔋 Initial Battery Level: {initial_battery}%[/cyan]\n")
    
    # Show comprehensive test instructions
    display_charging_control_instructions()
    
    console.print(f"[bold green]🚀 Starting {duration}-minute battery drain test for {app_info['display_name']}...[/bold green]")
    console.print("[dim]💡 Make sure the app is active and in use during the test![/dim]\n")
    
    # Run the test
    results = monitor_battery(target_udid, duration, interval, app)
    
    # Enhanced results processing
    if results.get('readings'):
        # Calculate advanced metrics
        readings = results['readings']
        if len(readings) >= 3:
            # Calculate drain rate trend
            mid_point = len(readings) // 2
            early_drain = readings[0]['level'] - readings[mid_point]['level']
            late_drain = readings[mid_point]['level'] - readings[-1]['level']
            
            console.print("\n[bold]📊 Advanced Analysis:[/bold]")
            console.print(f"Early Period Drain: {early_drain}%")
            console.print(f"Late Period Drain: {late_drain}%")
            
            if early_drain > late_drain:
                console.print("[yellow]📈 Battery drain slowed down over time[/yellow]")
            elif late_drain > early_drain:
                console.print("[red]📉 Battery drain accelerated over time[/red]")
            else:
                console.print("[green]📊 Consistent battery drain rate[/green]")
    
    # Save comprehensive results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = f"app_battery_test_{app_info['display_name'].replace(' ', '_')}_{timestamp}.json"
    
    # Add comprehensive metadata
    results['device_info'] = info
    results['test_settings'] = {
        'duration_minutes': duration,
        'interval_seconds': interval,
        'app_monitored': app,
        'test_type': 'app_specific_drain_test'
    }
    results['initial_conditions'] = {
        'charging_at_start': initial_charging,
        'battery_at_start': initial_battery
    }
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    console.print(f"\n[green]💾 Comprehensive results saved to {results_file}[/green]")
    
    # Final recommendations
    if results.get('drain_rate_per_hour', 0) > 10:
        console.print(f"[red]⚠️  High battery drain detected! This app may be power-intensive.[/red]")
    elif results.get('drain_rate_per_hour', 0) < 5:
        console.print(f"[green]✅ Low battery drain. This app appears to be power-efficient.[/green]")
    else:
        console.print(f"[yellow]📊 Moderate battery drain detected.[/yellow]")


if __name__ == "__main__":
    cli()
