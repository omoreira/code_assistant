# Demo Workflow - Local Coding Assistant

This document demonstrates the complete workflow of the local coding assistant using a simple example.

---

## Scenario: Creating a Data Processing Pipeline

We want to create a simple Python project that processes CSV data.

### Project Structure (What We Want)
```
./data_processor/
├── src/
│   ├── main.py         (entry point)
│   ├── data_loader.py  (load CSV files)
│   ├── processor.py    (process data)
│   └── exporter.py     (export results)
├── tests/
│   ├── test_loader.py
│   └── test_processor.py
└── config/
    └── settings.yaml   (configuration file)
```

---

## Stage 1: Create Project Definition

### Step 1a: Run starterfile_creator.py

```bash
$ python starterfile_creator.py
```

### Step 1b: Build Structure Interactively

```
============================================================
STARTERFILE CREATOR - Main Menu
============================================================
1. Create new project structure
2. View current structure
3. Add/Edit pseudocode for files
4. Preview starterfile.pseudo
5. Save to starterfile.pseudo
6. Load existing starterfile.pseudo
7. Clear all
8. Exit
------------------------------------------------------------
Select option (1-8): 1

============================================================
CREATE PROJECT STRUCTURE
============================================================

Enter root directory (e.g., ./my_project): ./data_processor
Root directory set: ./data_processor

[./data_processor]
1. Add directory
2. Add file
3. Go to parent
4. Done
Select (1-4): 1
Directory name: src
Add items to ./data_processor/src? (y/n): y

[./data_processor/src]
1. Add directory
2. Add file
3. Go to parent
4. Done
Select (1-4): 2
Filename (with extension): main.py
✓ Added file: ./data_processor/src/main.py

[./data_processor/src]
Select (1-4): 2
Filename (with extension): data_loader.py
✓ Added file: ./data_processor/src/data_loader.py

[./data_processor/src]
Select (1-4): 2
Filename (with extension): processor.py
✓ Added file: ./data_processor/src/processor.py

[./data_processor/src]
Select (1-4): 2
Filename (with extension): exporter.py
✓ Added file: ./data_processor/src/exporter.py

[./data_processor/src]
Select (1-4): 3
# (Go back to parent)

[./data_processor]
Select (1-4): 1
Directory name: tests
Add items to ./data_processor/tests? (y/n): y

[./data_processor/tests]
Select (1-4): 2
Filename (with extension): test_loader.py
✓ Added file: ./data_processor/tests/test_loader.py

[./data_processor/tests]
Select (1-4): 2
Filename (with extension): test_processor.py
✓ Added file: ./data_processor/tests/test_processor.py

[./data_processor/tests]
Select (1-4): 3

[./data_processor]
Select (1-4): 1
Directory name: config
Add items to ./data_processor/config? (y/n): n

[./data_processor]
Select (1-4): 4
# (Done with structure)

============================================================
STARTERFILE CREATOR - Main Menu
============================================================
Select option (1-8): 2

============================================================
CURRENT STRUCTURE
============================================================

./data_processor
├── src/
│   ├── main.py
│   ├── data_loader.py
│   ├── processor.py
│   └── exporter.py
├── tests/
│   ├── test_loader.py
│   └── test_processor.py
└── config/

# (Good! Structure looks correct)

============================================================
STARTERFILE CREATOR - Main Menu
============================================================
Select option (1-8): 3

============================================================
MANAGE PSEUDOCODE
============================================================

Files in project:
  1. [ ] ./data_processor/src/main.py
  2. [ ] ./data_processor/src/data_loader.py
  3. [ ] ./data_processor/src/processor.py
  4. [ ] ./data_processor/src/exporter.py
  5. [ ] ./data_processor/tests/test_loader.py
  6. [ ] ./data_processor/tests/test_processor.py

Select file number (or 'done' to return): 1

============================================================
EDIT PSEUDOCODE: ./data_processor/src/main.py
============================================================

[INPUT]
Enter input (multi-line, type 'END' on new line to finish):
Command line arguments with input file path
END

[OUTPUT]
Enter output (multi-line, type 'END' on new line to finish):
Processed data exported to output file
END

[TASK]
Enter task (multi-line, type 'END' on new line to finish):
Main entry point for data processing pipeline
Parse arguments, load data, process, and export results
END

[CONDITIONS]
Enter conditions (multi-line, type 'END' on new line to finish):
Input CSV file must exist
END

[PREFERENCES]
Enter preferences (multi-line, type 'END' on new line to finish):
Use argparse for CLI arguments
Implement logging for debugging
END

✓ Pseudocode saved for ./data_processor/src/main.py

# (Continue for other files: 2, 3, 4, 5, 6)
# (Similar pseudocode entries...)

Select file number (or 'done' to return): done

============================================================
STARTERFILE CREATOR - Main Menu
============================================================
Select option (1-8): 4

============================================================
PREVIEW STARTERFILE.PSEUDO
============================================================

# REPOMAP

./data_processor
        |______ src/
        |______ main.py
        |______ data_loader.py
        |______ processor.py
        |______ exporter.py
        |______ tests/
        |______ test_loader.py
        |______ test_processor.py
        |______ config/


# PSEUDOCODE


## ./data_processor/src/main.py

INPUT: Command line arguments with input file path

OUTPUT: Processed data exported to output file

TASK: Main entry point for data processing pipeline
Parse arguments, load data, process, and export results

CONDITIONS: Input CSV file must exist

PREFERENCES: Use argparse for CLI arguments
Implement logging for debugging

## ./data_processor/src/data_loader.py

INPUT: File path to CSV file

OUTPUT: Pandas DataFrame with loaded data

TASK: Load CSV data and perform basic validation

CONDITIONS: File must be readable and valid CSV format

PREFERENCES: Use pandas for data loading
Add error handling for malformed files

# (... more files ...)

Press Enter to continue...

============================================================
STARTERFILE CREATOR - Main Menu
============================================================
Select option (1-8): 5

Filename (default: starterfile.pseudo): 
✓ Saved to starterfile.pseudo

Select option (1-8): 8
Goodbye!
```

