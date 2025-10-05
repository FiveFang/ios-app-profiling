# Output Directory Structure

This directory contains all generated files from iOS battery tests.

## 📁 Directory Structure

### `traces/`
Contains Instruments trace files (.trace directories)
- `battery_profile_YYYYMMDD_HHMMSS.trace/` - Raw Instruments Activity Monitor traces
- These files can be large (100MB+) and contain detailed profiling data
- Can be opened in Instruments app for detailed analysis

### `results/` 
Contains JSON test result files
- `app_battery_test_*.json` - Individual app battery test results
- `battery_comparison_*.json` - Comparative test results (with/without app)
- `validation_report_*.json` - Validation and accuracy reports

### `exports/`
Contains exported trace data files
- `*_toc.xml` - Table of contents exports from traces
- `*_process_ledger.xml` - Process-level energy and CPU data
- `*_system_data.xml` - System monitoring data exports
- `activity_monitor_data.xml` - Activity Monitor exports

## 🧹 Cleanup

To clean up old files:
```bash
# Remove traces older than 7 days
find output/traces -name "*.trace" -mtime +7 -exec rm -rf {} \;

# Remove results older than 30 days  
find output/results -name "*.json" -mtime +30 -delete

# Remove exports older than 7 days
find output/exports -name "*.xml" -mtime +7 -delete
```

## 📊 Analysis

To analyze results:
```bash
# View latest test results
cat output/results/$(ls -t output/results/*.json | head -1) | jq .

# Open latest trace in Instruments
open output/traces/$(ls -t output/traces/ | head -1)
```
