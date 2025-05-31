import os

from cs50 import SQL
import csv
# import sqlite3
import shutil
from flask import Flask, flash, redirect, render_template, request, session, send_from_directory
from flask_session import Session
import nh3
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
# from flask_talisman import Talisman

from helpers import apology, login_required, text_parser, def_cleaner, def_builder, eng_card_def_builder, build_study_deck

# Configure application
app = Flask(__name__)
# Talisman(app)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///dict.db")

# Global vars to manage dictionary state
depth = 0
searched = []
cards_added = []
deck = []


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    try:
        os.remove(f'export/words{session.get("user_id")}.csv')
        file_handle.close()
    except:
        return response
    # except Exception as error:
        # app.logger.error("Error removing or closing downloaded file handle", error)
    return response


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure confirmation submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password", 400)

        # Ensure password & confirmation match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords must match", 400)

        try:
            # Store the user
            db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", request.form.get(
                "username"), generate_password_hash(request.form.get("password")))

            # Add default "known words"
            user_id = db.execute("SELECT id FROM users WHERE username=?",
                                 request.form.get("username"))[0]['id']
            for char in '㋽㋝《＆㊃㋤㋔㋹〞》―「〒♪１⑨〵③〥〭８〫〼\'㈨＞〤＄＝〜㋟㋫0〯㋚㊇〆㊅－〘{④\\㋕〡（#〛⑲,㋠㈤6&㈩(⑫㋼㋪⑪?)㋵4㊁㊉㋷』〷＋２・７㋙〃〖〺）+＠㈢〟㋓’⟨②『㈠"🈪㋳５６〻＜㊂㋧㋭㋰〳％〣%㋻$［[〕]⑭〨㋣/㋗㈣；＾3〔〝㋩”＊３㋛？㋞㋾㋡…｀〴＿🈔〱〪㋥㋮〶〗㈦！>９<‥〓＃〦〸.㋦⟩~］⑤!㋨㊈㋶㋢」〬*～々㊄^〚〹}-㊀〄〽。〮:㋜〈9〰〧㋺４〉㊆=8🈩⑰，゠㋑：⑧｜㋖⑥7@〙⑱㋬〇1_㋴〢㋱㋐⑩㋒￥【;０⑬`㋯⑮㈧｝〲⑦5㋲⑳2|｛⑯㈥、〩㋘】〠㋸㈡①':
                db.execute(
                    "INSERT INTO user_words (user_id, word, status, not_word) VALUES (?, ?, 0, 1)", user_id, char)

            return render_template("login.html")
        except:
            return apology("username already exists", 400)

    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    if request.method == "POST":
        # Ensure all fields filled out
        if not request.form.get("old_password") or not request.form.get("new_password") or not request.form.get("confirm_password"):
            return apology("please fill out all fields", 400)

        # Ensure new_password properly confirmed
        elif request.form.get("new_password") != request.form.get("confirm_password"):
            return apology("new passwords must match", 400)

        # Ensure old_password is correct
        if not check_password_hash(db.execute("SELECT hash FROM users WHERE id=?",
                                              session.get("user_id"))[0]['hash'], request.form.get("old_password")):
            return apology("incorrect password entered", 400)

        db.execute("UPDATE users SET hash=? WHERE id=?", generate_password_hash(
            request.form.get("new_password")), session.get("user_id"))
        return render_template("/account.html", pw="pw")

    else:
        return render_template("/account.html")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        global depth
        global searched
        depth = 0
        searched.clear()
        cards_added.clear()
        user_id = session.get("user_id")
        tokenized_text = text_parser(request.json.get("text-in"), user_id)
        analyzed_text = ''.join(def_builder(0, '', tokenized_text, "txt", 0, user_id))
        return {"analyzed_text": analyzed_text}
    else:
        return render_template("index.html")