### Result: Generated `starterfile.pseudo`

The tool created a properly formatted file with:
- ✅ REPOMAP section (directory structure)
- ✅ PSEUDOCODE section (specifications for each file)

---

## Stage 2: Create Project Skeleton

Now we have `starterfile.pseudo`, let's create the actual directory structure.

```bash
$ python blueprint_renderer.py
```

### Output:

```
[blueprint_renderer] Reading starterfile.pseudo...
Found 7 directories and 6 files to create

Blueprint creation completed successfully!

Created Directories (7):
  ✓ ./data_processor
  ✓ ./data_processor/src
  ✓ ./data_processor/tests
  ✓ ./data_processor/config

Skipped Directories (0):
  (none)

Created Files (6):
  ✓ ./data_processor/src/main.py
  ✓ ./data_processor/src/data_loader.py
  ✓ ./data_processor/src/processor.py
  ✓ ./data_processor/src/exporter.py
  ✓ ./data_processor/tests/test_loader.py
  ✓ ./data_processor/tests/test_processor.py

Skipped Files (0):
  (none)

[Result]: success
```

### What Was Created:

```
./data_processor/
├── config/
├── src/
│   ├── __pycache__/
│   ├── data_loader.py (empty)
│   ├── exporter.py (empty)
│   ├── main.py (empty)
│   └── processor.py (empty)
└── tests/
    ├── test_loader.py (empty)
    └── test_processor.py (empty)
```

---

## Stage 3: Generate Real Code

Now we have the skeleton. Let's generate actual code from the pseudocode specifications.

```bash
$ python pseudocode_renderer.py
```

### Output:

