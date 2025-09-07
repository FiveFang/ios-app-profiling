"""
Command Line Interface for iOS Battery Drain Testing Utility.
"""

import click
import json
import sys
import time
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TaskID
from rich.live import Live
import logging

from ..core.device_manager import DeviceManager
from ..core.battery_monitor import BatteryMonitor
from ..core.test_runner import TestRunner, TestStatus


console = Console()


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx: click.Context, verbose: bool) -> None:
    """iOS Battery Drain Testing Utility."""
    setup_logging(verbose)
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose


@cli.command()
def devices() -> None:
    """List connected iOS devices."""
    console.print("[bold blue]Discovering iOS devices...[/bold blue]")
    
    device_manager = DeviceManager()
    devices = device_manager.discover_devices()
    
    if not devices:
        console.print("[yellow]No iOS devices found.[/yellow]")
        console.print("\n[dim]Make sure:")
        console.print("- Device is connected via USB")
        console.print("- Device is trusted (check for trust dialog)")
        console.print("- libimobiledevice is installed[/dim]")
        return
    
    table = Table(title="Connected iOS Devices")
    table.add_column("Name", style="cyan")
    table.add_column("UDID", style="magenta")
    table.add_column("Version", style="green")
    table.add_column("Model", style="yellow")
    table.add_column("Battery", style="red")
    
    for device in devices:
        battery_str = f"{device.get('battery_level', 'N/A')}%" if device.get('battery_level') else "N/A"
        table.add_row(
            device.get('name', 'Unknown'),
            device['udid'][:16] + "...",  # Truncate UDID
            device.get('version', 'Unknown'),
            device.get('model', 'Unknown'),
            battery_str
        )
    
    console.print(table)


@cli.command()
@click.option('--udid', required=True, help='Device UDID')
@click.option('--duration', '-d', default=60, help='Monitoring duration in minutes')
@click.option('--interval', '-i', default=30, help='Reading interval in seconds')
@click.option('--output', '-o', help='Output file path')
def monitor(udid: str, duration: int, interval: int, output: Optional[str]) -> None:
    """Monitor battery level of a specific device."""
    device_manager = DeviceManager()
    devices = device_manager.discover_devices()
    
    # Find the device
    target_device = None
    for device in devices:
        if device['udid'].startswith(udid) or udid in device['udid']:
            target_device = device
            break
    
    if not target_device:
        console.print(f"[red]Device with UDID '{udid}' not found.[/red]")
        sys.exit(1)
    
    console.print(f"[green]Starting battery monitoring for {target_device['name']}[/green]")
    console.print(f"Duration: {duration} minutes, Interval: {interval} seconds")
    
    lockdown = device_manager.lockdown_clients[target_device['udid']]
    battery_monitor = BatteryMonitor(target_device['udid'], lockdown)
    
    if not battery_monitor.start_monitoring(interval):
        console.print("[red]Failed to start battery monitoring.[/red]")
        sys.exit(1)
    
    try:
        with Progress() as progress:
            task = progress.add_task("[green]Monitoring battery...", total=duration * 60)
            
            start_time = time.time()
            while time.time() - start_time < duration * 60:
                time.sleep(1)
                progress.update(task, advance=1)
                
                # Show current battery level
                current_info = battery_monitor.get_current_battery_info()
                if current_info:
                    level = current_info['level']
                    charging = "⚡" if current_info['is_charging'] else "🔋"
                    progress.update(task, description=f"[green]Battery: {level}% {charging}[/green]")
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Monitoring cancelled by user.[/yellow]")
    
    finally:
        battery_monitor.stop_monitoring()
    
    # Export data
    data = battery_monitor.export_data()
    
    if output:
        with open(output, 'w') as f:
            json.dump(data, f, indent=2)
        console.print(f"[green]Data exported to {output}[/green]")
    else:
        console.print(json.dumps(data, indent=2))


