from onelist.application import create_app
from onelist.config import DevelopmentConfig

if __name__ == '__main__':
    app = create_app(DevelopmentConfig)
    # app.run()
    app.run(host='0.0.0.0')