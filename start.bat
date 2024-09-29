@echo off
echo Activating virtual environment...
call .venv\Scripts\activate

echo Virtual environment activated.

pip install -r requirements.txt

echo Running main.py...
python main.py

echo Script execution completed.