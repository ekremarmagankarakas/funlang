FROM nginx:1.27-alpine

# Serve the FunLang browser playground (static files)
COPY web/ /usr/share/nginx/html/

EXPOSE 80
