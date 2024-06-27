#!/bin/bash

# Step 1: Change directory to where the script is located
cd "$(dirname "$0")"

# Step 2: Create directory in /opt and copy program files
echo "Copying program files to /opt/adbtools..."
sudo mkdir -p /opt/adbtools
sudo cp -r ./* /opt/adbtools

# Step 3: Install Python dependencies from requirements.txt (if any)
echo "Installing Python dependencies..."
pip install -r /opt/adbtools/requirements.txt

# Step 4: Create a wrapper script to execute main.py with dependencies
echo "Creating wrapper script..."

cat <<EOF > adbtools
#!/bin/bash

PYTHON_SCRIPT="/opt/adbtools/main.py"
PYTHON_PATH="/opt/adbtools/prog"

PYTHONPATH="\$PYTHON_PATH" python3 "\$PYTHON_SCRIPT" "\$@"
EOF

# Step 5: Make the wrapper script executable
echo "Making wrapper script executable..."
chmod +x adbtools

# Step 6: Move the wrapper script to /usr/local/bin to make it executable system-wide
echo "Moving wrapper script to /usr/local/bin..."
sudo mv adbtools /usr/local/bin/adbtools

echo "Installation complete!"
echo "You can now run 'adbtools' from anywhere in the terminal."
