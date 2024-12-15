source /home/team5/edu-for-disabled-api/venv/bin/activate
pip3 install -r requirements.yaml
uvicorn main:app --host 0.0.0.0 --port 8080
