# Instime

A time management site

---

## The project

This is my capstone one project for my software engineering bootcamp with Springboard. Below are it's details.

### Deployment

***Instime*** is hosted at this [link on Heroku][live]. Here's what it can do...

* Greet you with random **quotes**, some inspirational, some odd, and some just flat out funny.

    * Sometimes when you're needing the motivation to work, hearing words from others can help.

* Allow you assign blocks of **time** that you're **available** to work on getting things done.

    * In order to get things done, you have to know when you're available to work on them.

* Create **tasks** of things that you need to get done.

    * Unclutter your mind and list out everything you gotta do, so you can sort through them one by one.

* Manage your available **times** by making **plans** of **tasks** to do during them.

    * To get the tasks done, you need a plan of what time you'll be doing them at.

### Navigation

There are multiple ways to get around on the site, but here the general process for a new user.

1. Sign up for an account, you've gotta be logged in to use the site. It'll prompt you on the landing page.

1. After that, you're free to do what you want, here are those options again.

    * Manage your available times on the *freetimes* page.

    * Manage your tasks on the *tasks* page.

    * Check out your plans on the *plans* page.

    * Get random quotes on the home page with the *get quote* button

### The Quotes API

My orginal API was taken down and I had to find a replacement to fetch quotes. Here's [the link to][api] to ***Go Quotes***.

### Technologies & Tools Used

As a fullstack website, there were quite a few that went into the making of Instime.

* HTML

    * Jinja (templating)

* CSS

    * Bulma library with Bulma calendar

* JavaScript

    * Axios library with Bulma calendar

* PostgreSQL

    * SQLAlchemy (ORM)

        * Flask SQLAlchemy (special version for use with the Flask framework)

* Python

    * Flask (backend framework for Python)

        * Flask Login (handle user login & logout)

        * Flask CORS (communication with client side)

        * Flask WTF (creating & validating forms)

        * WTForms Alchemy (making forms from FSQLA models)

        * Flask Bcrypt (encrypting passwords)

    * Others listed in `requirements.txt`

[Proposal Document][propdoc]

[api]:https://goquotes.docs.apiary.io/#

[propdoc]:https://docs.google.com/document/d/1NXsswApnI3eOrPGZjdtL1hzIaHP0ZTS9cs4dvjj8OOc/edit?usp=sharing

[live]:https://instime.herokuapp.com/
