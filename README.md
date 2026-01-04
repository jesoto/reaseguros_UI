# Siniestros Vehicular Bot

Bot para la validacion de siniestros vehiculares

---
## Requirements
- pipenv
- streamlit

## Run locally

1. Create a service account file: llm.json

3. Install dependencies using pipenv
   ```bash
   pipenv install
   ```
4. Run the server
    ```shell
   # With pipenv
   pipenv run streamlit run src/app.py

   # With streamlit
   streamlit run src/app.py
    ```
## Deploy to Cloud Run
0. Configure service account for project POC
   ```bash
    gcloud auth activate-service-account sa-nprd-dlk-ia-dev-poc-terrafm@rs-nprd-dlk-ia-dev-poc-55a3.iam.gserviceaccount.com --key-file=sa-nprd-dlk-ia-dev-poc-terrafm_rs-nprd-dlk-ia-dev-poc.json --project=rs-nprd-dlk-ia-dev-poc-55a3
    ```
    
1. Update lock file
    ```bash
    pipenv lock 
    ```
2. Create requirements.txt
    ```shell
    pipenv run pip freeze > requirements.txt
    ```

3. Deploy using Makefile comand

    ```shell
    make deploy
    ```
    ** Retry step 0 if fails
