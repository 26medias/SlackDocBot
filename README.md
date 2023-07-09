# SlackDocBot
 Slack bot to chat with your code: Embed the code, chat with GPT, via LangChain

## Setup

Create a `env.py` file:

```
BOT_TOKEN=""
SIGNING_SECRET=""
DEEPLAKE_USERNAME=""
DEEPLAKE_DB=""
CHANNELS = {
    "C05G52A1UTC": {
        "name": "your channel name",
        "db": "deeplake db name"
    },
    "C05G4U9AYR1": {
        "name": "your channel name",
        "db": "deeplake db name"
    }, 
    ...
}
```

`pip install -r requirements.txt`

## Run

`python SlackBot.py`

## Embed a repo


`Embed.py` allows you to generate embeddings for a repo using the `EmbedRepo` class and save them into a DeepLake database. Those embeddings can then be used by the GPT agent.

Example: `python Embed.py -dir "../some_dir" -db "deeplake_db_name"`

Arguments:

- `-dir <dir>`: This argument is **required**. Replace `<dir>` with the path to the repo you want to generate embeddings for.
- `-username <username>`: This argument is optional. Replace `<username>` with your DeepLake username. If you don't provide a username, the script will use the one provided in your `env.py`.
- `-db <db>`: This argument is optional. Replace `<db>` with the name of the DeepLake database where you want to save the embeddings. If you don't provide a database name, the script will use the one provided in your `env.py`.
