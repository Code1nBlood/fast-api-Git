from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr
from database import init_db, table_tokens, create_reset_token, get_reset_token, set_as_used_token, add_user_to_db, get_user_by_email, update_user_password
import time
import uuid

app = FastAPI(title='Сброс пароля')


TOKEN_TTL = 300 

class ForgotPassword(BaseModel):
    email: EmailStr

@app.on_event('startup')
async def startup():
    init_db()
    table_tokens()
    add_user_to_db('user@example.com', 'hashed_password')


@app.post('/forgot-password')
def forgot_password(data: ForgotPassword):

    if not get_user_by_email(data.email):
        raise HTTPException(status_code=404, detail='User not found')
    token = str(uuid.uuid4())
    exp = int(time.time()) + TOKEN_TTL
    create_reset_token(data.email, token, exp)
    reset_link = f"http://127.0.0.1:8000/reset-password?token={token}"
    print(reset_link)
    return {'token': token}
    
@app.get('/reset-password', response_class=HTMLResponse)
def reset_password_page(token: str):
    email = get_reset_token(token)
    if email is None:
        return HTMLResponse("""
            <html>
                <body style = "padding: 40px;">
                    <h2>Ссылка недействительна</h2>
                    <p>Возможно, вы уже использовали эту ссылку или она истекла.</p>
                </body>
            </html>
""", status_code=400)
    else:
        return HTMLResponse(f"""
        <html>
        <head>
            <title>Сброс пароля</title>
            <style>
                body {{ font-family: sans-serif; max-width: 400px; margin: 60px auto; padding: 20px; }}
                input {{ width: 100%; padding: 10px; margin: 8px 0; box-sizing: border-box; border: 1px solid #ccc; border-radius: 4px; }}
                button {{ width: 100%; padding: 12px; background: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }}
                button:hover {{ background: #45a049; }}
                .hint {{ color: #888; font-size: 13px; margin-top: 10px; }}
            </style>
        </head>
        <body>
            <h2>Сброс пароля</h2>
            <p class="hint">Ссылка действительна ещё 20 секунд</p>
            <form method="post" action="/reset-password">
                <input type="hidden" name="token" value="{token}" />
                <label>Новый пароль:</label>
                <input type="password" name="new_password" placeholder="Минимум 8 символов" minlength="8" required />
                <label>Повторите пароль:</label>
                <input type="password" name="confirm_password" placeholder="Повторите пароль" required />
                <button type="submit">Сохранить новый пароль</button>
            </form>
        </body>
        </html>
""")
    
@app.post('/reset-password', response_class=HTMLResponse)
def reset_password(
    token: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):
    
    if len(new_password)< 6:
        raise HTTPException(status_code=400, detail='Password must be at least 6 characters long')
    
    if new_password != confirm_password:
        raise HTTPException(status_code=400, detail='Passwords do not match')
    
    email = get_reset_token(token)
    if email is None:
        raise HTTPException(status_code=400, detail = 'Token expired')
    
    update_user_password(email, new_password)

    set_as_used_token(token)

    return HTMLResponse("""
        <html>
            <body sstyle = "padding: 40px; margin: 50px auto; max-width: 400px;">
                <h2>Пароль успешно изменен</h2>
                <p>Вы можете войти с новым паролем</p>
            </body>
        </html>
    """, status_code=200)
    