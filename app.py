from api.api import prepare_app
from lib.config import ProductionConfig
from migrations.migration import migrate

config = ProductionConfig()

if __name__ == '__main__':
    # should be excluded for real production
    migrate(config)
    app = prepare_app(config)
    app.run(host='0.0.0.0', port=config.FLASK_PORT)
