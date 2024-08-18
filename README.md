# anilist

## AniList Python Client

This is a Python client library for interacting with the AniList GraphQL API. It allows you to search for anime, manga, and user information, as well as retrieve a user's manga collection and update their reading progress.

**Features:**

- Search for anime and manga by title or ID
- Retrieve detailed information about anime and manga entries
- Search for users by username
- Get a user's manga collection, including their reading status and progress
- Update a user's reading progress for a specific manga (**requires authorization**)

**Installation:**

```bash
pip install git+https://github.com/Agsayan/anilist.git
```

**Usage:**

1. **Import the library:**

```python
from anilist import AniList
```

2. **Create an AniList object:**

- You can optionally provide an authorization token for modifying your user data.

```python
# Without authorization (read-only)
client = AniList()

# With authorization (read-write)
client = AniList(authorization="YOUR_ANILIST_TOKEN")
```

3. **Search for anime and manga:**

```python
# Search by title
anime = client.search_anime(search_query="Your Name")
manga = client.search_manga(search_query="Attack on Titan")

# Search by ID
anime = client.search_anime(media_id=13211)
manga = client.search_manga(media_id=4231)
```

4. **Search for a user:**

```python
user = client.search_user(user_name="Arifureta")
```

5. **Get a user's manga collection:**

```python
collection = client.get_user_manga_collection(user_name="Arifureta")
```

6. **Update a user's reading progress (requires authorization):**

```python
# Update progress and reading status
success = client.update_progress(media_id=4231, progress=10, reading_status=ReadingStatus.CURRENTLY_READING)

# Update progress only
success = client.update_progress(media_id=4231, progress=15)
```

**Important Notes:**

- This library uses the AniList GraphQL API. Refer to the official AniList API documentation for details on available queries and mutations: [https://anilist.gitbook.io/anilist-apiv2-docs](https://anilist.gitbook.io/anilist-apiv2-docs)
- Updating a user's reading progress requires a valid AniList authorization token.
- This is a basic client library and may not handle all edge cases. Error handling and advanced features can be implemented based on your needs.

This Read Me provides a clear overview of the library's functionalities, installation instructions, and usage examples. It also includes important notes for users.
