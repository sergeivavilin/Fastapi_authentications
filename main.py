import uvicorn


if __name__ == '__main__':
    """
    Запуск приложений необходимо осуществлять по отдельности 
    Для запуска конкретного приложения раскомментируйте блок 
    в дальнейшем можно будет запускать через Docker образы и docker-compose
    """

    """
    Session-based authentication приложение
    """
    # uvicorn.run(
    #     app='Session_auth.main:session_app',
    #     host='127.0.0.1',
    #     port=8000,
    #     reload=True,
    # )
    """
    JWT authentication приложение
    """

    # uvicorn.run(
    #     app='JWT_auth.main:JWT_app',
    #     host="127.0.0.1",
    #     port=8002,
    #     reload=True
    # )

    """
    Oauth2 authentication приложение
    """
    uvicorn.run(
        app='OAuth2_auth.main:oauth2_app',
        host='localhost',
        port=8001,
        reload=True,
    )