@app.route("/swap_word", methods=["POST"])
@login_required
def swap_word():
    user = session.get('user_id')
    word = request.json.get("word")
    type = request.json.get("type")
    if type == "known" or type == "in-deck-to-unknown":
        db.execute("DELETE FROM user_words WHERE user_id=? AND word=?", user, word)
    elif type == "in-deck-to-known":
        db.execute(
            "UPDATE user_words SET status=?, due='', level='', WHERE user_id=? AND word=?", 0, user, word)
    else:
        if len(db.execute("SELECT user_id, word FROM user_words WHERE user_id=? AND word=?", user, word)) == 0:
            db.execute(f"INSERT INTO user_words (user_id, word, status, not_word) VALUES (?, ?, 0, 0)", user, word)
    return {"word": word}


@app.route("/get_jj", methods=["POST"])
@login_required
def get_jj():
    global depth
    global searched
    global cards_added
    if request.json.get("req_type") == 'define':
        depth = 0
        searched.clear()
        cards_added.clear()

    user_id = session.get("user_id")
    # jj_request = request.json.get("def")
    jj_request = nh3.clean(request.json.get("def"))
    click_depth = int(request.json.get("click_depth"))
    if click_depth < depth:
        depth = click_depth
    depth = depth + request.json.get("dive")
    searched.append([jj_request, depth])

    # Get definition from DB
    jj_def_raw = db.execute("SELECT definition, sound FROM jj WHERE word=?", jj_request)
    user_def = db.execute("SELECT definition, sound FROM user_defs WHERE word LIKE ?", jj_request)

    if len(jj_def_raw) + len(user_def) == 0:
        empty_def = def_builder(jj_request, '', "Word not in JJ dictionary",
                                "jj-empty", depth, user_id)
        return {"def": empty_def, "depth": depth}

    # Clean up definition formatting
    jj_def_clean = ''
    if len(jj_def_raw) != 0:
        jj_def_clean = def_cleaner(jj_def_raw[0]['definition'])
        kana = jj_def_raw[0]['sound']

    if len(user_def) != 0:
        jj_def_clean += f"<br><br>{user_def[0]['definition']}"
        if len(jj_def_raw) == 0:
            kana = user_def[0]['sound']

    # Parse the definition
    jj_def_tokenized = text_parser(jj_def_clean, user_id)

    # Print definition to the screen
    jj_def_analyzed = ''.join(def_builder(jj_request, kana, jj_def_tokenized, "jj", depth, user_id))
    return {"def": jj_def_analyzed, "depth": depth, "searched": searched, "cards_added": cards_added}


@app.route("/get_ej", methods=["POST"])
@login_required
def get_ej():
    global depth
    global searched
    user_id = session.get("user_id")
    ej_request = request.json.get("def")
    click_depth = int(request.json.get("click_depth"))
    if click_depth < depth:
        depth = click_depth
    depth = depth + request.json.get("dive")
    searched.append([ej_request, depth])

    user_id = session.get("user_id")
    ej_request = nh3.clean(request.json.get("def"))
    ej_request_sql = f'%"{ej_request}"%'

    # Get definition from DB
    ej_def_raw = db.execute("SELECT definition, sound FROM ej WHERE kanji LIKE ?", ej_request_sql)
    user_def = db.execute("SELECT definition, sound FROM user_defs WHERE word LIKE ?", ej_request)

    if len(ej_def_raw) + len(user_def) == 0:
        empty_def = def_builder(ej_request, '', "Word not in EJ dictionary",
                                "ej-empty", depth, user_id)
        return {"def": empty_def, "depth": depth}

    else:
        if len(user_def) != 0:
            for definition in user_def:
                ej_def_raw.append(definition)
        ej_def_complete = ''.join(def_builder(ej_request, '', ej_def_raw, "ej", depth, user_id))
        return {"def": ej_def_complete, "depth": depth, "searched": searched, "cards_added": cards_added}


@app.route("/go_back", methods=["POST"])
@login_required
def go_back():
    global depth
    global searched
    depth = depth - 1
    searched.pop()
    return {"depth": depth}


