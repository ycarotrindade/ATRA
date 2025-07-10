# ATRA - A True Random Bot

ATRA (Atmospheric Randomness) is a Discord dice bot that uses true randomness to generate values. The bot utilizes the [Random.org](https://www.random.org) API to produce these values. If you have doubts about its true randomness, I recommend checking [this page](https://www.random.org/randomness/) on the Random.org website.

# Features

- A dice bot completly random.
- Statistics about the session.
- The bot's code is structured for scalability.

# Instalation

First you'll need a Discord API token, create one on [Discord Developer Portal](https://discord.com/developers/applications)

After that you'll need a Random.org API token, get one on [api.random.org](https://api.random.org/dashboard)

Now replace the values on `.env-example` and rename the file for `.env`

Install the requirements 
```
pip install -r requirements.txt
```

# Running with Docker

If you use Docker, just modify the `.env-example` file, rename it to `.env`, and then run one of the following commands:

1. Using `make` (recommended):

   * If you have [make](https://en.wikipedia.org/wiki/Make) installed, simply run:

     ```
     make up
     ```

   * Or just:

     ```
     make
     ```

    This will build and run the project using `docker-compose`.

2. Without `make`:

   * Run this command manually:

     ```
     docker-compose up --build
     ```

Now just invite the bot to your server and enjoy



# Usage

- 1d20 = 1 is the amount of dice that will be rolled and 20 the max
- 3#1d20 = this will roll 1d20 3 times
- 1d20 + 5 = this will roll 1d20 and add 5 to the final result

# Notes

- The free version of Random.org API allows just 1,000 requests/day and 250,000 bits/day. **DO NOT USE THIS BOT FOR COMMERCIAL PURPOSES**

- Your discord bot will need **Send Messages** and **Use Slash Commands** permissions.

- **DO NOT SHARE YOUR API TOKENS WITH ANYWONE**
