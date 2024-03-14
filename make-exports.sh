#!/bin/bash

generate_password() {
    # Use OpenSSL to generate random bytes and encode them in base64
    openssl rand -base64 "${1:-16}" | tr -d '+/' | fold -w "${1:-16}" | head -n 1
}

if [ -f "exports.sh" ]; then
  echo ""
  echo "    -------------------------------------"
  echo "    The file 'exports.sh' already exists."
  echo ""
  #echo "    Run 'source exports.sh' to use it."
  echo "    -------------------------------------"
  echo ""
  exit 1
fi

MYSQL_ROOT_PASSWORD=$(generate_password 32)
MYSQL_PASSWORD=$(generate_password 32)

# Export the generated passwords as environment variables
echo "Exporting generated MySQL root password: $MYSQL_ROOT_PASSWORD"
echo "Exporting generated MySQL user password: $MYSQL_PASSWORD"
echo ""
echo "Passwords stored in exports.sh for future usage. "
#echo "Run 'source exports.sh' to use it."

export MYSQL_ROOT_PASSWORD="$MYSQL_ROOT_PASSWORD"
export MYSQL_PASSWORD="$MYSQL_PASSWORD"

cat <<EOF > exports.sh
#!/bin/bash
# Export the passwords as environment variables for Labelbase.
export MYSQL_ROOT_PASSWORD="$MYSQL_ROOT_PASSWORD"
export MYSQL_PASSWORD="$MYSQL_PASSWORD"
EOF

chmod +x exports.sh
