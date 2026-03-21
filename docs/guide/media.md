# Media Uploads

Upload images, files, video, and audio to Boosty, then attach them to posts.

## Upload a File

```python
from pathlib import Path

media = await client.media.upload_file(
    Path("./data.zip"),
    filename="data.zip",
)
print(f"Uploaded: {media.id}, size: {media.size}")
```

## Upload an Image

```python
media = await client.media.upload_image(
    Path("./photo.png"),
    content_type="image/png",
)
```

## Upload Video / Audio

```python
video = await client.media.upload_video(Path("./video.mp4"))
audio = await client.media.upload_audio(Path("./track.mp3"))
```

## Attach to a Post

```python
from boostylib.builders import PostBuilder

post = (
    PostBuilder()
    .title("Download the Archive")
    .text("Here is the source code:")
    .file(media_id=media.id, filename=media.filename)
    .access_level(level_id="premium_level_id")
    .build()
)
await client.posts.create_post("my_blog", post)
```

## Upload from File-Like Objects

```python
with open("data.csv", "rb") as f:
    media = await client.media.upload_file(f, filename="data.csv")
```

## MediaFile Model

| Field | Type | Description |
|---|---|---|
| `id` | `str` | Media identifier |
| `url` | `str` | Direct URL |
| `signed_url` | `str \| None` | Signed URL for authenticated access |
| `filename` | `str \| None` | Original filename |
| `size` | `int \| None` | Size in bytes |
| `content_type` | `str \| None` | MIME type |
| `width` | `int \| None` | Width (images/video) |
| `height` | `int \| None` | Height (images/video) |
| `duration` | `float \| None` | Duration in seconds (audio/video) |
