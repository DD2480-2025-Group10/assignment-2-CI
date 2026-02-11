# Setting up the Development Environment
This project uses Python 3.13
Begin by setting up a virtual environment to manage dependencies:
```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

Install the required packages:
```bash
pip install -e ".[dev]"
```

# Setting up hosted environment

The CI server can run either as a Github App or as a standalone webhook listener. The Github App is the recomended approach and the only one that has been tested live.
To set it up you all have ownership of the current app installation in `Settings > Integrations > Github Apps`. The app uses some secrets to authenticate against Github, 
hence in order to run the app you'll need to change the secrets into your own (this breaks any currently running instances of the app).

In `Settings > Integrations > Github Apps` hit `Configure > App settings` and change the following
- Create a new Client Secret (currently not used)
- Generate a new Private Key
- Later change the WebHook URL and change the WebHook Secret

On the KTH server (in the repository root), add a new `.env` file with the following content: 
```bash
CLIENT_SECRET=your_client_secret # Not strictly needed
SECRET_KEY="-----BEGIN RSA PRIVATE KEY----- ... -----END RSA PRIVATE KEY-----"
CLIENT_ID=your_client_id # Found in the about section of the app settings
```

After setting up ngrok (see below) and adding the WebHook URL to the app settings, you should be able to run the app with the following command (make sure to have dependencies installed):
```bash
python3.13 -m src.main
```

## Install and run ngrok
In order to setup ngrok you first need to [create an account](https://dashboard.ngrok.com/signup). Then, on your kth server, download and unzip ngrok:
```bash
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar xvzf ./ngrok-v3-stable-linux-amd64.tgz -C <path_to_unzip>
```

Visit your [ngrok dashboard](https://dashboard.ngrok.com/get-started/setup/linux) and copy the authtoken setup command from that page. It should look something like this:
```bash
ngrok config add-authtoken <TOKEN>
```

I recommend adding a [traffic policy](https://ngrok.com/docs/traffic-policy/actions/verify-webhook?ref=getting-started&cty=agent-cli) to only allow traffic from Github. This is done by creating a new policy file `github-policy.yml` with the following content:
```yml
on_http_request:
  - actions:
      - type: verify-webhook
        config:
          provider: github
          secret: "{your secret}"
```

The secret in this case being the WebHook Secret and NOT the Client Secret. Then, start ngrok with the following command:
```bash
./<path_to_ngrok>/ngrok http 8010 --traffic-policy-file github_policy.yml
```

Add the generated ngrok URL and route as the WebHook URL in the Github App settings. You should now be able to receive events from Github and see them in the ngrok dashboard.


# Code formatting
This project uses [Ruff](https://docs.astral.sh/ruff/) for code formatting and linting. The formatting configuration is defined in `pyproject.toml`.

To format all Python files in the project:
```bash
ruff format .
```

To check if code is properly formatted (without making changes):
```bash
ruff format --check .
ruff check .
```

# API Documentation

This project uses [pdoc](https://pdoc.dev/) to generate API documentation from Python docstrings.

## Generate documentation

To generate HTML documentation for all modules:
```bash
python -m pdoc -o docs src
```

This will create documentation in the `docs/` directory.

## View documentation

### Option 1: Open directly in browser
Open `docs/index.html` in your web browser:
```bash
# On Linux
xdg-open docs/index.html

# On macOS
open docs/index.html

# On Windows
start docs/index.html
```

### Option 2: Serve with local HTTP server
Start a local web server to browse the documentation:
```bash
cd docs
python -m http.server 8080
```

Then open http://localhost:8080 in your browser.

The documentation includes:
- All public classes and their methods
- Function signatures with parameter types
- Return types
- Docstring descriptions
- Module structure and organization

# Way of working


## Principles Established

Principles and constraints are committed to by the team. ✅

Principles and constraints are agreed to by the stakeholders. ✅

The tool needs of the work and its stakeholders are agreed.  ✅

A recommendation for the approach to be taken is available. ✅

The context within which the team will operate is understood ✅

The constraints that apply to the selection, acquisition, and use of practices and tools are
known. ✅

## Foundation Established

The key practices and tools that form the foundation of the way-of-working are
selected. ✅

Enough practices for work to start are agreed to by the team. ✅

All non-negotiable practices and tools have been identified. ✅

The gaps that exist between the practices and tools that are needed and the practices and
tools that are available have been analyzed and understood. ✅

The capability gaps that exist between what is needed to execute the desired way of
working and the capability levels of the team have been analyzed and understood. ✅

The selected practices and tools have been integrated to form a usable way-of-working. ✅

## In Use

The practices and tools are being used to do real work. ✅

The use of the practices and tools selected are regularly inspected. ✅

The practices and tools are being adapted to the team’s context. ✅

The use of the practices and tools is supported by the team. ✅

Procedures are in place to handle feedback on the team’s way of working. ✅

The practices and tools support team communication and collaboration. ✅

## In Place

The practices and tools are being used by the whole team to perform their work. ❌

All team members have access to the practices and tools required to do their work. ❌

The whole team is involved in the inspection and adaptation of the way-of-working. ❌


Based on the checklist in the Essence Standard v1.2, we asses our way of working as currently completing the In Use state and starting with the In Place state. Our practices and tools are being used for real work and team members are beginning to use them consistently. We feel like we have handled feedback better through informal communication such as on Discord. We have not reached the In Place state since the practices and tools are not fully being used by the whole team. The main obstacle to reach this state is the short assignments which limits the time needed for practices to become second nature.