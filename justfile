# Copy .env.sample to dist/.env
env:
    mkdir -p dist
    cp -v .env.sample dist/.env

# Build the Python CLI into an exe
cli: env
    pyinstaller \
        --add-data "database/dbCreateScript.sql:database" \
        --onefile main.py \
        --name cli

# Build backend + frontend into an exe
gui: env
    npm --prefix frontend/article-charter install
    npm --prefix frontend/article-charter run build
    pyinstaller --add-data "frontend/article-charter/dist:ui" \
        --add-data "database/dbCreateScript.sql:database" \
        --onefile backend/main.py \
        --name gui


# Build Docusaurus docs
docs:
    mkdir -p dist/docs
    npm --prefix docs install
    npm --prefix docs run build
    cp -vr docs/build/* dist/docs/

# Build everything
all: cli gui docs
