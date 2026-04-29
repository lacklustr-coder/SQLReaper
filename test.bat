@echo on
python -c "import sys; print('Python:', sys.version); import flask; print('Flask OK'); import jwt; print('JWT OK')"
pause