```
[pseudocode_renderer] Detected starterfile.pseudo → Running MODE A (Fresh Project)

============================================================
MODE A: Fresh Project Initialization
============================================================

[Step 1] Extracting pseudocode from starterfile.pseudo...
  Found 6 files with pseudocode

[Step 2] Verifying project structure...
  ✓ File verified: ./data_processor/src/main.py (empty, ready for conversion)
  ✓ File verified: ./data_processor/src/data_loader.py (empty, ready for conversion)
  ✓ File verified: ./data_processor/src/processor.py (empty, ready for conversion)
  ✓ File verified: ./data_processor/src/exporter.py (empty, ready for conversion)
  ✓ File verified: ./data_processor/tests/test_loader.py (empty, ready for conversion)
  ✓ File verified: ./data_processor/tests/test_processor.py (empty, ready for conversion)

[Step 3] Converting pseudocode to real code...
  Converting: ./data_processor/src/main.py
    ✓ Converted and saved
  Converting: ./data_processor/src/data_loader.py
    ✓ Converted and saved
  Converting: ./data_processor/src/processor.py
    ✓ Converted and saved
  Converting: ./data_processor/src/exporter.py
    ✓ Converted and saved
  Converting: ./data_processor/tests/test_loader.py
    ✓ Converted and saved
  Converting: ./data_processor/tests/test_processor.py
    ✓ Converted and saved

[Step 4] Cleanup: Removing starterfile.pseudo...
  ✓ Deleted starterfile.pseudo

============================================================
CONVERSION SUMMARY
============================================================

✓ Successfully converted 6 file(s):
  - ./data_processor/src/main.py
  - ./data_processor/src/data_loader.py
  - ./data_processor/src/processor.py
  - ./data_processor/src/exporter.py
  - ./data_processor/tests/test_loader.py
  - ./data_processor/tests/test_processor.py

⚠ Warnings (0):
  (none)

✗ Errors (0):
  (none)

============================================================

[Result]: success
```

### Generated Code Example

**`./data_processor/src/main.py`** (Generated by LLM):

```python
#!/usr/bin/env python3
"""
Main entry point for data processing pipeline.

This module handles command-line argument parsing, orchestrates the data
loading, processing, and export workflow.
"""

import argparse
import logging
import sys
from pathlib import Path

from data_loader import load_csv_data
from processor import process_data
from exporter import export_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """
    Main entry point for the data processing pipeline.
    
    Parses command-line arguments, loads data from CSV file,
    processes it according to specified operations, and exports
    the results.
    """
    parser = argparse.ArgumentParser(
        description='Data processing pipeline for CSV files'
    )
    parser.add_argument(
        'input_file',
        type=str,
        help='Path to input CSV file'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='output.csv',
        help='Path to output file (default: output.csv)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    try:
        # Validate input file
        input_path = Path(args.input_file)
        if not input_path.exists():
            logger.error(f"Input file not found: {args.input_file}")
            sys.exit(1)
        
        logger.info(f"Loading data from {args.input_file}...")
        df = load_csv_data(args.input_file)
        logger.info(f"Loaded {len(df)} rows")
        
        logger.info("Processing data...")
        processed_df = process_data(df)
        logger.info(f"Processing complete, {len(processed_df)} rows result")
        
        logger.info(f"Exporting to {args.output}...")
        export_data(processed_df, args.output)
        logger.info("Export complete!")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
```

**`./data_processor/src/data_loader.py`** (Generated by LLM):

