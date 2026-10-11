# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project aims to follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- `# PATHS` section in `starterfile.pseudo`, declaring generation-time
  `root` and `data_dir` (both relative to the starterfile). Parsed by the new
  `code_starter.starterfile_paths.parse_paths`.
- `ENV_VARS` per-file field in `# PSEUDOCODE` blocks, describing the
  environment variables (names/defaults only) the generated code expects.
- Automatic `.env.example` generation at the project root from `ENV_VARS`
  fields (`code_starter.env_example`); it is written only when variables are
  declared and never overwrites an existing file.
- `shared.paths_config.data_dir_source` / `data_dir_is_explicit` to report
  which precedence level supplied the data directory.

### Changed
- The SQLite data directory is no longer created as an implicit side effect.
  It is created only when its location is requested explicitly: a `# PATHS`
  `data_dir`, `--data-dir`, the `CODE_ASSISTANT_DATA_DIR`/`DATA_DIR`
  environment variable, or `--interactive`. Otherwise `.db` creation fails
  with an actionable message (`data_handler.DataDirectoryMissingError`).
- Data-directory precedence is now `--data-dir` > environment variable >
  `# PATHS data_dir` > `config/defaults.yaml` (`paths.data_dir`) > built-in
  `data`.
- Project-root precedence in the pipeline is now an explicit `project_root`
  argument > `# PATHS root` (relative to the starterfile) > current working
  directory. `python -m code_starter.pipeline` treats `project_root` as
  optional.

### Deprecated
- The legacy `# PROJECT_ROOT:` marker is still recognised but superseded by
  `# PATHS` (`root:`); files with neither retain current-working-directory
  semantics.

## [0.1.0] - 2026-09-27

### Added
- Initial release: code_starter / code_analyzer / code_refractor / data_handler
  toolchain, the full pipeline (`run_pipeline.sh`), and supporting assistants.
