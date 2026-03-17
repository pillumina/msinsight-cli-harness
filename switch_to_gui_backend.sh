#!/bin/bash
# Switch CLI to use GUI's backend

echo "=================================================="
echo "Switching CLI to GUI Backend"
echo "=================================================="

echo ""
echo "Current backend processes:"
ps aux | grep "profiler_server" | grep -v grep

echo ""
echo "Step 1: Killing old backend (port 9000, PID 62120)..."
kill 62120 2>/dev/null && echo "✅ Old backend killed" || echo "⚠️  Old backend already gone"

echo ""
echo "Step 2: Checking GUI backend (port 9001)..."
GUI_BACKEND=$(ps aux | grep "profiler_server.*9001" | grep -v grep)

if [ -n "$GUI_BACKEND" ]; then
    echo "✅ GUI backend is running on port 9001"
    echo "$GUI_BACKEND"
else
    echo "❌ GUI backend not found on port 9001"
    echo "   Please keep MindStudio Insight GUI running!"
    exit 1
fi

echo ""
echo "=================================================="
echo "Next Steps:"
echo "=================================================="
echo "1. Close MindStudio Insight GUI (but backend will keep running)"
echo "2. Run: python3 test_api_v2_live.py --port 9001"
echo ""
echo "Or update CLI default port:"
echo "  export MSINSIGHT_BACKEND_PORT=9001"
echo "=================================================="
