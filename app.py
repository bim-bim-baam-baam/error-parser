from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from log_parser import get_links, parse_log
import requests

app = FastAPI()

class ParseRequest(BaseModel):
    url: str

@app.post("/parse", summary="Парсинг логов", description="Парсит логи по указанному URL и возвращает ошибки.")
def parse_logs(request: ParseRequest):
    """
    Парсит логи по URL и возвращает найденные ошибки в формате JSON.
    """
    try:
        links = get_links(request.url)
        all_errors = []

        for href, link in links:
            error_entry = parse_log(href, link, request.url)
            if error_entry:
                all_errors.append(error_entry)

        return all_errors
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Ошибка запроса: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")
