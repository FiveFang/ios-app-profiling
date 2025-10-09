# Device Profiling Parser - Usage Examples

This document shows how to use the device profiling parser for various iOS profiling scenarios.

## Quick Start

### 1. Parse a Device-Generated .aar File
```bash
# Basic parsing
python device_profiling_parser.py parse-aar --file MyApp_Profile.aar

# Parse with custom output location
python device_profiling_parser.py parse-aar --file MyApp_Profile.aar --output results/analysis.json
```

### 2. Scan Directory for Profiling Files
```bash
# Scan current directory
python device_profiling_parser.py scan

# Scan specific directory
python device_profiling_parser.py scan --directory /path/to/profiles
```

### 3. Analyze Parsed Data
```bash
# Analyze with app focus
python device_profiling_parser.py analyze --file MyApp_Profile.aar --app-name "MyApp"

# Analyze already parsed JSON
python device_profiling_parser.py analyze --file results/analysis.json
```

## Supported File Formats

### Apple Archive (.aar) Files
- Created by iOS Power Profiler on device
- Contains compressed profiling data
- Includes timing, energy, and app-specific metrics

### Other Formats (Future Support)
- `.trace` - Instruments trace files
- `.dtps` - Device performance statistics
- `.energy` - Energy usage logs

## Workflow Examples

### Manual Device Profiling Workflow

1. **On iOS Device:**
   - Open Settings → Developer → Power Profiler
   - Start profiling session
   - Use your app normally
   - Stop profiling and export .aar file

2. **Transfer to Mac:**
   - AirDrop, email, or USB transfer the .aar file
   - Place in your analysis directory

3. **Parse and Analyze:**
   ```bash
   # Parse the device profile
   python device_profiling_parser.py parse-aar --file DeviceProfile.aar
   
   # Generate detailed analysis
   python device_profiling_parser.py analyze --file DeviceProfile.aar --app-name "YourApp"
   ```

### Comparison with Live Profiling

```bash
# 1. Parse device-generated profile
python device_profiling_parser.py parse-aar --file device_profile.aar

# 2. Run live profiling for same app
python instruments_tester.py hybrid-test --device "iPhone" --app "com.yourapp" --duration 1

# 3. Compare results manually or build comparison script
```

## Output Format

### JSON Structure
```json
{
  "file_info": {
    "path": "profile.aar",
    "size_bytes": 936609,
    "format": "aar",
    "parsed_at": "2025-10-08T11:47:44.700329"
  },
  "energy_data": {
    "timing_info": {
      "start_time": "2025-10-04T18:57:07",
      "end_time": "2025-10-04T18:57:29", 
      "duration_seconds": 22.0,
      "duration_minutes": 0.367
    },
    "energy_estimation": {
      "estimated_total_mah": 0.73,
      "estimated_app_mah": 0.29,
      "confidence": "very_low"
    }
  },
  "parsing_method": "instruments_export"
}
```

## Integration Examples

### Python Script Integration
```python
from device_profiling_parser import DeviceProfilingParser

# Create parser instance
parser = DeviceProfilingParser()

# Parse .aar file
results = parser.parse_aar_file("profile.aar")

# Extract energy data
energy_data = results.get("energy_data", {})
if "energy_estimation" in energy_data:
    total_mah = energy_data["energy_estimation"]["estimated_total_mah"]
    print(f"Total energy consumption: {total_mah:.2f} mAh")
```

### Batch Processing
```python
import glob
from pathlib import Path

# Process all .aar files in directory
aar_files = glob.glob("profiles/*.aar")
results = []

for aar_file in aar_files:
    parser = DeviceProfilingParser()
    result = parser.parse_aar_file(aar_file)
    results.append(result)

# Analyze batch results
for result in results:
    filename = Path(result["file_info"]["path"]).name
    energy = result["energy_data"].get("energy_estimation", {})
    print(f"{filename}: {energy.get('estimated_total_mah', 0):.2f} mAh")
```

## Advanced Usage

### Custom Analysis Scripts
You can extend the parser for custom analysis:

```python
class CustomAnalyzer(DeviceProfilingParser):
    def analyze_app_efficiency(self, results, baseline_energy):
        """Compare app energy usage against baseline"""
        energy_data = results.get("energy_data", {})
        if "energy_estimation" in energy_data:
            app_energy = energy_data["energy_estimation"]["estimated_app_mah"]
            efficiency = (baseline_energy - app_energy) / baseline_energy * 100
            return {
                "efficiency_improvement": efficiency,
                "energy_saved_mah": baseline_energy - app_energy
            }
        return None
```

### Command Line Automation
```bash
#!/bin/bash
# Automated profiling analysis script

# Process all new .aar files
for file in profiles/*.aar; do
    if [ -f "$file" ]; then
        echo "Processing $file..."
        python device_profiling_parser.py parse-aar --file "$file"
        python device_profiling_parser.py analyze --file "$file" --app-name "MyApp"
    fi
done

# Generate summary report
echo "Analysis complete. Check output/device_profiles/ for results."
```

## Troubleshooting

### Common Issues

1. **"Export failed: Document Missing Template Error"**
   - The .aar file may be corrupted or incompatible
   - Try opening manually in Instruments first
   - Use the binary analysis fallback

2. **Low confidence results**
   - Device profiling sessions were too short
   - Increase profiling duration on device
   - Combine with live profiling for validation

3. **No energy data extracted**
   - File may not contain energy metrics
   - Check if profiling session captured power data
   - Verify iOS device supports Power Profiler

### Debug Mode
```bash
# Enable verbose output
export DEBUG=1
python device_profiling_parser.py parse-aar --file profile.aar
```

## Best Practices

1. **Profiling Duration**: Profile for at least 30 seconds for meaningful data
2. **Consistent Conditions**: Use same device state, battery level, temperature
3. **App Focus**: Focus profiling on specific app activities
4. **Validation**: Cross-reference with live profiling results
5. **Storage**: Organize .aar files by app version, test scenario, date

## Future Enhancements

- Support for additional profiling formats
- Real-time .aar file processing
- Integration with CI/CD pipelines
- Automated comparison reporting
- Machine learning-based energy predictions
