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
[working-directory: 'frontend/article-charter']
gui: env
    #!/usr/bin/env bash
    ROOT='../..'
    npm install
    npm run build
    pyinstaller --add-data "dist:ui" \
        --add-data "$ROOT/database/dbCreateScript.sql:database" \
        --onefile "$ROOT/backend/main.py" \
        --name gui \
        --distpath "$ROOT/dist"


# Build Docusaurus docs
[working-directory: 'docs']
docs:
    #!/usr/bin/env bash
    ROOT='..'
    mkdir -p "$ROOT/dist/docs"
    npm install
    npm run build
    cp -vr build/* "$ROOT/dist/docs/"

# Build everything
all: cli gui docs
