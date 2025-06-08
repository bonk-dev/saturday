# Build the Python CLI into an exe
cli:
    pyinstaller \
        --add-data "database/dbCreateScript.sql:database" \
        --onefile main.py \
        --name cli

# Build backend + frontend into an exe
app:
    echo TODO


# Build Docusaurus docs
docs:
    mkdir -p dist/docs
    npm --prefix docs install
    npm --prefix docs run build
    cp -vr docs/build/* dist/docs/

# Build everything
all: cli app docs
