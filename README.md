# Free Your Software Please!

(Forked from [https://github.com/karan/add-a-license-please](https://github.com/karan/add-a-license-please))

A bot that crawls Github for projects with freedom denying licenses, and asks them to respect the freedoms of others.

![](http://i.imgur.com/I6yp2mR.gif)

Github is full of "open source" projects that carry freedom denying licenses. This bot will create an issue in repositories that are not using the GPL.

### Why include a license?

> Generally speaking, the absence of a license means that the default copyright laws apply. This means that you retain all rights to your source code and that nobody else may reproduce, distribute, or create derivative works from your work. This might not be what you intend.

### Why include the GPL?

> Gernally speaking, the absence of the GPL means that the project is using a license that does not respect the freedoms of anyone who uses its code to its full potential amount of freedom. This means that you still retain some rights to your source code that can impact the reproduction, distribution, and derivative works that come from others using your work as a base. Hence, most non-GPL licenses detract from the freedoms of both you and anyone who uses your software. This may not be what you intend.

Source: https://help.github.com/articles/open-source-licensing/

![](http://i.imgur.com/1eIBvfv.jpg)

### How does it work?

The bot searches Github for repositories that have some stars (although the star restriction is a bit wonky). For the returned repos, it will check to see existence of any license information. If the GPL is missing, it will create an issue in the repo. Simple!

All repositories that are processed (skipped or issue created) are saved in a sqlite3 database. This is done to prevent double scanning the same repository.

### Running

#### Requirements

- Python 2.7
- pip
- sqlite3

#### Instructions 

Create a file called `config.py` that looks like `config_example.py`. Fill in the necessary values.

For Github config:

1. [Register your application](https://developer.github.com/guides/basics-of-authentication/#registering-your-app)
2. [Create your oauth token](https://help.github.com/articles/creating-an-access-token-for-command-line-use/)

Then, to run the bot:

```bash
$ pip install -r requirements.txt
$ python bot.py
```

This only runs the bot once, meaning only one search. To make it look (think `while True: search and stuff`), you need to write your own wrapper. I'm not including mine to prevent misuse of Github's API.

### Testing

From the project root:

```bash
$ pip install -r requirements.txt
$ python -m unittest discover test
```
