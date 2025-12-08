#!/bin/bash
# Create a minimal 16x16 PNG icon
python3 << 'PYTHON'
import struct

# Minimal 16x16 blue PNG
png_data = bytes.fromhex(
    '89504e470d0a1a0a0000000d49484452000000100000001008060000001ff3ff61000000017352474200aece1ce900000006624b474400ff00ff00ffa0bda793000000097048597300000ec400000ec401952b0e1b0000000d49444154789c6360606060600000000500010d0a2db40000000049454e44ae426082'
)

with open('icon.png', 'wb') as f:
    f.write(png_data)
print('Icon created')
PYTHON
chmod +x create-icon.sh && ./create-icon.sh 2>&1 || echo "Trying alternative..."