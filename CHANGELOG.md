# Changelog

All notable changes to the Text2Everything SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.7-rc2] - 2025-10-27

### Fixed
- **Schema Split Grouping Support**: Fixed `create()` and `bulk_create()` methods to properly handle split schema groups
  - `create()` now returns `Union[SchemaMetadataResponse, List[SchemaMetadataResponse]]` to include all split parts when tables have >8 columns
  - `bulk_create()` now properly flattens results to include all split parts from large tables
  - Split schemas now properly expose `split_group_id`, `split_index`, and `total_splits` fields
  - Previously, only the first part of split schemas was returned, losing track of other parts

### Changed
- **Breaking Change**: `schema_metadata.create()` return type changed from always returning a single `SchemaMetadataResponse` to returning `Union[SchemaMetadataResponse, List[SchemaMetadataResponse]]`
  - Single schemas (≤8 columns) return `SchemaMetadataResponse` as before
  - Split schemas (>8 columns) now return `List[SchemaMetadataResponse]` with all parts
  - Users should check `isinstance(result, list)` to handle both cases

### Added
- Enhanced documentation in `create()` and `bulk_create()` methods explaining split behavior
- Added examples showing how to handle split schemas in docstrings

## [0.1.7-rc1] - Previous Release
