# Changelog

All notable changes to CloudDash will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-04-29

### Added
- ✨ **D1 Database Management** - Complete SQL execution interface with schema explorer
- ✨ **R2 Storage Explorer** - Dual-pane bucket browser with smart pagination
- ✨ **Dashboard** - Real-time row-read monitoring and query history tracking
- ✨ **Settings Panel** - API credential verification and daily statistics
- ✨ **Query History Persistence** - Automatic JSON-based query logging (500 entries)
- ✨ **Logging System** - File-based logging for debugging and troubleshooting
- ✨ **Error Handling** - Automatic retry logic with exponential backoff
- 📚 **Comprehensive Documentation** - README with troubleshooting guide

### Features
- Real-time Row-Read Monitor with Green/Yellow/Red indicators
- Cost Estimator for SQL queries with unindexed scan detection
- Smart EXPLAIN QUERY PLAN analysis
- R2 pagination with "Load More" support
- Persistent query history with today's statistics
- Connection verification and credential masking
- Auto-retry on timeouts and rate limits (429 errors)
- 30-second request timeout protection

### Technical
- Type hints added to core modules
- Version pinning in requirements.txt to prevent breaking changes
- Enhanced .env.example with detailed instructions
- Improved pyproject.toml with classifiers and metadata

---

## Planned Features (Future Releases)

### v0.2.0
- [ ] File upload/download in R2 Explorer
- [ ] Query analytics and performance metrics
- [ ] Advanced filtering for query history
- [ ] Configuration file support (YAML)
- [ ] Docker support with Dockerfile

### v0.3.0
- [ ] Unit tests and integration tests
- [ ] Query templates and saved queries
- [ ] Multi-account support
- [ ] Export query results (CSV, JSON)
- [ ] Keyboard macro recording

### v1.0.0
- [ ] Stable API for programmatic access
- [ ] Plugin system for extensions
- [ ] Web UI alternative
- [ ] Performance optimization benchmarks

---

## Version History

| Version | Date | Status |
|---------|------|--------|
| 0.1.0 | 2026-04-29 | ✅ Release (Production Ready) |