@app.route("/add_card", methods=["POST"])
@login_required
def add_card():
    global cards_added
    user = session.get('user_id')
    word = request.json.get("word")
    depth = request.json.get("depth")
    lang = request.json.get("lang")
    due = datetime.now()
    if len(db.execute("SELECT user_id, word FROM user_words WHERE user_id=? AND word=?", user, word)) == 0:
        db.execute(f"INSERT INTO user_words (user_id, word, status, lang, due, level, not_word) VALUES (?, ?, ?, ?, ?, ?, 0)",
                   user, word, depth, lang, due.isoformat(), 0)
        cards_added.append([word, depth])
    return {"word": word}


@app.route("/update_card", methods=["POST"])
@login_required
def update_card():
    user = session.get('user_id')
    word = request.json.get("word")
    depth = request.json.get("depth")
    db.execute("UPDATE user_words SET status=? WHERE user_id=? AND word=?", depth, user, word)
    return {"word": word}


@app.route("/add_user_def", methods=["POST"])
@login_required
def add_user_def():
    user = session.get('user_id')
    word = request.json.get("word")
    definition = nh3.clean(request.json.get("definition"))
    reading = nh3.clean(request.json.get("reading"))
    lang = request.json.get("user_def_lang")
    db.execute(f"INSERT INTO user_defs (user_id, word, sound, definition, language) VALUES (?, ?, ?, ?, ?)",
               user, word, reading, definition, lang)
    return {"word": word, "definition": definition, "reading": reading, "lang": lang}


@app.route("/cards", methods=["GET", "POST"])
@login_required
def cards():
    global deck
    user = session.get('user_id')
    if request.method == "POST":
        # If revealing answer
        if request.form.get("card-action") == 'reveal' and deck[0]['lang'] == 'ej':
            ej_request = deck[0]['word']
            ej_request_sql = f'%"{ej_request}"%'
            ej_def_raw = db.execute(
                "SELECT definition, sound FROM ej WHERE kanji LIKE ?", ej_request_sql)
            user_def = db.execute(
                "SELECT definition, sound FROM user_defs WHERE word LIKE ?", ej_request)

            if len(ej_def_raw) + len(user_def) == 0:
                return render_template("cards.html", card=deck[0], definition='Something is missing')

            if len(user_def) != 0:
                for definition in user_def:
                    ej_def_raw.append(definition)
            definition = ''.join(eng_card_def_builder(ej_def_raw))

            return render_template("cards.html", card=deck[0], definition=definition, display="back")

        elif request.form.get("card-action") == 'reveal' and deck[0]['lang'] == 'jj':
            jj_request = deck[0]['word']
            jj_def_raw = db.execute("SELECT definition, sound FROM jj WHERE word=?", jj_request)
            user_def = db.execute(
                "SELECT definition, sound FROM user_defs WHERE word LIKE ?", jj_request)

            if len(jj_def_raw) + len(user_def) == 0:
                return render_template("cards.html", card=deck[0], definition='Something is missing')

            # Clean up definition formatting
            jj_def_clean = ''
            if len(jj_def_raw) != 0:
                jj_def_clean = def_cleaner(jj_def_raw[0]['definition'])
                kana = jj_def_raw[0]['sound']

            if len(user_def) != 0:
                jj_def_clean += f"<br><br>{user_def[0]['definition']}"
                if len(jj_def_raw) == 0:
                    kana = user_def[0]['sound']

            # Print definition to the screen
            definition = f"""
                <div id="definition">
                    <br>
                    <h3 class="kana-displayed">{kana}</h3>
                    <div class="card-def">{jj_def_clean}</div>
                    <br><br>
                </div>
                """

            return render_template("cards.html", card=deck[0], definition=definition, display="back")

        # If submitting correct answer
        elif request.form.get("card-action") == 'correct':
            # If level < 10, increment & update due date
            if deck[0]['level'] < 11:
                # Calculate new interval
                interval = 1440 * (0.1 * deck[0]['level']) * deck[0]['level']
                due = deck[0]['due'] + timedelta(minutes=interval)
                db.execute("UPDATE user_words SET level=?, due=? WHERE user_id=? AND word=?",
                           deck[0]['level'] + 1, due.isoformat(), user, deck[0]['word'])

            # Else, mark known: Set status=0, nullify due & level
            else:
                db.execute(
                    "UPDATE user_words SET status=0, due='', level='', WHERE user_id=? AND word=?", user, deck[0]['word'])

            del deck[0]
            # Check if list empty
            if len(deck) == 0:
                # check for new cards to add to deck
                deck = build_study_deck(user)
                # If none, display "no cards to study now"
                if len(deck) == 0:
                    return render_template("cards.html", card='', definition='', display='no-cards')

            return render_template("cards.html", card=deck[0], definition='', display='front')

        # If submitting wrong answer
        else:
            if deck[0]['level'] > 0:
                db.execute("UPDATE user_words SET level=? WHERE user_id=? AND word=?",
                           deck[0]['level'] - 1, user, deck[0]['word'])
            move = deck[0]
            del deck[0]
            deck.append(move)
            return render_template("cards.html", card=deck[0], definition='', display='front')

    else:
        deck = build_study_deck(user)

        if len(deck) == 0:
            return render_template("cards.html", card='', definition='', display='no-cards')

        return render_template("cards.html", card=deck[0], definition='', display='front')


