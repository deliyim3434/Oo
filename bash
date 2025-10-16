# Heroku CLI'ye giriş yaptığından emin ol
heroku login

# Python buildpack'ini ekle (genellikle otomatiktir ama garanti olsun)
heroku buildpacks:add heroku/python -a SENIN_UYGULAMA_ADIN

# FFmpeg için buildpack'i ekle (En Önemli Adım!)
heroku buildpacks:add https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git -a SENIN_UYGULAMA_ADIN