@cli.command()
def scenarios() -> None:
    """List available test scenarios."""
    device_manager = DeviceManager()
    test_runner = TestRunner(device_manager)
    scenarios = test_runner.get_scenarios()
    
    if not scenarios:
        console.print("[yellow]No test scenarios available.[/yellow]")
        return
    
    table = Table(title="Available Test Scenarios")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Duration (min)", style="green")
    table.add_column("App Bundle", style="yellow")
    table.add_column("Description", style="white")
    
    for scenario in scenarios:
        table.add_row(
            scenario.id[:8] + "...",
            scenario.name,
            str(scenario.duration_minutes),
            scenario.app_bundle_id or "N/A",
            scenario.description[:50] + "..." if len(scenario.description) > 50 else scenario.description
        )
    
    console.print(table)


@cli.command()
@click.option('--udid', required=True, help='Device UDID')
@click.option('--scenario', required=True, help='Test scenario ID or name')
@click.option('--output', '-o', help='Output file path')
@click.option('--wait', is_flag=True, help='Wait for test completion')
def test(udid: str, scenario: str, output: Optional[str], wait: bool) -> None:
    """Run a battery drain test."""
    device_manager = DeviceManager()
    target_device = _find_device(device_manager, udid)
    if not target_device:
        return
    
    test_runner = TestRunner(device_manager)
    target_scenario = _find_scenario(test_runner, scenario)
    if not target_scenario:
        return
    
    test_id = _start_test(test_runner, target_scenario, target_device)
    if not test_id:
        return
    
    if wait:
        _wait_for_test_completion(test_runner, test_id, target_scenario, output)


def _find_device(device_manager: DeviceManager, udid: str):
    """Find device by UDID."""
    devices = device_manager.discover_devices()
    for device in devices:
        if device['udid'].startswith(udid) or udid in device['udid']:
            return device
    
    console.print(f"[red]Device with UDID '{udid}' not found.[/red]")
    sys.exit(1)


def _find_scenario(test_runner: TestRunner, scenario: str):
    """Find scenario by ID or name."""
    scenarios = test_runner.get_scenarios()
    for s in scenarios:
        if s.id.startswith(scenario) or scenario.lower() in s.name.lower():
            return s
    
    console.print(f"[red]Scenario '{scenario}' not found.[/red]")
    console.print("Use 'ios-battery-test scenarios' to list available scenarios.")
    sys.exit(1)


def _start_test(test_runner: TestRunner, target_scenario, target_device) -> Optional[str]:
    """Start the test and return test ID."""
    console.print(f"[green]Starting test: {target_scenario.name}[/green]")
    console.print(f"Device: {target_device['name']}")
    console.print(f"Duration: {target_scenario.duration_minutes} minutes")
    
    test_id = test_runner.start_test(target_scenario.id, target_device['udid'])
    if not test_id:
        console.print("[red]Failed to start test.[/red]")
        sys.exit(1)
    
    console.print(f"Test started with ID: {test_id}")
    return test_id


def _wait_for_test_completion(test_runner: TestRunner, test_id: str, target_scenario, output: Optional[str]) -> None:
    """Wait for test completion and show progress."""
    try:
        with Progress() as progress:
            task = progress.add_task("[blue]Running test...", total=target_scenario.duration_minutes * 60)
            
            while True:
                test_result = test_runner.get_test_result(test_id)
                if not test_result or test_result.status in [TestStatus.COMPLETED, TestStatus.FAILED, TestStatus.CANCELLED]:
                    break
                
                _update_progress(progress, task, test_result)
                time.sleep(5)
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopping test...[/yellow]")
        test_runner.stop_test(test_id)
    
    _show_final_results(test_runner, test_id, output)


def _update_progress(progress: Progress, task: TaskID, test_result) -> None:
    """Update progress display."""
    if test_result.started_at:
        elapsed = (time.time() - test_result.started_at.timestamp())
        progress.update(task, completed=elapsed)
        
        if test_result.battery_readings:
            latest = test_result.battery_readings[-1]
            charging = "⚡" if latest.is_charging else "🔋"
            progress.update(task, description=f"[blue]Battery: {latest.level}% {charging}[/blue]")


def _show_final_results(test_runner: TestRunner, test_id: str, output: Optional[str]) -> None:
    """Show final test results and export if needed."""
    final_result = test_runner.get_test_result(test_id)
    if final_result:
        show_test_result(final_result)
        
        if output:
            with open(output, 'w') as f:
                json.dump(final_result.to_dict(), f, indent=2)
            console.print(f"[green]Results exported to {output}[/green]")


