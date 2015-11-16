# Client structure and building the code

## Structure

The latest javascript code is located in the `static/js/app` file. The are also other files in the `js` folder but they are only previously used scripts. Code mostly uses [Angular framework](https://angularjs.org/).

The `app` folder's structure is the following:
* `app.js` file contains the Angular module.
* `controllers` folder contains all the controllers. All the search logic is located in the `search_controller.js`.
* `directives` folder contains a few angular directives, like the topic visualization in the `topics_diagram.js` file.
* `utils` folder contains some fancy UI scripts.
* `services` folder contains all services used by controllers. Most important service is the backend API located in the `api.js` file which makes ajax calls to the backend.
* `views` folder contains all the views injected to `templates/index.html` file by Angular's router. Most important view is the `search.html` which contains the search template.
* `app.min.js` is the minified script file produced by running `grunt`.

All the stylesheets are located in the `static/css` folder.

All the templates are located in the `templates` folder.

## Building

1. Install [Node.js](https://nodejs.org/en/).
2. Install Grunt `npm install -g grunt-cli`.
3. Install dependencies by running `npm install`.

* Run `grunt` to minify the script files and watch the files. If the files are changed, the tasks is re-run.
