# Real-time Image Processing Flask App
Real-Time Image Processing with Flask and Docker (*Mobile Friendly*)

[**live demo!**](https://bugramurat.pythonanywhere.com)

## Preview
![preview](https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExZHVkdXBnYzFnMDJiZzJ6MWdtcGlqeDB3aWlsdjZlYXB2eWFpaGVtZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QL61nwJd8HPtS3bDg8/giphy-downsized-large.gif)

## How to run
Run this in your *project-folder/docker* path:
```
docker build -t container_name .
```
Then this:
```
docker run --rm -p 5002:5002 container_name
```

## Libraries
- flask==3.0.1
- gunicorn==21.2.0
- pillow
- opencv-python
- numpy

![example](https://i.ibb.co/Lgt74Gk/processed-original-image.jpg)
