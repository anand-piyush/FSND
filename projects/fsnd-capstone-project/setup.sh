
# Database URI
export DATABASE_PATH=postgres://piyush@localhost:5432/casting_agency

# Environment Variables
export ITEMS_PER_PAGE=10

# Flask App config
export FLASK_APP=app
export FLASK_ENV=development

# Configurations gotten from the account created on Auth0
export AUTH0_DOMAIN=iamgmt.eu.auth0.com
export ALGORITHMS=RS256
export API_AUDIENCE=casting_agency

export AUTH0_CLIENT_ID=YbxEqWT3TLHDnjk5Qq6QUAVGpKpN2Dqz
# export AUTH0_CALLBACK_URL="https://localhost:5000/"
export AUTH0_CALLBACK_URL=https://127.0.0.1:8080/login