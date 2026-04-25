#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== CloudDash: TUI for Cloudflare Setup ===${NC}"

# 1. Create Virtual Environment
echo -e "\n${BLUE}[1/4] Setting up virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# 2. Install Dependencies
echo -e "${BLUE}[2/4] Installing requirements...${NC}"
pip install -q -r requirements.txt

# 3. Interactive Configuration
echo -e "${BLUE}[3/4] Configuration${NC}"
if [ -f .env ]; then
    echo -e "${GREEN}Using existing .env file.${NC}"
else
    echo "Please provide your Cloudflare credentials (you can find these in your Cloudflare Dashboard)."
    read -p "Enter API Token: " token
    read -p "Enter Account ID: " acc_id
    
    echo "CLOUDFLARE_API_TOKEN=$token" > .env
    echo "CLOUDFLARE_ACCOUNT_ID=$acc_id" >> .env
    echo -e "${GREEN}.env file created successfully!${NC}"
fi

# 4. Create Launcher Script
echo -e "${BLUE}[4/4] Creating launcher script...${NC}"
cat <<EOF > clouddash
#!/bin/bash
source "$(pwd)/venv/bin/activate"
python3 "$(pwd)/main.py"
EOF

chmod +x clouddash

echo -e "\n${GREEN}=== Setup Complete! ===${NC}"
echo -e "You can now start CloudDash by running:"
echo -e "${BLUE}./clouddash${NC}"
