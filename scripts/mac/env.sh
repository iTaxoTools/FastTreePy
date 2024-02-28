# Sources:
# https://mac.r-project.org/openmp/
# https://stackoverflow.com/a/70664229

export LDFLAGS="-L$HOME/.local/lib"
export CPPFLAGS="-I$HOME/.local/include"
export DYLD_LIBRARY_PATH="$HOME/.local/lib"

export PATH="/opt/homebrew/opt/llvm/bin:$PATH"
export CC="/opt/homebrew/opt/llvm/bin/clang"
