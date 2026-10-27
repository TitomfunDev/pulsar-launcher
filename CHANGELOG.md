# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
If something is incorrect, please open an issue [here](https://github.com/TitomfunDev/pulsar-launcher/issues/new)

## [Unreleased] - XXXX-XX-XX

## [0.4.0-alpha] - 2026-10-27

### Added
- Added java manager. Will now download Eclipse Termurin java.

### Changed
- Changed updater. Now all updates are forced.

## [0.3.1-alpha] - 2026-10-23

### Security
-Fixed python vunerability "regarding eMudhra / emSign CA certificate security incident" [Python Forum report](https://discuss.python.org/t/information-for-python-users-regarding-emudhra-emsign-ca-certificate-security-incident/109576) 


## [0.3.0-alpha] - 2026-10-18

### Added
- Added update confirmation prompt for new version. (Deleted in 0.4.0)
- Integrated PySide6 dialogs for clearer status messages and notifications.


## [0.2.1-alpha] - 2026-10-18

### Fixed
- HotFix, changed pyinstaller configuration in build.yml


## [0.2.0-alpha] - 2026-10-18

### Changed
- Main.py entry point revamped.


### Added
- Added Auto-updater for Windows, Linux et MacOS.
- Added version display on the temporary UI to verify update.


## [0.1.0-alpha] - 2026-10-17

### Changed
- Renamed project from `titomfun_launcher` to `pulsar_launcher`.
- Download.py revamp for threading.
- Main.py entry point revamped. 


### Added
- Added temporary UI for first use of the launcher in real situation.
- Added instance version management for quicker game launch rather than redownloading everthing.
- Added deprecation management feature.


## [0.0.1-alpha] - 2026-08-23

### Added
- Core backend functionality for Minecraft launching, modloader support and future instance support.
- Project structure, base configuration management, and `.gitignore`.
- Added GNU General Public License v3.