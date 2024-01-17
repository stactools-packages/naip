# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/). This project attempts to match the major and minor versions of [stactools](https://github.com/stac-utils/stactools) and increments the patch number as needed.

## [Unreleased]

### Added

- Support for NAIP 2022

### Changed

- Updated repository structure to match [stactools](https://github.com/stac-utils/stactools)

## [v0.4.0] - 2023-05-18

### Added

- Support for NAIP 2021

## [v0.3.2] - 2023-05-03

### Added

- Add Projection Extension field proj:centroid ([#38](https://github.com/stactools-packages/naip/pull/38))

## [v0.3.1] - 2023-02-24

### Fixed

- Certain XML files for 2020 have inconsistent fields, which are now processed correctly instead generating an error. This is a continuation to work performed for the 0.3.0 version release.

## [v0.3.0] - 2023-02-16

### Changed

- Scientific Extension fields are now in the Collection rather than the Item.

### Fixed

- Certain XML files for 2020 have different fields, which are now processed correctly instead
  generating an error.

## [v0.2.0] - 2023-01-31

First release as a stand-alone repository.

[Unreleased]: https://github.com/stactools-packages/naip/compare/v0.4.0..main
[v0.4.0]: https://github.com/stactools-packages/naip/compare/v0.3.2..v0.4.0
[v0.3.2]: https://github.com/stactools-packages/naip/compare/v0.3.1..v0.3.2
[v0.3.1]: https://github.com/stactools-packages/naip/compare/v0.3.0..v0.3.1
[v0.3.0]: https://github.com/stactools-packages/naip/compare/v0.2.0..v0.3.0
[v0.2.0]: https://github.com/stactools-packages/naip/tags/v0.2.0
