export PATH="$HOME/.rbenv/bin:$PATH"
eval "$(rbenv init -)"
# Added environment variables for icu4c@77 keg-only package
export PATH="/usr/local/opt/icu4c@77/bin:$PATH"
export PATH="/usr/local/opt/icu4c@77/sbin:$PATH"
export LDFLAGS="-L/usr/local/opt/icu4c@77/lib"
export CPPFLAGS="-I/usr/local/opt/icu4c@77/include"
export PKG_CONFIG_PATH="/usr/local/opt/icu4c@77/lib/pkgconfig"

# Added environment variables for krb5 keg-only package

export PATH="/usr/local/opt/krb5/bin:$PATH"
export PATH="/usr/local/opt/krb5/sbin:$PATH"
export LDFLAGS="-L/usr/local/opt/krb5/lib"
export CPPFLAGS="-I/usr/local/opt/krb5/include"
export PKG_CONFIG_PATH="/usr/local/opt/krb5/lib/pkgconfig"

# Added environment variables for libpq keg-only package

export PATH="/usr/local/opt/libpq/bin:$PATH"
export LDFLAGS="-L/usr/local/opt/libpq/lib"
export CPPFLAGS="-I/usr/local/opt/libpq/include"
export PKG_CONFIG_PATH="/usr/local/opt/libpq/lib/pkgconfig"