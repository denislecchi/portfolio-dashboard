#!/bin/bash
echo "====================================="
echo " IBKR to Dashboard Converter v2.0"
echo " (Stocks + Options + Performance)"
echo "====================================="
echo
echo "Looking for IBKR files..."
echo
python3 convert_ibkr_to_csv.py
echo
echo "Done!"
read -p "Press Enter to exit..."
