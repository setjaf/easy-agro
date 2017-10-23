1.- Colocar el archivo "app.yalm" en la carpeta del proyecto a hacer deployment
2.- Actualizar archivo requirements.txt
3.- Ejecutar comando "python manage.py collectstatic" en consola, parea que todos los archivos estáticos queden en una sola carpeta se subira a un bucket en GCP
4.- Ejecutar comando "gsutil rsync -R static/ gs://<your-gcs-bucket>/static" para sincronizar el bucket online
5.- Cambiar valor de "STATIC_URL" en settings.py por https://storage.googleapis.com/deploy_set/static/
6.- Ejecutar comando "gcloud app deploy"
