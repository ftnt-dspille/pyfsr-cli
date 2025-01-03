# Option 1: Config file

```bash
# tests/integration/config.yaml
server: "https://fortisoar.example.com"
username: "test-user"
password: "test-password"
verify_ssl: false
```

# Option 2: Set environment variables

```bash
export PYFSR_TEST_SERVER="https://fortisoar.example.com"
export PYFSR_TEST_USERNAME="test-user"
export PYFSR_TEST_PASSWORD="test-password"
export PYFSR_TEST_VERIFY_SSL="false"
```

# Run tests
```bash
# Run only unit tests
pytest tests/commands/test_alerts.py -v

# Run only integration tests
pytest tests/integration/test_alerts.py -v

# Run both
pytest tests/commands/test_alerts.py tests/integration/test_alerts.py -v

# Run specific integration test
pytest tests/integration/test_alerts.py -v -k "test_create_and_list_alert"
```