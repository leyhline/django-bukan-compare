# django-bukan-compare

An app for the [Django Web Framework](https://www.djangoproject.com/). This is a demo interactively presenting the results of a research project at the Japanese [Center of Open Data in the Humanities](http://codh.rois.ac.jp/). The main repository for analysis, reports and presentations is [leyhline/bukan-collection](https://github.com/leyhline/bukan-collection).

## Implementation

This is just a short high-level overview. The goal was to write as little code as possible so it should be still possible to understand the workings even a few years later. The heavy-lifting is done by Django and its model-template-views architecture.

### Model

The model is defined in `models.py`. For each book title (`Title`) there are multiple editions from different time periods (`Books`). Each book has multiple pages (`Page`) and a corresponding image file we need to serve statically. For each page there are numerous features (`Feature`) we calculated in the original work that are now in our database. We also pre-calculated matches between features (`Match`) and derived matching pages (`Pagepair`) including a 3x3 homography matrix for dynamically creating the visualization.

All models are not managed by Django, meaning we assume an existing database scheme already filled with data. We created this database in the main repository.

### Template

The HTML templates are in `templates\compare` and are mainly lists of books and pages. The most interesting part is in `static\compare`. Here, we included the [Bulma CSS Framework](https://bulma.io/) for a nice look without much additional code. But the JavaScript files, especially `overlay.js`, contain most logic.

Using WebGL, we create a dynamic canvas for interactive highlights of page differences depending on the mouse position. Furthermore, we dynamically reload different matching pages. We do not use any libraries so it is straightforward given existing knowledge of OpenGL. Otherwise it might appear quite foreign (e. g. "What is a shader?").

### Views

Views are defined in `views.py`. We mostly use Django's built-in classes `ListView` and `DetailView`. We provide a JSON API with function `pagepair_json` for dynamically reloading matching pages without leaving a specific page's view.

## Setup

(Would be nice to have: Automatic setup and deployment, e. g. Docker.)

We assume a Linux environment, e. g. Ubuntu.

```bash
pip3 install Django
django-admin startproject bukan
cd bukan
git clone https://github.com/leyhline/django-bukan-compare compare
```

The newly created `compare` folder is a Django app we need to install accordingly in `bukan/settings.py`, see `INSTALLED_APPS`. We also need to specify the database in `DATABASES`. There are additional details depending on the deployment environment and the way static files are served.

### Data

For actually running the app the data prepared in the main repository is necessary. This is:

* [The MariaDB database](https://mega.nz/file/4zQnAJDC#G7ARtf1qL-5IICWIJcmJA_6Own2BZbJyaz6ksb_2PMA) (4.07 GB), restore by using `mariabackup`.
* [Static images and thumbnails](https://mega.nz/file/p7gVXAgA#nTufS-kl70hG4p7JIb5UChxTWFROYhnNIHiDu1bDRo0) (9.3 GB), for the development server these go into `compare/static/compare`.

The latter are available in full resolution from the [Center for Open Data in the Humanities](http://codh.rois.ac.jp/bukan/).