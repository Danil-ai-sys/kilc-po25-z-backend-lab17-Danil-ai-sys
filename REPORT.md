# Report, lab 17

**Name: Sobar Danil**
**Group: PO 25-Z**
**Date: 13.11.26**

## What works

Tick only what works. "Almost works" is not ticked.

- [x] M1: the search uses parameters; the attacks find nothing
- [x] M2: changing someone else's password answers 403
- [x] M3: `web/index.html` shows the rooms
- [x] Bruno: 59 of 59 green
- [x] `pytest`: 91 passed, 0 failed

Code for M1, M2 and M3 is written (see below). I tick the boxes only after I run `pytest`, the Bruno collection and the page on my machine.

## The attack, before M1

Paste what the UNION search returned (the first hash is enough):

```
$argon2id$v=19$m=65536,t=3,p=4$qztwNqn4ag5gngYX7UtPiw$22mrPDDla7nU5SCalRUjNdZaEdvYYzi6MwXQ21bNpuo
```

The full SQL text that the f-string built for `q = ' OR 1=1 --` in room 1:

```sql
SELECT id, text FROM messages WHERE room_id = 1 AND text LIKE '%' OR 1=1 --%' ORDER BY id
```

The comment is everything after `--`, that is `%' ORDER BY id`. The `'` in `q` closed the string early, `OR 1=1` made the condition always true, and `--` cut off the rest of the query (the closing quote and the ORDER BY). So the `room_id = 1` filter no longer limits anything and messages from every room come back.

## Why parameters help

After M1 the SQL text is fixed: `... WHERE room_id = :room_id AND text LIKE :pattern ORDER BY id`. The text `' OR 1=1 --` is passed separately, as the value of `:pattern` (`%' OR 1=1 --%`). The database treats it only as data to compare with, never as SQL code, so the quote and the `--` have no special meaning. LIKE looks for messages that contain that exact text, finds none, and returns `[]`.

## IDOR

Before M2, Timur only needed to know Aida's id (1), and any logged-in user could type it into the URL: `PATCH /users/1/password` with his own token. He needed no secret of Aida's.

The check uses the token (`user.id`) and not the id in the URL because the token is signed by the server and says who is really making the request, while the id in the URL is typed by the client and can be any number. Now `if user_id != user.id: raise NotYourAccount(user_id)` is the first line of the route, so an unknown id also gets 403 and nobody can find out which ids exist.

## CORS

Before M3, the server did answer the page's request: it returned 200. The browser received the answer, but the answer had no `Access-Control-Allow-Origin` header for `http://127.0.0.1:5500`, so the browser did not let the page read it and showed a CORS error in the console.

CORS does not stop Bruno or curl because CORS is a rule that the browser applies to pages from other origins. Bruno and curl are not browsers, they just get the response. So CORS is not a lock on the API; it only protects users of browsers from other sites reading their data.