# Setting up the Development Environment

Begin by setting up a virtual environment to manage dependencies:
```bash
python3 -m venv .venv
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
PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY----- ... -----END RSA PRIVATE KEY-----"
CLIENT_ID=your_client_id # Found in the about section of the app settings
```

After setting up ngrok (see below) and adding the WebHook URL to the app settings, you should be able to run the app with the following command (make sure to have dependencies installed):
```bash
python3 -m src.main
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

I recommend adding a [trafic policy](https://ngrok.com/docs/traffic-policy/actions/verify-webhook?ref=getting-started&cty=agent-cli) to only allow traffic from Github. This is done by creating a new policy file `github-policy.yml` with the following content:
```yml
on_http_request:
  - actions:
      - type: verify-webhook
        config:
          provider: github
          secret: "{your secret}"
```

The secret in this case being the WebHook Secret and NOT the Client Secret. Then, start Ngrok with the following command:
```bash
./<path_to_ngrok>/ngrok http 8080 --traffic-policy-file github_policy.yml
```

Add the generated ngrok URL and route as the WebHook URL in the Github App settings. You should now be able to receive events from Github and see them in the ngrok dashboard.