@cli.command()
@click.option('--test-id', help='Specific test ID to show')
def results(test_id: Optional[str]) -> None:
    """Show test results."""
    device_manager = DeviceManager()
    test_runner = TestRunner(device_manager)
    
    if test_id:
        test_result = test_runner.get_test_result(test_id)
        if not test_result:
            console.print(f"[red]Test with ID '{test_id}' not found.[/red]")
            sys.exit(1)
        show_test_result(test_result)
    else:
        # Show all tests
        active_tests = test_runner.get_active_tests()
        completed_tests = test_runner.get_completed_tests()
        
        if active_tests:
            console.print("[bold blue]Active Tests:[/bold blue]")
            for test in active_tests:
                show_test_summary(test)
        
        if completed_tests:
            console.print("\n[bold green]Completed Tests:[/bold green]")
            for test in completed_tests[-10:]:  # Show last 10
                show_test_summary(test)


def show_test_summary(test_result) -> None:
    """Show a summary of a test result."""
    status_color = {
        TestStatus.PENDING: "yellow",
        TestStatus.RUNNING: "blue",
        TestStatus.COMPLETED: "green",
        TestStatus.FAILED: "red",
        TestStatus.CANCELLED: "orange"
    }.get(test_result.status, "white")
    
    duration = ""
    if test_result.started_at and test_result.completed_at:
        duration = f" ({(test_result.completed_at - test_result.started_at).total_seconds() / 60:.1f} min)"
    
    console.print(f"  [{status_color}]{test_result.status.value}[/{status_color}] "
                 f"{test_result.scenario.name} - {test_result.device_udid[:16]}...{duration}")


def show_test_result(test_result) -> None:
    """Show detailed test result."""
    console.print(f"\n[bold]Test Result: {test_result.scenario.name}[/bold]")
    console.print(f"ID: {test_result.id}")
    console.print(f"Status: [{test_result.status.name.lower()}]{test_result.status.value}[/{test_result.status.name.lower()}]")
    console.print(f"Device: {test_result.device_udid}")
    
    if test_result.started_at:
        console.print(f"Started: {test_result.started_at}")
    if test_result.completed_at:
        console.print(f"Completed: {test_result.completed_at}")
    
    if test_result.initial_battery_level and test_result.final_battery_level:
        console.print(f"Battery: {test_result.initial_battery_level}% → {test_result.final_battery_level}%")
        console.print(f"Total Drain: {test_result.total_drain}%")
        
        if test_result.drain_rate_per_hour:
            console.print(f"Drain Rate: {test_result.drain_rate_per_hour:.2f}%/hour")
    
    if test_result.error_message:
        console.print(f"[red]Error: {test_result.error_message}[/red]")


@cli.command()
@click.option('--udid', help='Filter by device UDID')
def apps(udid: Optional[str]) -> None:
    """List installed apps on device(s)."""
    device_manager = DeviceManager()
    devices = device_manager.discover_devices()
    
    if not devices:
        console.print("[yellow]No iOS devices found.[/yellow]")
        return
    
    target_devices = devices
    if udid:
        target_devices = [d for d in devices if d['udid'].startswith(udid) or udid in d['udid']]
        if not target_devices:
            console.print(f"[red]Device with UDID '{udid}' not found.[/red]")
            return
    
    for device in target_devices:
        console.print(f"\n[bold blue]Apps on {device['name']} ({device['udid'][:16]}...):[/bold blue]")
        
        apps = device_manager.get_installed_apps(device['udid'])
        if not apps:
            console.print("[yellow]  No user apps found.[/yellow]")
            continue
        
        table = Table()
        table.add_column("Name", style="cyan")
        table.add_column("Bundle ID", style="magenta")
        table.add_column("Version", style="green")
        
        for app in apps:
            table.add_row(
                app['name'],
                app['bundle_id'],
                app['version'] or "Unknown"
            )
        
        console.print(table)


def main() -> None:
    """Main CLI entry point."""
    cli()
