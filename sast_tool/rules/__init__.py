# sast_tool/rules/__init__.py
from . import sec_001_dangerous_calls
from . import sec_002_dangerous_eval

# If you have sec_999_test.py in that folder, uncomment the line below:
# from . import sec_999_test