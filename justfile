# Build the Python CLI into an exe
cli:
    pyinstaller \
        --add-data "database/dbCreateScript.sql:database" \
        --onefile main.py \
        --name cli

# Build backend + frontend into an exe
gui:
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
