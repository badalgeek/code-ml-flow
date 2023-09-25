from pathlib import Path
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).parent.resolve()
print(f"templates=`{BASE_DIR}`")
templates = Jinja2Templates(directory=BASE_DIR)