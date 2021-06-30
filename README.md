# algotrader
An algorithmic trading application supporting plug in data-sources and algo trading strategies.

# Setup
1) Set up your python environment.
   
2) Install a database. This application has been tested on postgresql but should support all main databases.

3) Install the required libraries.

```shell
pip install -r algotrader/requirements.txt
```

4) Create a file named secrets.py in the root folder and store your database password here. If you are using a publicly accessible source control system such as GitHub, exclude this file from your source controlled files (e.g., by adding to .gitignore.)

```python
secrets = {
    'db_pass': 'yourpwd'
}
```

5) Launch the application.

```shell
python -m mt5_correlations/mt5_correlations.py
```

6) Configure your database connection in the setting's dialog which can be accessed through File\Settings. Note this will not require the password as this was stored in secrets.py earlier.

7) The application comes with a MetaTrader5 DataSource for collecting price data. Additional datasources can be built. These should implement the algotrader.connections.ds.DataSource interface and added to the config.yaml file. The datasource config in the config.yaml file must include the class and can also include any required connection parameters. These will be passed to your classes constructor and can be accessed through your classes _params property.

```python
from algotrader.connections.ds import DataSource

class ExampleDataSource(DataSource):
    """
    Example DataSource
    """
    def __init__(self, params):
        # Super
        DataSource.__init__(self, params=params)

        # TODO Connection code here. Can use connection params defined in config.

    def __del__(self):
        # TODO Code to terminate connection here
        pass

    def get_symbols(self):
        # TODO Code to retrieve symbols from data source here. Can use connection params available in _params property.
        print(self._params)
```

config.yaml

```yaml
datasources:
  example_datasource:
    class: package.path.ExampleDataSource
    example_connection_param_1: test
    example_connection_param_2: test
```

8) Once a new datasource has been implemented and added to config.yaml, it will be available to configure in the applications settings dialog. An application restart will be required if new datasources are added.
