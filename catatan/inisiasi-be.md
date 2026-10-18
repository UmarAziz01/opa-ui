### buat sturktur folder
mkdir -p alembic/versions \
  app/core \
  app/common \
  app/modules/{auth,tenants,organizations,applications,policies,bundles,governance,audit} \
  app/workers && \
touch alembic/env.py \
  alembic.ini \
  Dockerfile \
  requirements.txt \
  app/__init__.py \
  app/main.py \
  app/core/{__init__,config,database,security,storage}.py \
  app/common/{__init__,dependencies,exceptions,pagination,utils}.py \
  app/modules/__init__.py \
  app/modules/{auth,tenants,organizations,applications,policies,bundles,governance,audit}/{__init__,router,schemas,service,models}.py \
  app/workers/{__init__,bundle_compiler,trial_checker}.py


### Cara jalankan docker staging
docker compose -f docker-compose.staging.yml up -d --build
docker logs -f opa-backend-staging



### Cara jalankan di lokal
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt


APP_ENV=staging python run_dev.py


APP_ENV=staging alembic revision --autogenerate -m "create_initial_schema"

