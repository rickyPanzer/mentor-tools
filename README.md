# bloc-mentor-tools

##What it does
Creates a new calendar instantaneously of your Bloc appointments with students. For me the ics file that I imported into google calendar too much latency (it would take a couple days to update), and actually just stopped working in my case, so figured I would make something faster. 

This was made in a couple days, so there is SO MUCH that can be improved with the project. Only works with Google Calendar right now

##Steps to make this work:

1. make a contants.py file in the main directory of the project
2. create two variables called headers and cookies
3. assign headers and cookies to the headers and cookies when logged in at https://bloc.io
4. in the main directory run
```
python -i quickstart.py

main()
```

Voilà!

5) this was built in a couple days, so please report any bugs, feature requests, etc.
