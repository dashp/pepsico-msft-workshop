source "https://rubygems.org"

# Minimal Jekyll setup for local preview (our content uses only
# kramdown GFM + relative-links + the cayman theme).
# Avoids the full github-pages metagem which drags in nokogiri/sassc
# native builds that are painful on ARM64 Windows.
gem "jekyll", "~> 4.3"
gem "jekyll-theme-cayman"
gem "jekyll-relative-links"
gem "kramdown-parser-gfm"
gem "webrick"

# Windows + JRuby fix for time-zone data
gem "tzinfo-data", platforms: [:mingw, :mswin, :x64_mingw, :jruby]
