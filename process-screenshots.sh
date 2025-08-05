#!/bin/bash

echo "📸 DealFlow Analytics - Screenshot Processor"
echo "=========================================="

# Create output directory
OUTPUT_DIR="chrome-store-screenshots"
mkdir -p $OUTPUT_DIR

# Function to process image
process_image() {
    local input_file=$1
    local base_name=$(basename "$input_file" .png)
    
    echo "Processing: $input_file"
    
    # Use sips (built-in macOS tool) to convert
    # 1280x800 version
    sips -z 800 1280 "$input_file" --out "$OUTPUT_DIR/${base_name}_1280x800.png" >/dev/null 2>&1
    echo "✅ Created: ${base_name}_1280x800.png"
    
    # 640x400 version
    sips -z 400 640 "$input_file" --out "$OUTPUT_DIR/${base_name}_640x400.png" >/dev/null 2>&1
    echo "✅ Created: ${base_name}_640x400.png"
    
    # Also create a padded version with correct aspect ratio
    # This maintains the original aspect ratio with padding
    sips -p 800 1280 "$input_file" --out "$OUTPUT_DIR/${base_name}_1280x800_padded.png" >/dev/null 2>&1
    echo "✅ Created: ${base_name}_1280x800_padded.png (with padding)"
}

# Check if image file provided
if [ $# -eq 0 ]; then
    echo ""
    echo "Usage: ./process-screenshots.sh <screenshot.png>"
    echo ""
    echo "Or save your screenshot as 'screenshot.png' and run again"
    echo ""
    
    # Look for common screenshot names
    if [ -f "screenshot.png" ]; then
        echo "Found screenshot.png - processing..."
        process_image "screenshot.png"
    elif [ -f "Screen Shot "*.png ]; then
        echo "Found Screen Shot - processing..."
        for file in "Screen Shot "*.png; do
            process_image "$file"
            break
        done
    else
        echo "❌ No screenshot found"
        echo ""
        echo "Tips:"
        echo "1. Take a screenshot with Cmd+Shift+4"
        echo "2. Save it as 'screenshot.png' in this directory"
        echo "3. Run this script again"
    fi
else
    # Process provided file
    process_image "$1"
fi

echo ""
echo "📁 Screenshots saved in: $OUTPUT_DIR/"
echo ""
echo "✨ Next steps:"
echo "1. Review the generated screenshots"
echo "2. Choose the best versions for Chrome Web Store"
echo "3. Take 4 more screenshots of different features"
echo "   - Initial state (before analysis)"
echo "   - LinkedIn integration"
echo "   - Export in action"
echo "   - Different company"