@app.route("/export", methods=["POST"])
@login_required
def export():
    if request.method == "POST":
        user_id = session.get('user_id')
        words = db.execute(
            "SELECT word, status, lang, level, due FROM user_words WHERE user_id=? AND level>0", user_id)

        with open(f'export/words{user_id}.csv', 'w', newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([word for word in words[0]])
            writer.writerows([word.values() for word in words])

        return send_from_directory('', f'export/words{user_id}.csv', as_attachment=True)

    else:
        return render_template("/account.html")


@app.route("/import_file", methods=["POST"])
@login_required
def import_file():
    try:
        user_id = session.get('user_id')
        import_file = request.files['file']
        if import_file != '':
            import_file.save(f'imports/{import_file.filename}')
            with open(f'imports/{import_file.filename}', 'r') as file:
                read_import = csv.reader(file)
                for word in read_import:
                    # MIGHT BE A BUG HERE
                    db.execute("INSERT INTO user_words (user_id, word, status, not_word)SELECT ?, ?, 0, 0 WHERE NOT EXISTS (SELECT user_id, word FROM user_words WHERE user_id=? AND word=?)", user_id, word, user_id, word)
        os.remove(f'imports/{import_file.filename}')
        return render_template("/account.html")
    except:
        return apology("formatting error", 400)


@app.route("/tokens", methods=["POST"])
@login_required
def tokens():
    user_id = session.get('user_id')
    if not os.path.exists(f'user_tokens/tokens{user_id}.csv'):
        shutil.copyfile('default_tokens.csv', f'user_tokens/tokens{user_id}.csv')

    word = nh3.clean(request.json.get("word"))
    pos = 'ユーザー'
    reading = nh3.clean(request.json.get("reading"))
    entry = [word, pos, reading]

    with open(f'user_tokens/tokens{user_id}.csv', 'a') as file:
        writer = csv.writer(file)
        writer.writerow(entry)

    return {"word": word, "reading":reading}


@app.route("/reset_progress", methods=["POST"])
@login_required
def reset_progress():
    user_id = session.get('user_id')
    reset_type = request.json.get("reset_type")
    if reset_type == "known":
        print("reset known")
        db.execute("DELETE FROM user_words WHERE user_id=? AND status=0 AND not_word IS NOT 1", user_id)
        return {"reset":"reset known"}
    elif reset_type == "flash":
        print("reset flash")
        db.execute("DELETE FROM user_words WHERE user_id=? AND status IS NOT 0 AND not_word IS NOT 1", user_id)
        return {"reset":"reset flash"}
    elif reset_type == "all":
        print("reset all")
        db.execute("DELETE FROM user_words WHERE user_id=? AND not_word IS NOT 1", user_id)
        return {"reset":"reset all"}
