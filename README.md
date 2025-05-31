# Dictionary Diver

[Video demonstration on YouTube](https://youtu.be/6hF62qzZroE)

## Installation

Please refer to the `requirements.txt` file to install all the necessary dependencies, or see below:

- cs50
- Flask
- Flask-Session
- pytz
- requests
- janome

Running `pip install <requirement>` for each of the above, if not already installed on your machine, will give you everything you need to get started.

## Launching

While in the dict_diver folder, enter `flask --app app.py run` in the terminal and follow the onscreen instructions to open the app in your browser.

## Usage

### Logging in

If this is your first time using the app, you will be prompted to log in. If you do not yet have an account, please click Register in the top-right corner of the window and register an account.

### Logging out

To log out, press Log Out in the top-right corner of the window.


### Dictionary Diver

#### *For testing purposes, you can use these text samples to get an overview of the app behavior*

> 日本酒

> ヨーロッパ

> 原始時代

> 通常、古代の末期に位置付けられるが、中世の萌芽期と位置づけることも可能であり、古代から中世への過渡期と理解されている。

The Dictionary Diver has two starting modes, Analyze and Define.

- Analyze

    - Use this for entering sentences or other large pieces of text. The text will be parsed and then shown, with each word identified by color and clickable for further use. Please be patient as this may take some time.

- Define

    - Use this for looking up the definitions of single words from the text box. By default this will always search for the Japanese definition. You can switch this once the definition has loaded.

Once you've clicked either of those, the diving can begin! On screen you will now see a bunch of text. If this is your first time using the app, or you haven't saved any words yet, all the words will be the same color. As you use the app, that will change.

- Purple word = Unknown
- White word = Known
- Green word = In flash cards

As you move your mouse over the words, you may notice that not only will unknown words under your mouse be highlighted, but so will other identical words on the screen. As you dive deeper, this behavior will stretch across the whole screen.

Each word can be clicked. When you do, a menu will appear. For all words, you will have the option to look up the word in either Japanese or English. You will also have the option to mark the word known or unknown, depending on the current status of the word. If you change the status of the word, that word will be updated for all identical words on the screen.

When you click Japanese Lookup, after a moment, the word, pronunciation, and definition will populate below. This definition behaves the same way as the text above. It is all clickable in the same way.

If you click English Lookup, the definition is not clickable, and you have reached the end of your dive.

Beneath every definition, there are additional buttons on screen.

- Add to flash cards
- Switch dictionary
- Add user definition
- Add user token
- Go back - *Removes the lowest definition from the screen*

If the word was not found in the dictionary, the "Add to flash cards" button will be missing.

All the buttons are automatic, except for "Add user definition" and "Add user token". If you click "Add user definition" the following input fields will appear:

- Definition - You can write this in English or Japanese (or whatever you want, really)
- Reading - This is optional
- Japanese/English - Choose which language you wrote the definition in (if you wrote it in some language other than Japanese or English, select English)

If you click "Add user token" you can input a word that you wish would be parsed as a single unit. Next time text is parsed, it will appear as one unit, available for lookup.

At any point, you can click a word in a definition higher up the page and do a lookup on it. Note, however, that this will remove all definitions currently displayed below it and replace them with the definition just requested.

### Flash Cards

When you select Flash Cards, a study session will be automatically populated for you based on the words you've added to your deck. If you have no currently-scheduled cards a message will let you know.

When studying, you will see the Japanese word on screen. Think to yourself if you know the pronunciation and meaning. Click Reveal to display the pronunciation and meaning. If you were correct, or wrong, click the corresponding button.

Clicking Wrong will move the card to the end of the current study session. Clicking Correct will remove the card from the current study session and schedule it for a later date. After a word is marked Correct 10 times in a row, the word will be marked as known and will no longer be shown in study sessions.

The current scheduling algorithm will show the word at progressively later and later dates. Here's how that works:

- Each word in your deck has a "level" associated with it.
- All words start at 1 and increment with every correct answer, until they reach 10.
- After that they get marked to 0, which is understood by the program as "known".
- If a word is marked Wrong, it is decremented to a minimum of 1.
- The interval until the card is available for study again is:
`1440 * (0.1 * word_level) * word_level`
- 1440 represents the number of minutes in a day
- A "perfect run" of a word will have you studying the word for just over 38 days.

When all cards available for study have been marked Correct, the study session will end.

### Account

#### Change Password

Does what it says on the tin!

If you wish to change your password, once you're logged in, click Account in the top-right corner and follow the instructions.

#### Export Words as CSV

This will export all the words in your flash card deck as a CSV file, easily importable to Anki or other similar services.

#### Import known words

Perhaps you already have a list of words you know. Drop it in here, as a CSV file with each word on a separate line, and all the words will be instantly added to your "known words" list. This is a great feature if you have already studied lots on another platform that allows data handling with CSV's, such as Anki.
