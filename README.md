# MindStudio Insight CLI Harness

Command-line interface harness for MindStudio Insight performance analysis tool.

## Overview

This project provides a CLI harness that enables natural language control of MindStudio Insight through AI agents.

**Architecture**:
```
User → AI Agent (via Skill) → CLI → Control Layer → Protocol Layer → Backend
```

## Features

- ✅ **Protocol Layer**: WebSocket client for backend communication
- ✅ **Control Layer**: Timeline control and data query APIs
- ✅ **CLI**: Command-line interface with REPL
- ✅ **Skill**: AI agent integration

## Installation

```bash
pip install -e .
```

## Quick Start

```bash
# Close MindStudio Insight GUI (single connection limit)

# Start CLI
cli-anything-msinsight

# Import data
msinsight> import load-profiling /path/to/data

# Query
msinsight> operator top --n 10
msinsight> memory summary

# Control
msinsight> timeline zoom --start 0 --end 1000
```

## Documentation

- [Implementation Roadmap](IMPLEMENTATION_ROADMAP.md) - Development roadmap
- [User Guide](USER_INSTALLATION_GUIDE.md) - Installation and usage
- [API Documentation](MSINSIGHT.md) - CLI commands and options

## Status

**Completion**: 95% ✅

- Core implementation: 100%
- Testing: 90%
- Documentation: 100%

## Verified

- ✅ WebSocket connection
- ✅ Heartbeat check
- ✅ Protocol format

## License

Mulan PSL v2

## Acknowledgments

Generated with [Claude Code](https://claude.com/claude-code)