```python
"""
CSV Data Loading Module

Handles loading and basic validation of CSV data files.
Uses pandas for data loading and basic error handling.
"""

import logging
from pathlib import Path
from typing import Union

import pandas as pd

logger = logging.getLogger(__name__)


def load_csv_data(filepath: Union[str, Path]) -> pd.DataFrame:
    """
    Load CSV data from file with validation.
    
    Args:
        filepath: Path to CSV file
        
    Returns:
        Pandas DataFrame containing the loaded data
        
    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file is not valid CSV format
        IOError: If file cannot be read
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    if not filepath.suffix.lower() == '.csv':
        logger.warning(f"File extension is {filepath.suffix}, expected .csv")
    
    try:
        logger.debug(f"Reading CSV file: {filepath}")
        df = pd.read_csv(filepath)
        
        if df.empty:
            logger.warning("Loaded CSV file is empty")
        
        logger.info(f"Successfully loaded {len(df)} rows and {len(df.columns)} columns")
        return df
        
    except pd.errors.EmptyDataError:
        raise ValueError("CSV file is empty")
    except pd.errors.ParserError as e:
        raise ValueError(f"Invalid CSV format: {str(e)}")
    except Exception as e:
        raise IOError(f"Error reading CSV file: {str(e)}")
```

---

## Stage 4: Run and Iterate

Now you have a fully generated project!

```bash
$ cd ./data_processor
$ python src/main.py input_data.csv -o output.csv --verbose
2024-01-15 10:23:45,123 - __main__ - INFO - Loading data from input_data.csv...
2024-01-15 10:23:45,456 - __main__ - INFO - Loaded 1000 rows
2024-01-15 10:23:45,789 - __main__ - INFO - Processing data...
2024-01-15 10:23:46,123 - __main__ - INFO - Processing complete, 950 rows result
2024-01-15 10:23:46,456 - __main__ - INFO - Exporting to output.csv...
2024-01-15 10:23:46,789 - __main__ - INFO - Export complete!
```

---

## Iterative Improvement: Mode B

If you want to add more features to an existing project:

### 1. Add pseudocode to an existing file:

**`./data_processor/src/visualizer.py`**:
```python
"""
Data Visualization Module

"""Pseudo Code"""
INPUT: Pandas DataFrame
OUTPUT: Matplotlib figure with plots
TASK: Create visualization of processed data with multiple plots
CONDITIONS: Data must have numeric columns
PREFERENCES: Use matplotlib subplots, add proper labels and titles
"""End Pseudo Code"""

# This file will be generated by the LLM
```

### 2. Run pseudocode_renderer in Mode B:

```bash
$ python pseudocode_renderer.py
```

```
[pseudocode_renderer] starterfile.pseudo not found → Running MODE B (Existing Project)

============================================================
MODE B: Existing Project Development
============================================================

[Step 1] Scanning project for pseudocode comments...
  Found 1 file with pseudocode
    - ./data_processor/src/visualizer.py

[Step 2] Extracting and converting pseudocode...
  Converting: ./data_processor/src/visualizer.py
    ✓ Converted and saved

============================================================
CONVERSION SUMMARY
============================================================

✓ Successfully converted 1 file(s):
  - ./data_processor/src/visualizer.py

⚠ Warnings (0):

✗ Errors (0):

============================================================
```

Now `visualizer.py` has real code!

---

## Summary: Complete Workflow

```
┌──────────────────────────┐
│  starterfile_creator.py  │  ← Interactive tool
└───────────┬──────────────┘
            │
            ↓
      ┌─────────────┐
      │starterfile  │  ← Project specification
      │.pseudo      │
      └──────┬──────┘
             │
             ├─→ blueprint_renderer.py  ← Creates skeleton
             │         │
             │         ↓
             │   Directory Tree + Empty Files
             │         │
             │         ├─→ pseudocode_renderer.py (Mode A)  ← Generates code
             │                     │
             │                     ↓
             │              Real Code Files
             │                     │
             │                     └─→ Delete starterfile.pseudo
             │
             └─→ pseudocode_renderer.py (Mode B - Later)
                      │
                      ↓
               Add features to existing project
```

---

## Key Benefits

✅ **Fast Project Setup**: From idea to working code in minutes
✅ **Clear Specifications**: Pseudocode makes requirements explicit
✅ **Local LLM**: No external APIs needed
✅ **Non-Destructive**: Never overwrites existing files
✅ **Iterative**: Can keep adding features in Mode B
✅ **Maintainable**: All specifications in one place

---

This complete workflow demonstrates the power of the local coding assistant system!
