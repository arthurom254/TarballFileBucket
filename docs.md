# Upload the image
## Request:
```bash
curl -X POST "http://127.0.0.1:8000/upload/" -F "image=@C:\Users\blue\Downloads\light.jpg"
```
## Respone:
```json
    {
    "status":"success",
    "file_name":"3b121306-627e-4577-87a4-871c690f3ba6.jpg",
    "url":"http://127.0.0.1:8000/file/3b121306-627e-4577-87a4-871c690f3ba6.jpg/"
    }
```

`