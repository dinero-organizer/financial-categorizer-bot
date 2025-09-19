setup:
	@py -3.11 --version >nul 2>&1 || (echo Error: Python 3.11 is not installed or not available. && echo Please install Python 3.11 and ensure it's accessible via 'py -3.11' && exit 1)
	@echo Creating virtual environment with Python 3.11...
	py -3.11 -m venv .venv
	.venv\Scripts\python.exe -m pip install --upgrade pip
	.venv\Scripts\python.exe -m pip install -r requirements.txt
	@echo Setup complete! Virtual environment created at .venv

venv:
	@echo Virtual environment created at .venv
	@echo To activate: .venv\Scripts\activate

run-telegram-bot:
	.venv\Scripts\python.exe src/handlers/telegram_bot.py

clean:
	rmdir /s /q .venv