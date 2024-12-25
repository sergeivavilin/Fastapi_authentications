import uvicorn


if __name__ == '__main__':
    """
    Запуск приложений необходимо осуществлять по отдельности 
    в дальнейшем можно будет запускать через Docker образы и docker-compose
    """
    # Запуск Session authentication приложения
    # uvicorn.run(
    #     app='Session_auth.main:session_app',
    #     host='127.0.0.1',
    #     port=8000,
    #     reload=True,
    # )

    # Запуск Oauth2 authentication приложения
    # uvicorn.run(
    #     app='OAuth2_auth.main:oauth2_app',
    #     host='localhost',
    #     port=8001,
    #     reload=True,
    # )