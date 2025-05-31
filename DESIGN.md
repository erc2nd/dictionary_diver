# Design Discussion

## Implementation

### Languages used:
- HTML
- CSS
- JavaScript
- Python (+Flask)
- SQLite

*Why I used them*: HTML, CSS, JS were used because, as far as I'm aware, that's the only way to make a website! I used Python/Flask and SQL because of the familiarity I built with them during the course.

### Third-party tools used:
 - [Janome](https://github.com/mocobeta/janome)
    - Janome is a parser for the Japanese language written in Python and built on top of MeCab
    - [MeCab](https://taku910.github.io/mecab/) is an open-source tool for parsing Japanese text

*Why I used Janome*: Since it's written in Python, it was very easy to integrate with my workflow. It also had some of the best documentation of any of the parsers I explored, which allowed me to tailor it to my needs. Furthermore, it comes wholly pre-packaged with a dictionary and is ready to use out-of-the-box, so to speak. Theoretically, I could have used MeCab directly, but Janome's API was significantly easier to work with.

### Dictionaries used:
- 旺文社国語辞典, aka Ōbunsha-kokugojiten, aka the Obunsha Japanese Dictionary

*Why*: I considered several dictionaries, but settled on this one for two reasons. First, the definitions are reasonably modern and easy to understand. Second, the JSON formatting was—relative to other dictionaries—easy to format for entry into a SQL table

- Jim Breen's JMdict

*Why*: This one was much more difficult to wrestle into SQL, but it's up-to-date and is the sort of de facto standard for Japanese-English dictionary applications. It was the obvious answer.

## How it works

### Database

The SQLite database is split into 5 different tables.

- Japanese-English dictionary
- Japanese-Japanese dictionary
- Users table that stores a unique ID, username, and password hash
- A table to store words the user knows, or is learning
- A table to store definitions the user has added. This table acts like a combined JJ & EJ dictionary.

I went with this set up as it seemed like a reasonable separation of data-duties. With just a few SELECT parameters I can get whatever I need for any job in the application as it is now.

### Python Functions
I won't explain every single function in the program, obviously, but I should draw special attention to the parser and dictionary features of the program as they are core to the application.

The parser is truly the core of everything here. When a chunk of text is passed to app.py from the client, it's first passed into the text_parser() function where it's processed by Janome and returned as a list of "tokens", i.e. individual words. From there, it gets passed into the def_builder() function. The def_builder() function uses a series of parameters to direct the construction of a block of html depending on what is being passed in. In the case of parsed Japanese text, the function loops over every token in the list, building the mouseover events, menus, and display properties for each one dynamically. Each word's html is then appended together, and ultimately returned back to app.py where it can be sent back to the client side JavaScript function to display it.

The other core feature is the ability to look up definitions of words. The two dictionaries each get their own functions since fairly different things are required for each due to the formatting of things inside the SQL table. For example, when extracting the English definition, I don't need to parse anything, but I do need to clean up a whole host of extraneous punctuation, and then dress it up in html before sending it back to the JavaScript function.

With Japanese definitions, I also need to do a lot of clean-up. This clean-up is, unfortunately, specific to this particular dictionary, and the cleanup function is a mess of confusing-looking regex that I had to hand-craft based around the very specific idiosyncrasies of the dictionary. Once the function is cleaned up, it's ready to be tossed into the parser, where it gets broken into tokens, and then moved over to the def_builder() for final html-ization!

I'm also super proud of my last-minute implementation of file uploads and downloads, as well as the ability to add user-defined tokens to the parser. These were reach goals of mine, and something I was working on until the last day. There's still much I could do to improve them, but with them fully functional, this now  feels like a piece of software I can and will actually use regularly for my studies.

## Python Structure

On the Python side of things, I decided to keep all functions dealing with requests in the app.py file, feeding data over to the helper.py file for anything else. I tried to strike a balance of separating roles in both files, but also not making things too granular. Ultimately, I don't know if my decisions were the best. For example, I feel that my def_builder() function could be tidied up quite a bit. As it is right now, it's somewhat hard to read and make changes when necessary.


## JavaScript Functions

What I'm happiest with in my JavaScript is the fact that any change to one word on any part of the screen is propagated to every other identical word on the screen. Highlights, menus, and text colors—everything is dynamically updated as you go.

Every button on screen is tied to a JavaScript function. Most JavaScript functions are tied, via a POST request, to app.py where data can be easily retrieved from the databases and then returned to the client via a JSON object.

For almost every JavaScript function call, several things are taken into consideration. What word is being acted on, the relevant id, what type of request it is (new definition? switch the dictionary? etc), and how far down we are now.

The reason it's important to know how far down we are is because for every word added to the user's flashcard deck, I note in its table row the depth at which it was added; furthermore, if that word appears again at a lower depth, the word's database entry is updated to reflect the lower depth. The reason for this is the crux of this app's pedagogical process. In order to understand the words higher up the page, you first need to understand all of the words beneath it. So, by noting the depth, and studying the cards with the greatest depth first, we ensure that you can make your way towards understanding the initial word/phrase you entered into the Dictionary Diver more quickly.

That said, currently the flashcard learning algorithm is fairly simple and needs additional work to be as powerful as I'd like it to be.

## Future Improvements & Things I'd Change

- Make this application language-agnostic:
    1)  Reformat the dictionary contents so that every dictionary table has the exact same structure. This way it only needs to be "cleaned up" once, when I first add the language's dictionary to the SQL database. It also means any dictionary could, theoretically, be used.
    2) Once a dictionary structure is decided on, and the dictionaries are rebuilt, I could collapse the get_jj() and get_ej() functions into one get_def() function that could be used with any language.
    3) Break up the def_builder() function into 3 functions, based on if the text is the user's known language, target language, or if the text to be returned is empty. This way it wouldn't matter if you're learning Japanese or Chinese or Russian, and it wouldn't matter if you speak English or Spanish or German.
        - NB: I acknowledge that it likely wouldn't be this simple for *all* languages, as some have uncommon orthographic  features, but I think as a general rule this would make the program more easy to adapt to different languages.

- Improve the flashcard algorithm
    - prioritize English definition words first, and ordered by depth
    - then prioritize high-depth Japanese (target langauage) words
    - when cycling words marked "Wrong", don't send to the back, but place behind the last in their cohort
        - e.g. English words at depth 7, would all get studied until "Correct" first, then all English words at depth 6, etc etc, *then* Japanese words at their highest depth, and so on.
    - Provide 4 total answer buttons, similar to Anki—again, hard, okay, easy—each one having a different impact on card interval
        - e.g. "Hard" would be equivalent to "Wrong"; "Hard" might increment Level by 1, "Okay" by 2, and "Easy" by, 3

- I need to do a complete overhaul on how words are highlighted. When I first wrote the highlighting function, I didn't have the full structure of the program in mind. I ended up having to write exception after exception, tying things together by threads—and it still doesn't function exactly how I want it to. That said, I think the solution should be fairly easy, now that I know what the shape of the full program looks like.

- Again, now that I have a more complete understanding of how this program is structured, I need to redo some of the html templating. As it currently stands I need to do a lot of weird, complicated, hard-to-read query selections in order to make the code work. I think I could fix this with a few more classes and/or data attributes.

- I need to make the program much more secure by sanitizing inputs, restricting files, etc.

- I need to restructure app.py to do more testing for, and catching of, potential errors
