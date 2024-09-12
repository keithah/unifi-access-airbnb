# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.2.0] - 2024-09-11

### Added
- Automatic setting of default door group when only one is available
- Improved error logging for API interactions
- CHANGELOG file to track project changes

### Changed
- Refactored `create_visitor` method to simplify API calls
- Updated `process_reservations` method to use new `create_visitor` implementation
- Improved error handling in API request methods

### Fixed
- Issue with visitor creation failing due to invalid parameters

### Updated
- README with more detailed usage instructions and configuration details
