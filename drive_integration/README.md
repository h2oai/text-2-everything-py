# H2O Drive to Text2Everything Integration

This folder contains a complete integration solution for transferring data from H2O Drive to the Text2Everything API using the official SDK.

## Files Overview

| File | Description |
|------|-------------|
| `drive_to_t2e_integration.py` | Main integration script with interactive workflow |
| `H2O_Drive_to_T2E_End_to_End.ipynb` | **Complete end-to-end Jupyter notebook** |
| `README_drive_integration.md` | Detailed documentation and usage guide |
| `config_example.py` | Configuration template for customization |
| `requirements_drive_integration.txt` | Python dependencies |
| `test_drive_integration.py` | Test suite for validation |
| `usage_example.py` | Programmatic usage example |

## Quick Start

1. **Install dependencies**:
   ```bash
   cd drive_integration
   pip install -r requirements_drive_integration.txt
   ```

2. **Set environment variables**:
   ```bash
   export H2OGPTE_API_KEY="your-api-key"
   ```

3. **Run the integration**:
   
   **Option A: Interactive Script**
   ```bash
   python drive_to_t2e_integration.py
   ```
   
   **Option B: Jupyter Notebook (Recommended)**
   ```bash
   jupyter notebook H2O_Drive_to_T2E_End_to_End.ipynb
   ```

## Features

- **Interactive project selection**: Choose source and destination projects easily
- **Multiple file format support**: JSON, text, and markdown files
- **Bulk operations**: Efficient SDK-based uploads
- **Comprehensive error handling**: Robust exception management
- **Step-by-step workflow**: Clear progress tracking

## Data Structure

Organize your H2O Drive data like this:
```
project_name/
├── schema_metadata/
│   ├── schema1.json
│   └── schema2.json
├── contexts/
│   ├── context1.json
│   ├── context2.txt
│   └── context3.md
└── golden_examples/
    ├── example1.json
    └── example2.json
```

## Documentation

For detailed documentation, see [`README_drive_integration.md`](README_drive_integration.md).

## Testing

Run the test suite to validate functionality:
```bash
python test_drive_integration.py
```

## Programmatic Usage

See [`usage_example.py`](usage_example.py) for examples of using the integration as a library.
