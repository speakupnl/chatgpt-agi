# Asterisk ChatGPT intergration -  Proof of Concept

Read the blogpost about this [here](https://developer.speakup.nl)

A proof of concept AGI script that integrates Asterisk with ChatGPT to hold converstations with ChatGPT.

## Deployment
#### Cloning and installing dependencies
Clone the repo somewhere on your Asterisk system. For example, to `/usr/local/src/`:

```bash
cd /usr/local/src/
https://github.com/speakupnl/chatgpt-agi.git
```

Then, create a virtual environment and install the dependencies:

```
cd chatgpt-agi
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
deactivate
```

Make sure to replace the API key in `chatgpt_agi.py` to your own. 

```bash
vim chatgpt_agi.py
```

#### Configuring Asterisk
Copy the `chatgpt-welcome.wav` or replace it with your own.

Please note, the actual path of your sounds directory may be different depending on your system.

```bash
cp chatgpt-welcome.wav /usr/share/asterisk/sounds/
```

Next, edit your `extensions.conf`. 

```
vim /etc/asterisk/extensions.conf
```

Here is an example of what the dialplan might look like. Replace the phone number to your own.

```
exten = 31532401205,1,Noop(ChatGPT)
 same = n,answer()
 same = n,AGI(/usr/local/src/chatgpt-agi/venv/bin/python3 /usr/local/src/chatgpt-agi/openai_agi.py)
```

Reload the Asterisk dialplan

```bash
asterisk -rx 'dialplan reload'
```

And call away!


## Troubleshooting
If you experience any trouble, check the Asterisk console:

```bash
asterisk -rvvv
```

or check the Asterisk syslog. On systems with `systemd`:

```bash
journalctl -fu asterisk
```
